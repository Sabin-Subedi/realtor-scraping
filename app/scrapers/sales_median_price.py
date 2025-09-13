import asyncio
from playwright.async_api import async_playwright, Page
from loguru import logger
from playwright_stealth import Stealth
from httpx import AsyncClient, HTTPError
from fastapi import HTTPException
import random
import json
from datetime import datetime
from app.utils import parse_currency
from app.schemas import MedianScrapeOutput
from app.config import settings


class SalesMedianPriceScraper:
    base_housing_market_url = "https://www.redfin.com/{location_url}/housing-market"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # noqa: E501
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # noqa: E501
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",  # noqa: E501
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",  # noqa: E501
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",  # noqa: E501
    ]

    def _get_random_user_agent(self):
        """Return a random user agent from the list"""
        return random.choice(self.user_agents)

    def _parse_response(self, response: str):
        if response.startswith("{}&&"):
            return json.loads(response.split("&&", 1)[1])
        return json.loads(response)

    async def _get_scraping_url(self, city: str, state: str, retry_count: int = 0):
        async with AsyncClient(proxy=settings.WEBSHARE_ROTATING_PROXY_URL) as client:
            try:
                response = await client.get(
                    f"https://www.redfin.com/stingray/do/location-autocomplete?location={city},{state}&v=2",  # noqa: E501
                    headers={
                        "User-Agent": self._get_random_user_agent(),
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                    },
                )
                response.raise_for_status()
                response_json = self._parse_response(response.text)
                response_url = response_json["payload"]["exactMatch"]["url"]
                return self.base_housing_market_url.format(
                    location_url=response_url.lstrip("/")
                )
            except HTTPError as e:
                logger.error(f"Error getting scraping url: {e}")
                if e.response.status_code == 429:
                    if retry_count > 3:
                        raise HTTPException(
                            status_code=429,
                            detail="Too many requests. Please try again later.",
                        )
                    await asyncio.sleep(2**retry_count)
                    return await self._get_scraping_url(city, state, retry_count + 1)
                return None
            except Exception as e:
                logger.error(f"Error getting scraping url: {e}")
                return None

    async def _get_row_data(self, page: Page) -> MedianScrapeOutput:
        row = page.locator("#home_prices .locationEntries .locationEntry").first
        splited_text = (await row.inner_text()).strip().split("\n")
        date_str = await page.locator(
            "#home_prices .locationHeader .locationSubheader"
        ).first.inner_text()

        return MedianScrapeOutput(
            date=datetime.strptime(date_str, "%b %Y"),
            regionName=splited_text[0] if len(splited_text) > 0 else "",
            value=parse_currency(splited_text[1]) if len(splited_text) > 1 else None,
        )

    async def _scrape_chart(
        self, scraping_url: str, retry_count: int = 0, default_timeout: int = 30_000
    ) -> list[MedianScrapeOutput]:
        try:
            logger.info(f"Scraping chart with url: {scraping_url}")
            async with Stealth().use_async(async_playwright()) as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--disable-extensions",
                        "--no-first-run",
                        "--disable-default-apps",
                        "--disable-features=VizDisplayCompositor",
                    ],
                )
                context = await browser.new_context(
                    user_agent=self._get_random_user_agent(),
                    timezone_id="America/New_York",
                    locale="en-US",
                    # Some common headers to avoid being blocked
                    extra_http_headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                    },
                )
                page = await context.new_page()
                await page.goto(scraping_url, wait_until="domcontentloaded")
                await page.evaluate("window.scrollTo(0, 500);")
                await page.locator(
                    "#home_prices .lineGraph .VictoryContainer"
                ).wait_for(state="visible", timeout=default_timeout)
                await page.locator("#home_prices .locationEntries").wait_for(
                    state="visible",
                    timeout=default_timeout,
                )
                svg = page.locator(
                    "#home_prices .lineGraph .VictoryContainer svg"
                ).first

                out = []
                visible_dates = set()

                box = await svg.bounding_box()
                y = box["y"] + box["height"] * 0.5

                if not box:
                    raise RuntimeError("Could not get chart bounding box")

                for x in range(int(box["x"]), int(box["x"] + box["width"]), 2):
                    await page.mouse.move(x, y)
                    await page.wait_for_timeout(10)
                    row_data = await self._get_row_data(page)
                    if row_data.date in visible_dates:
                        continue
                    visible_dates.add(row_data.date)
                    out.append(row_data)
                await page.close()
                await context.close()
                await browser.close()
                return out
        except TimeoutError as e:
            logger.error(f"TimeoutError: {e}")
            if retry_count > 3:
                raise HTTPException(
                    status_code=500,
                    detail="Error scraping chart. Please try again later.",
                )
            await asyncio.sleep(2**retry_count)
            return await self._scrape_chart(
                scraping_url, retry_count + 1, default_timeout * 1.5
            )
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Error scraping chart. Please try again later.",
            )

    async def scrape(self, city: str, state: str):

        scraping_url = await self._get_scraping_url(city, state)
        if not scraping_url:
            raise HTTPException(
                status_code=400,
                detail="Invalid city or state provided. Please try again with a valid US city and state.",
            )

        chart_data = await self._scrape_chart(scraping_url)
        return chart_data


sales_median_price_scraper = SalesMedianPriceScraper()
