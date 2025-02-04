# Async Web Crawler Service - Shoppin Assignment Submission - Gunish Matta

This project provides an asynchronous web crawling service to extract product URLs from multiple domains efficiently using `asyncio`, `aiohttp`, `Selenium` and `BeautifulSoup`. It supports dynamic content fetching using Selenium and implements retry logic for robust data extraction.

## Features

* Asynchronous and scalable crawling of multiple domains
* Handles dynamic web pages using Selenium
* Extracts product URLs using configurable patterns
* Supports domain input via command line arguments or JSON/text files
* Next-page navigation strategies for deep crawling
* Error handling and retry logic for failed fetches
* Observer pattern for real-time logging

## Tech Stack

* Python 3.8+
* `asyncio`
* `aiohttp`
* `BeautifulSoup`
* `Selenium`
* `uvloop` for enhanced async I/O performance
* Observer pattern for logging and notifications

## Getting Started

### Installation

```bash
git clone <repository_url>
cd async-web-crawler
pip install -r requirements.txt
```

Additional Setup for Selenium:

Ensure Chrome and ChromeDriver are installed.

```bash
sudo apt install -y chromium-browser
```
Install Selenium Chrome driver:

```bash
pip install selenium
```

Usage
Command Line Arguments

```bash
python crawl_service.py <domains> [--file <file_path>]
```
Examples

Directly Passing Domains:

```bash
python crawl_service.py example.com example.org
```
Using a File:

```bash
python crawl_service.py --file domains.json
```
Example JSON file content:

```json
 ["example.com", "example.org"]
 ```

Configuration
The patterns for extracting product URLs can be customized in the Config.DEFAULT_PRODUCT_PATTERNS.

Example configuration:

```python
DEFAULT_PRODUCT_PATTERNS = [
    r'product',
    r'item',
    r'details',
    r'description'
]
 ```

**Architecture**

**Overview**

Main Module: Entry point to the entire crawling process.

CrawlerService: Manages concurrent crawling tasks.

Fetcher: Abstracts fetching logic for both static and dynamic content.

Observer Pattern: Logs real-time crawling events.

Logging : Logs are enabled at the INFO level and provide crawl status updates.

Error Handling 
* Retries for content fetching with exponential backoff
* Graceful handling of domain and content-related exceptions


Future Improvements
* Persistent storage integration for crawl results
* Use a more sophisticated worker for workloads like Celery
