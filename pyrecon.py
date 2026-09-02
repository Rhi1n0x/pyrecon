#!/usr/bin/env python3
"""
PyRecon v1.1 - Lightweight Modular Target Reconnaissance & Probing Tool
Author: Mattia Barbieri (Aggiornato)
Description: Automates DNS resolution, active HTTP/HTTPS probing, and robust header/title fingerprinting.
"""

import argparse
import concurrent.futures
import os
import socket
import sys
from datetime import datetime
import urllib3
import requests
from bs4 import BeautifulSoup

# Disabilita warning per certificati SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Codici colore ANSI
GREEN, BLUE, YELLOW, RED, RESET = "\033[92m", "\033[94m", "\033[93m", "\033[91m", "\033[0m"

def print_banner():
    banner = f"""{BLUE}
    ╔═════════════════════════════════════════════╗
    ║                PyRecon v1.1                 ║
    ║  Automated Probing & Reconnaissance Tool    ║
    ╚═════════════════════════════════════════════╝{RESET}"""
    print(banner)

def resolve_domain(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None

def probe_target(target, timeout, user_agent):
    results = []
    headers = {"User-Agent": user_agent}

    for proto in ["https", "http"]:
        url = f"{proto}://{target}"
        try:
            # allow_redirects=False per mappare i codici 30X
            resp = requests.get(
                url, headers=headers, timeout=timeout, verify=False, allow_redirects=False
            )
            
            # Estrazione sicura del title tramite BeautifulSoup
            title = "N/A"
            if resp.text:
                soup = BeautifulSoup(resp.text, "html.parser")
                if soup.title and soup.title.string:
                    title = soup.title.string.strip().replace("\n", "")[:50]

            server_header = resp.headers.get("Server", "Unknown")
            location = resp.headers.get("Location", "")
            
            # Colorazione Status Code
            status_color = GREEN if resp.status_code < 300 else (YELLOW if resp.status_code < 400 else RED)
            status_str = f"{status_color}{resp.status_code}{RESET}"
            
            # Formattazione per eventuali reindirizzamenti
            redirect_info = f" -> {location}" if location else ""

            entry = {
                "url": url,
                "status": resp.status_code,
                "server": server_header,
                "title": title,
                "location": location
            }
            results.append(entry)
            
            print(f" [{status_str}] {url:<35} | Srv: {server_header:<15} | Title: {title}{redirect_info}")

        except requests.exceptions.RequestException:
            continue

    return results

def process_host(target, timeout, user_agent):
    target = target.strip()
    if not target or target.startswith("#"):
        return None

    ip = resolve_domain(target)
    if not ip:
        print(f" [{YELLOW}SKIP{RESET}] {target:<35} -> Impossibile risolvere DNS")
        return None

    print(f" [{GREEN}RESOLV{RESET}] {target:<33} -> IP: {ip}")
    return {"host": target, "ip": ip, "probes": probe_target(target, timeout, user_agent)}

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Lightweight HTTP/HTTPS Prober")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Singolo dominio target")
    group.add_argument("-l", "--list", help="File lista target")
    
    parser.add_argument("-t", "--threads", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=4)
    parser.add_argument("-o", "--output", help="File di output TXT")
    parser.add_argument("--user-agent", default="Mozilla/5.0 PyRecon/1.1")
    
    args = parser.parse_args()

    targets = [args.domain] if args.domain else []
    if args.list:
        if not os.path.exists(args.list):
            print(f"{RED}[-] Errore: File {args.list} non trovato.{RESET}")
            sys.exit(1)
        with open(args.list, "r", encoding="utf-8") as f:
            targets = [line.strip() for line in f if line.strip()]

    recon_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [
            executor.submit(process_host, target, args.timeout, args.user_agent)
            for target in targets
        ]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res: recon_data.append(res)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as out:
                out.write(f"# PyRecon Scan Report - {datetime.now().isoformat()}\n")
                for item in recon_data:
                    out.write(f"\nTarget: {item['host']} ({item['ip']})\n")
                    for p in item["probes"]:
                        redir = f" -> {p['location']}" if p['location'] else ""
                        out.write(f"  - [{p['status']}] {p['url']} | Server: {p['server']} | Title: {p['title']}{redir}\n")
            print(f"{GREEN}[+] Risultati salvati in: {args.output}{RESET}")
        except IOError as e:
            print(f"{RED}[-] Errore salvataggio output: {e}{RESET}")

if __name__ == "__main__":
    main()
