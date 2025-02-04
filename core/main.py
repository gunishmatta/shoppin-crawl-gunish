import logging
import os

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from fastapi import FastAPI, HTTPException
from typing import List
from core.service.crawl_service import CrawlerService
from dramatiq.results.backends import RedisBackend

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
redis_broker = RedisBroker(host=REDIS_HOST, port=6379)
result_backend = RedisBackend(host=REDIS_HOST, port=6379)
redis_broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(redis_broker)


@dramatiq.actor(max_retries=3, store_results=True)
def crawl_task(domains: List[str]):
    """
    Dramatiq actor that performs the crawling task.
    This runs in a separate process managed by Dramatiq workers.
    """
    import asyncio
    async def run_crawler():
        crawler_service = CrawlerService()
        result = await crawler_service.crawl_all_domains(domains)
        logging.info("Crawl completed for domains: %s", domains)
        logging.info("Result: %s", result)
        return result
    result = asyncio.run(run_crawler())
    return result


@app.post("/crawl/")
async def crawl_domains(domains: List[str] = None):
    """
    Endpoint to initiate crawling of domains.
    The actual crawling is performed asynchronously by Dramatiq workers.
    """
    if not domains:
        raise HTTPException(status_code=400, detail="No domains provided.")
    normalized_domains = [
        f"https://{domain}" if not domain.startswith(("http://", "https://"))
        else domain for domain in domains
    ]

    message = crawl_task.send(normalized_domains)

    return {
        "message": "Crawling task enqueued",
        "task_id": message.message_id,
        "domains": normalized_domains
    }


@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    """
    Endpoint to get the result of a task by its ID.
    """
    try:
        message = dramatiq.Message(
            queue_name="default",
            actor_name="crawl_task",
            args=(),
            kwargs={},
            options={},
            message_id=task_id,
        )
        result = result_backend.get_result(message, block=False)
        if result is None:
            return {"status": "pending", "task_id": task_id}
        return {"status": "completed", "task_id": task_id, "result": result}
    except Exception as e:
        return {"status": "error", "task_id": task_id, "error": str(e)}


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to the domain crawler API",
        "endpoints": {
            "/crawl/": "POST - Submit domains for crawling",
            "/task/{task_id}": "GET - Get task result",
        },
        "status": "running"
    }
