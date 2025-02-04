import asyncio
from core.service.crawl_service import CrawlerService

DOMAINS = [
    "www.ebay.com/sch/i.html?_nkw=machine&_sacat=0&_from=R40&_trksid=p4432023.m570.l1313",
    "www.flipkart.com/search?q=washing+machine&as=on&as-show=on",
    "www.shoppersstop.com/beauty-skincare-cleanser-toners/c-B102020",
    "www.meesho.com/search?q=bags&searchType=manual",
    "www.ajio.com/s/bakeware-4720-51871"
]


async def main():
    crawler_service = CrawlerService()
    await crawler_service.crawl_all_domains(DOMAINS)


if __name__ == "__main__":
    asyncio.run(main())
