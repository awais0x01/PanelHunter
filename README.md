# PanelHunter

**Admin Panel Finder Tool**

PanelHunter is a professional and fast admin panel finder written in Python. Designed for security professionals, it helps you identify admin panels and other sensitive endpoints on websites using wordlists.

## Features
- Scan single or multiple domains for admin panels
- Default wordlist included (user can provide a custom wordlist)
- Concurrent scanning with threading control
- Silent mode for minimal output
- Tor support for anonymity
- Real-time results with colored status codes
- Customizable HTTP status code filtering

## Requirements
- Python 3.7+
- `aiohttp` for asynchronous HTTP requests

```
pip install aiohttp
```

## Usage
### Basic Usage
```
python3 panelhunter.py -u example.com
```

### Scan with Custom Wordlist
```
python3 panelhunter.py -u example.com -w custom_wordlist.txt
```

### Scan Multiple Domains from a File
```
python3 panelhunter.py -dL domains.txt
```

### Filter Specific Status Codes
```
python3 panelhunter.py -u example.com -mc 200,403
```

### Silent Mode
```
python3 panelhunter.py -u example.com -s
```

### Using Tor for Anonymity
```
python3 panelhunter.py -u example.com --tor
```

### Custom Threads
```
python3 panelhunter.py -u example.com --threads 50
```

## Contributors
- **awais0x01** (Project Creator & Lead Developer)

## License
MIT License

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss the proposed changes.

---

### Disclaimer
**PanelHunter is intended for educational purposes only.** The author takes no responsibility for misuse. Use responsibly and ensure you have proper authorization before scanning any websites.
