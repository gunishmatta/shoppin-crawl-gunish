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