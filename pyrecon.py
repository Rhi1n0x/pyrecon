#!/usr/bin/env python3
"""
PyRecon - Lightweight Modular Target Reconnaissance & Probing Tool
Author: Mattia Barbieri
Description: Automates DNS resolution, active HTTP/HTTPS probing, and basic header fingerprinting.
"""

import argparse
import concurrent.futures
import os
import socket
import sys
from datetime import datetime
import urllib3
import requests

# Disabilita warning per certificati SSL autofirmati/non validi durante la ricognizione
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Codici colore ANSI per output a terminale
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def print_banner():
    banner = f"""{BLUE}
    ╔═════════════════════════════════════════════╗
    ║                PyRecon v1.0                 ║
    ║   Automated Probing & Reconnaissance Tool   ║
    ╚═════════════════════════════════════════════╝{RESET}"""
    print(banner)


def resolve_domain(target):
    """Risolve l'indirizzo IPv4 per il dominio fornito."""
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return None


def probe_target(target, timeout, user_agent):
    """Esegue probing HTTP/HTTPS estraendo Status Code, Titolo HTML e Web Server."""
    results = []
    protocols = ["https", "http"]
    headers = {"User-Agent": user_agent}

    for proto in protocols:
        url = f"{proto}://{target}"
        try:
            resp = requests.get(
                url,
                headers=headers,
                timeout=timeout,
                verify=False,
                allow_redirects=True,
            )
            # Estrazione rudimentale del tag <title>
            title = "N/A"
            if "<title>" in resp.text.lower():
                try:
                    start = resp.text.lower().index("<title>") + 7
                    end = resp.text.lower().index("</title>", start)
                    title = resp.text[start:end].strip().replace("\n", "")[:50]
                except ValueError:
                    pass

            server_header = resp.headers.get("Server", "Unknown")
            status_colored = (
                f"{GREEN}{resp.status_code}{RESET}"
                if resp.status_code < 400
                else f"{RED}{resp.status_code}{RESET}"
            )

            result_entry = {
                "url": url,
                "status": resp.status_code,
                "status_str": status_colored,
                "server": server_header,
                "title": title,
            }
            results.append(result_entry)
            print(
                f" [{result_entry['status_str']}] {url:<35} | Srv: {server_header:<15} | Title: {title}"
            )

        except requests.exceptions.RequestException:
            continue

    return results


def process_host(target, timeout, user_agent):
    """Orchestra la risoluzione DNS e il controllo web per singolo host."""
    target = target.strip()
    if not target or target.startswith("#"):
        return None

    ip = resolve_domain(target)
    if not ip:
        print(f" [{YELLOW}SKIP{RESET}] {target:<35} -> Impossibile risolvere DNS")
        return None

    print(f" [{GREEN}RESOLV{RESET}] {target:<33} -> IP: {ip}")
    probes = probe_target(target, timeout, user_agent)
    return {"host": target, "ip": ip, "probes": probes}


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="Lightweight HTTP/HTTPS Prober and Recon Automation Tool"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Singolo dominio target (es. example.com)")
    group.add_argument(
        "-l", "--list", help="File contenente lista di target (un dominio per riga)"
    )

    parser.add_argument(
        "-t", "--threads", type=int, default=5, help="Numero di thread concorrenti (default: 5)"
    )
    parser.add_argument(
        "--timeout", type=int, default=4, help="Timeout HTTP in secondi (default: 4)"
    )
    parser.add_argument(
        "-o", "--output", help="File di output in formato TXT per salvare i risultati"
    )
    parser.add_argument(
        "--user-agent",
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) PyRecon/1.0",
        help="Custom User-Agent per le richieste HTTP",
    )

    args = parser.parse_args()

    targets = []
    if args.domain:
        targets.append(args.domain)
    elif args.list:
        if not os.path.exists(args.list):
            print(f"{RED}[-] Errore: File {args.list} non trovato.{RESET}")
            sys.exit(1)
        with open(args.list, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip()]

    print(f"[*] Inizio ricognizione su {len(targets)} target con {args.threads} thread...")
    print("=" * 80)

    recon_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [
            executor.submit(process_host, target, args.timeout, args.user_agent)
            for target in targets
        ]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                recon_data.append(res)

    print("=" * 80)
    print(f"[*] Ricognizione completata con successo alle {datetime.now().strftime('%H:%M:%S')}.")

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as out:
                out.write(f"# PyRecon Scan Report - {datetime.now().isoformat()}\n")
                for item in recon_data:
                    out.write(f"\nTarget: {item['host']} ({item['ip']})\n")
                    for p in item["probes"]:
                        out.write(
                            f"  - [{p['status']}] {p['url']} | Server: {p['server']} | Title: {p['title']}\n"
                        )
            print(f"{GREEN}[+] Risultati salvati in: {args.output}{RESET}")
        except IOError as e:
            print(f"{RED}[-] Errore nel salvataggio del file di output: {e}{RESET}")


if __name__ == "__main__":
    main()
