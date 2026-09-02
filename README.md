# PyRecon 🔍
> Lightweight, multithreaded reconnaissance and web probing utility designed for penetration testers.

PyRecon automates target validation via IPv4 DNS resolution, performs dual-protocol web probing (HTTP/HTTPS), extracts responsive status codes, captures server header fingerprints, and retrieves HTML page titles.

---

## 📑 Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation Tutorial](#installation-tutorial)
- [Usage Examples](#usage-examples)
- [CLI Reference](#cli-reference)
- [Example Output](#example-output)
- [Disclaimer](#disclaimer)

---

## Features
- **Concurrent Execution:** Multithreaded requests powered by Python's `concurrent.futures`.
- **DNS Verification:** Skips dead hosts by resolving IPv4 addresses prior to web probing.
- **Dual-Protocol Checks:** Automatically verifies endpoints on both HTTP and HTTPS ports.
- **Fingerprinting:** Extracts `Server` HTTP response headers and `<title>` tags.
- **Color-Coded Terminal Feedback:** Clean visual layout for rapid live analysis.
- **File Export:** Writes structured reports to a flat text file for reporting and further automation.

---

## Prerequisites
Ensure you have the following installed on your system (Linux / macOS / WSL):
- Python 3.8+
- pip package manager

Verify your local versions:
$ python3 --version
$ pip3 --version

---

## Installation Tutorial

### 1. Clone the Repository
Clone the project locally to your working machine:
$ git clone https://github.com/mattiabarbieri/pyrecon.git
$ cd pyrecon

### 2. Set Up a Virtual Environment (Optional but Recommended)
Keep your Python dependencies isolated:
$ python3 -m venv venv
$ source venv/bin/activate

### 3. Install Dependencies
Install the required third-party libraries:
$ pip install -r requirements.txt

---

## Usage Examples

### 1. Basic Scan: Single Domain Target
To test a single domain across HTTP and HTTPS protocols:
$ python3 pyrecon.py -d example.com

### 2. Bulk Recon: Target List
To probe an enumerated list of subdomains or target hosts:
$ python3 pyrecon.py -l subdomains.txt

### 3. High-Speed Probing with Thread Adjustment
Increase execution speed by scaling concurrent worker threads (e.g., 20 threads):
$ python3 pyrecon.py -l targets.txt -t 20 --timeout 3

### 4. Full Scan with Export to File
Run enumeration and export all live hosts and fingerprints to a report file:
$ python3 pyrecon.py -l targets.txt -t 15 -o recon_output.txt

---

## CLI Reference

| Parameter | Short | Type | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `--domain` | `-d` | String | Single domain or host target | None |
| `--list` | `-l` | File | Path to target list (one per line) | None |
| `--threads` | `-t` | Integer | Number of concurrent worker threads | `5` |
| `--timeout` | | Integer | HTTP/HTTPS connection timeout (seconds) | `4` |
| `--output` | `-o` | File | Destination file path to save findings | None |
| `--user-agent` | | String | Custom User-Agent header for HTTP probes | `PyRecon/1.0` |

---

## Example Output

### Terminal View
    ╔═════════════════════════════════════════════╗
    ║                PyRecon v1.0                 ║
    ║   Automated Probing & Reconnaissance Tool   ║
    ╚═════════════════════════════════════════════╝

[*] Inizio ricognizione su 3 target con 5 thread...
================================================================================
 [RESOLV] example.com                     -> IP: 93.184.216.34
 [200] https://example.com                 | Srv: ECS (dcb/7f83)  | Title: Example Domain
 [200] http://example.com                  | Srv: ECS (dcb/7f80)  | Title: Example Domain
 [SKIP]   invalid-domain-test.local        -> Impossibile risolvere DNS
================================================================================
[*] Ricognizione completata con successo.
[+] Risultati salvati in: recon_output.txt

---

## Disclaimer
This tool is distributed strictly for authorized security assessments, CTFs, and educational research. Scanning targets without prior mutual written consent violates legal standards. The author assumes no liability for misuse of this utility.
