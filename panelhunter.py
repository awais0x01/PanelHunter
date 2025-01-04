  GNU nano 6.2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           adminpanelfinder.py *                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   import argparse
import asyncio
import logging
import random
import time
from typing import List, Optional

import aiohttp
from aiohttp import ClientResponse

# Constants
AGENT_FILE = "agents.txt"
DEFAULT_WORDLIST = "wordlist.txt"
BANNER = """
\033[92m
╔════════════════════════════════════════════╗
║                 PanelHunter                ║
║           Admin Panel Finder Tool          ║
║                 by: awais0x01              ║
╚════════════════════════════════════════════╝
\033[0m
"""

STATUS_COLORS = {
    200: "\033[92m",  # Green for 200 OK
    301: "\033[93m",  # Yellow for 301 Moved Permanently
    302: "\033[94m",  # Blue for 302 Found
    403: "\033[91m",  # Red for 403 Forbidden
    404: "\033[90m",  # Gray for 404 Not Found
}
RESET_COLOR = "\033[0m"

async def fetch(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore, follow_redirects: bool, filter_status: Optional[List[int]]) -> Optional[str]:
    """Fetch the URL using the semaphore and return the URL if valid."""
    try:
        async with semaphore:
            async with session.get(url, timeout=15, allow_redirects=follow_redirects) as response:
                if (filter_status and response.status in filter_status) or (not filter_status and response.status == 200):
                    color = STATUS_COLORS.get(response.status, "\033[95m")  # Default to magenta for unknown status
                    return f"{color}{response.url} [Status: {response.status}]{RESET_COLOR}"
    except aiohttp.ClientResponseError as e:
        logging.warning(e.status)
    except asyncio.TimeoutError:
        logging.warning("Timeout")
    except Exception as e:
        logging.warning(e)
    return None

async def process_domain(domain: str, wordlist: List[str], semaphore: asyncio.Semaphore, follow_redirects: bool, headers: dict, filter_status: Optional[List[int]]):
    """Process a single domain and display results as they are found."""
    print(f"[+] Scanning domain: {domain}")
    urls = [f"{domain}/{path}" for path in wordlist]
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [
            asyncio.create_task(fetch(session, url, semaphore, follow_redirects, filter_status))
            for url in urls
        ]

        for future in asyncio.as_completed(tasks):
            result = await future
            if result:
                print(result)

async def process_domains(domains: List[str], wordlist: List[str], threads: int, follow_redirects: bool, headers: dict, filter_status: Optional[List[int]]):
    """Process multiple domains sequentially and display results domain by domain."""
    semaphore = asyncio.Semaphore(threads)
    start_time = time.time()
    for domain in domains:
        await process_domain(domain, wordlist, semaphore, follow_redirects, headers, filter_status)
    elapsed_time = time.time() - start_time
    print(f"[+] Completed in {elapsed_time:.2f} seconds.")

def load_agents() -> List[str]:
    """Load user agents from the file or use built-in random agents."""
    try:
        with open(AGENT_FILE) as fp:
            return [line.strip() for line in fp if line.strip()]
    except FileNotFoundError:
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Linux; Android 11; Pixel 4 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
        ]  # Built-in random agents

def parse_filter_status(filter_status: Optional[List[str]]) -> Optional[List[int]]:
    """Parse filter status codes, handling comma-separated or space-separated values."""
    if filter_status:
        parsed = []
        for item in filter_status:
            parsed.extend(item.split(","))
        return [int(code) for code in parsed if code.isdigit()]
    return None

def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for the tool."""
    parser = argparse.ArgumentParser(prog="panelhunter.py", description="Admin panel finder by awais0x01")
    parser.add_argument("-u", "--url", help="Target URL/website")
    parser.add_argument("-dL", "--domains", help="File containing list of domains")
    parser.add_argument("-w", "--wordlist", help="Wordlist to use", default=DEFAULT_WORDLIST)
    parser.add_argument("--threads", help="Number of threads to use", type=int, default=100)
    parser.add_argument("-r", "--redirects", help="Follow redirects", action="store_true")
    parser.add_argument("-s", "--silent", help="Silent mode (no output)", action="store_true")
    parser.add_argument("-mc", "--filter-status", help="Show results only with specific status codes (e.g., -mc 200,403)", type=str, nargs='+')
    parser.add_argument("--tor", help="Use Tor for anonymity (requires Tor proxy setup at localhost:9050)", action="store_true")
    parser.add_argument("--examples", help="Show usage examples", action="store_true")
    return parser

def show_examples():
    """Show usage examples."""
    examples = """
Examples:
    python3 panelhunter.py -u example.com
    python3 panelhunter.py -u example.com -w custom_wordlist.txt
    python3 panelhunter.py -dL domains.txt -mc 200,403 --threads 50
    python3 panelhunter.py -u example.com -r
    python3 panelhunter.py -u example.com --tor
    """
    print(examples)

def banner():
    """Display the banner."""
    print(BANNER)

def ensure_https(url: str) -> str:
    """Ensure the URL starts with https://."""
    if not url.startswith("http://") and not url.startswith("https://"):
        return f"https://{url}"
    return url

def read_wordlist(wordlist: str) -> List[str]:
    """Read and return the wordlist as a list of paths."""
    try:
        with open(wordlist) as fp:
            return [line.strip() for line in fp if line.strip()]
    except FileNotFoundError:
        print(f"[!] Wordlist file {wordlist} not found.")
        exit(1)

def handle_interrupt():
    """Handle keyboard interrupt gracefully."""
    print("\n[~] Terminating... Goodbye!")
    exit(0)

def setup_tor() -> dict:
    """Set up headers for Tor anonymity."""
    return {"proxy": "socks5://127.0.0.1:9050"}

def main() -> None:
    try:
        banner()
        parser = build_parser()
        args = parser.parse_args()

        if args.examples:
            show_examples()
            return

        if not args.url and not args.domains:
            parser.print_help()
            print("[-] Either -u or -dL flag is required.")
            exit(1)

        domains = []
        if args.url:
            domains.append(ensure_https(args.url))
        if args.domains:
            try:
                with open(args.domains) as fp:
                    domains.extend([ensure_https(line.strip()) for line in fp if line.strip()])
            except FileNotFoundError:
                print(f"[!] Domains file {args.domains} not found.")
                exit(1)

        wordlist = read_wordlist(args.wordlist)
        filter_status = parse_filter_status(args.filter_status)

        headers = {"User-Agent": random.choice(load_agents())}
        if args.tor:
            print("[+] Using Tor for anonymity...")
            headers.update(setup_tor())

        loop = asyncio.get_event_loop()
        loop.run_until_complete(process_domains(domains, wordlist, args.threads, args.redirects, headers, filter_status))

    except KeyboardInterrupt:
        handle_interrupt()

if __name__ == '__main__':
    main()
