#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 15:14:04 2024

@author: antoinepury
"""

##scrapping script - no touch - Final

import asyncio
import json
from playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()

async def scrape_all_related_pages(start_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.new_page()

        await page.goto(start_url)

        links = await page.evaluate("""
            Array.from(document.querySelectorAll('a'))
            .map(anchor => anchor.href)
            .filter(href => href.startsWith(window.location.origin))
        """)

        links = list(set(links))

        print(f"Found {len(links)} related pages to scrape.")

        scraped_data = {}

        for link in links:
            await page.goto(link)
            print(f"Scraping {link}")

            title = await page.title()
            content = (await page.evaluate("document.body.innerText"))[:20000]

            scraped_data[link] = {
                "title": title,
                "content": content
            }
            print(f"Scraped content from {link}")

        await browser.close()

        with open("scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)

        print("Scraping complete. Data saved to 'scraped_data.json'.")

start_url = 'https://docs.step.finance/'
asyncio.run(scrape_all_related_pages(start_url))