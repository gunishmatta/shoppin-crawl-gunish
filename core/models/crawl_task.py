class CrawlTask:
    def __init__(self, url: str, fetcher):
        self.url = url
        self.fetcher = fetcher

    async def execute(self):
        content = await self.fetcher.fetch_content(self.url)
        return content
