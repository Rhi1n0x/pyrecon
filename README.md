# PyRecon 🔍

A fast, multithreaded Python reconnaissance utility built for Penetration Testers to automate DNS resolution, active HTTP/HTTPS probing, and web application fingerprinting.

## Features
- **Concurrent Probing:** Multithreaded execution using `concurrent.futures`.
- **DNS Resolution Check:** Validates live targets before probing web ports.
- **Protocol Discovery:** Probes both HTTP and HTTPS services automatically.
- **Fingerprinting:** Identifies HTTP status codes, web server headers, and HTML page titles.
- **Clean CLI Output:** Formatted terminal feedback with optional structured report output.

## Installation
```bash
git clone [https://github.com/](https://github.com/)<TUO-USERNAME>/pyrecon.git
cd pyrecon
pip install -r requirements.txt
