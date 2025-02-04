import asyncio

from core.service.crawl_service import CrawlerService
from core.worker import redis_broker
from taskiq import gather as taskiq_gather


crawler_service = CrawlerService()


async def crawl_domain_task(domain: str):
    await crawler_service.crawl_domain(domain)


async def crawl_all_domains(domains):
    """
    Crawl all domains concurrently using TaskIQ for distributed task processing.
    """
    crawler_service.subject.notify("Starting crawl process...")
    try:
        tasks = [
            await crawl_domain_task.kiq(domain)
            for domain in domains
        ]
        results = await taskiq_gather(*tasks, periodicity=5)
        successful_results = {}
        for domain, result in zip(crawler_service.domains, results):
            if isinstance(result, Exception):
                crawler_service.subject.notify(f"Error crawling {domain}: {str(result)}")
            else:
                successful_results[domain] = result
        crawler_service.results.update(successful_results)
        crawler_service.subject.notify(f"Crawl process completed. Successfully crawled {len(successful_results)} domains.")
        return crawler_service.results
    except Exception as e:
        crawler_service.subject.notify(f"Unexpected error during crawl process: {str(e)}")
        raise
