import pytest
from unittest.mock import Mock, AsyncMock, patch

from core.config import Config
from core.fetchers import DynamicContentFetcher
from core.service.crawl_service import CrawlerService

@pytest.fixture
def crawler_service():
    with patch('core.service.crawl_service.CrawlerService', new=Mock()):
        with patch('core.service.crawl_service.CrawlerService.domain_semaphores', new={}):
            yield CrawlerService()


@pytest.mark.asyncio
async def test_crawl_domain(crawler_service):
    with patch('core.fetchers.FetcherFactory.get_fetcher', return_value=DynamicContentFetcher()):
        mock_fetcher = Mock()
        mock_fetcher.fetch_content = AsyncMock(return_value="<html><a href='/product1'>Product</a></html>")
        with patch('core.fetchers.dynamic_fetcher.DynamicContentFetcher.fetch_content', new=mock_fetcher.fetch_content):
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = Mock()
                mock_response.__aenter__ = AsyncMock()
                mock_response.__aenter__.return_value.status = 200
                mock_response.__aenter__.return_value.text.return_value = "product description"
                mock_response.__aexit__ = AsyncMock()
                mock_get.return_value = mock_response
                result = await crawler_service.crawl_domain("example.com")
                assert isinstance(result, list)
                assert len(result) == 1



@pytest.mark.asyncio
async def test_extract_product_urls():
    crawler = CrawlerService()

    html_content = """
    <html>
        <body>
            <a href="/itm/123">Item 1</a>
            <a href="/p/product-name">Product Name</a>
            <a href="/image.jpg">Image</a>
        </body>
    </html>
    """

    with patch('core.service.crawl_service.CrawlerService.validate_url', new_callable=AsyncMock) as mock_validate_url:
        mock_validate_url.side_effect = [True, True, False]
        with patch('core.service.crawl_service.Config.DEFAULT_PRODUCT_PATTERNS', new=Config.DEFAULT_PRODUCT_PATTERNS):
            result = await crawler.extract_product_urls("example.com", html_content)
            assert len(result) == 2
            expected_urls = {
                "https://example.com/itm/123",
                "https://example.com/p/product-name"
            }
            assert result == expected_urls


def test_generate_full_url(crawler_service):
    result = crawler_service.generate_full_url("example.com", "/path")
    assert result == "https://example.com/path"