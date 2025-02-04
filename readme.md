# Async Web Crawler Service - Shoppin Assignment Submission - Gunish Matta

This project provides an asynchronous web crawling service to extract product URLs from multiple domains efficiently using `asyncio`, `aiohttp`, `Selenium` and `BeautifulSoup`. It supports dynamic content fetching using Selenium and implements retry logic for robust data extraction.

## Features

* Asynchronous and scalable crawling of multiple domains
* Handles dynamic web pages using Selenium
* Extracts product URLs using configurable patterns
* Next-page navigation strategies for deep crawling
* Error handling and retry logic for failed fetches
* Observer pattern for real-time logging
* Served Via Rest APIs (FastAPI)

## Tech Stack

* Python 3.8+
* `asyncio` - Async IO stuff
* `aiohttp` - async HTTP Requests
* `BeautifulSoup` - Parse HTML content
* `Selenium` - Browser Automation (Chrome)
* `Redis` as a Message Broker and Result Backend for Dramatiq
* `Dramatiq` - Workers
* `FastAPI` - Serving APIs
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

To run this project locally, you have two options: Docker-based or a local setup.

Docker-based (Linux, Windows, Non-Apple Silicon as we are using a docker image which includes chrome by default but not works on Silicon macs as of now).

This method uses Docker and Docker Compose, ensuring a consistent environment. Make sure you have both Docker and Docker Compose installed.

Navigate to the project's root directory in your terminal.
Run the following command:
```bash
docker-compose up -d --build
```
This command will build the Docker image (if necessary) and start the containers in detached mode (running in the background).

Local Setup (Non-Docker) (Works for Silicon Macs for now) 
This method requires you to install and manage the dependencies yourself.
```bash
pip install -r requirements.txt. 
```
Install Redis: Use your preferred method to install Redis. For macOS, you can use Homebrew:
```bash
brew install redis
```
Run Redis: Start the Redis server.

```bash
sudo brew services start redis
```

Run the Worker: In a terminal, execute the following command to start the Dramatiq worker:
```bash 
dramatiq core.main
```
Run the Main App: Open a separate terminal and run the main application using Uvicorn:
```bash
uvicorn core.main:app --reload --port 8000
```
The --reload flag will automatically restart the server when you make code changes, and --port 8088 specifies the port to use.

Access the API Documentation: Open your web browser and go to http://localhost:8000/docs to access the Swagger UI and interact with the API.

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

Main Module: Entry point to the entire crawling process + REST APIs.

CrawlerService: Manages concurrent crawling tasks.

Fetcher: Abstracts fetching logic for both static and dynamic content.

Observer Pattern: Logs real-time crawling events.

Logging : Logs are enabled at the INFO level and provide crawl status updates.

Error Handling 
* Retries for content fetching with exponential backoff
* Graceful handling of domain and content-related exceptions


Future Improvements
* Use docker base image which includes chrome and works on Silicon Macs too


## Extracting Product URLs

The core functionality of the web crawler is to find and extract product URLs from web pages. Here's how it works:

### 1. **Crawling All Domains**
   The crawler service initiates the crawling process for multiple domains concurrently. For each domain, a separate task is created, and the crawler tries to extract all the product URLs from each domain's pages.

   - The `crawl_all_domains` method manages this process using `asyncio.gather`, where each domain is handled asynchronously.
   - If any domain fails to be crawled, an exception is logged and the rest of the crawling continues.

### 2. **Crawling a Single Domain**
   The `crawl_domain` method is responsible for crawling a single domain. It uses the `FetcherFactory` to choose the appropriate fetcher for static or dynamic content.

   - It starts by fetching the homepage or entry point URL for the domain.
   - From the homepage, it recursively crawls subsequent pages based on links found.

### 3. **Handling Dynamic and Static Content**
   - **Static Content:** For static content, URLs are extracted directly from the page's HTML using `BeautifulSoup`.
   - **Dynamic Content:** For dynamic content, the `Selenium` fetcher is used to execute JavaScript and load content that may not be immediately available in the raw HTML.

### 4. **Product URL Extraction**
   The `extract_product_urls` method is responsible for parsing the content of a page to find product URLs.

   - **Pattern Matching:** The URLs are filtered based on predefined patterns (e.g., `r'product'`, `r'item'`, etc.) stored in `Config.DEFAULT_PRODUCT_PATTERNS`.
   - **URL Validation:** Each extracted URL is validated by making a request to ensure it's accessible and that the content matches the expected pattern for product pages. This is done by checking for keywords like `product`, `item`, `details`, etc., in the page content.

   If the URL pattern is not recognized or fails validation, the crawler tries to handle it as a potential new pattern, and additional URLs are checked.

### 5. **Next-Page Navigation**
   The crawler can handle pagination by identifying and following links to subsequent pages. This is done through multiple strategies to locate the "next page" link:

   - **SEO Hint:** Some websites include next-page hints in their meta tags.
   - **Button Class:** Some sites use buttons or links with specific CSS classes (e.g., "next", "pagination").
   - **Text or Aria Labels:** Some sites use specific text labels like "Next" or "Previous".
   - **Sibling Navigation:** Next-page links may be located as adjacent siblings to the current page's navigation element.
   - **Query Parameters:** The next page can sometimes be identified through URL query parameters (e.g., `page=2`).

   These strategies are applied in sequence, and the first valid next-page URL found is used.

### 6. **URL Generation**
   The `generate_full_url` method ensures that relative URLs are transformed into absolute URLs by combining them with the base domain. It cleans the base URL (removing path and query parameters) and appends the relative URL to create a full URL.

   ```python
   full_url = urljoin(clean_base_url, relative_url.lstrip('/'))
   ```

### 7. Error Handling and Retries
The crawler implements retry logic to handle transient errors (e.g., network issues, timeouts) and to ensure that failed fetches are retried with an exponential backoff.

- The `@retry` decorator is used for methods like `crawl_page` and `validate_url` to automatically retry fetching content or validating URLs up to three times with a delay of 2 seconds between retries.
- Failed fetches are logged, and the crawling process continues with other pages.

### 8. Logging and Monitoring
The Observer pattern is used for logging real-time updates on the crawling process. As the crawler progresses, logs are generated for each domain, page, and URL found.
- Logs are output at the INFO level, providing updates such as the number of URLs found or the detection of new URL patterns.

### 9. Handling New URL Patterns
If the crawler encounters URLs that do not match any of the predefined patterns, it attempts to validate them using `validate_url`. If the URL is valid and points to a product page, it is added to the list of product URLs. This mechanism allows the crawler to adapt to new or unknown URL structures.

### Example Configuration for URL Patterns
The URL extraction process is driven by configurable patterns defined in `Config.DEFAULT_PRODUCT_PATTERNS`. These patterns help the crawler identify links that are likely to point to product pages.
