"""
Dunyo va O'zbekiston yangiliklarini RSS orqali yuklab oluvchi va filtrlash xizmati.
Manbalar: Kun.uz, BBC O'zbek, Gazeta.uz
"""

import re
import html
import time
import hashlib
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    id: str
    title: str
    description: str
    link: str
    pub_date: str
    source: str
    category: str  # world, tech, economy, sport, general
    image_url: Optional[str] = None


def clean_html(raw_html: str) -> str:
    """HTML teglardan tozalash va chiroyli matn holatiga keltirish."""
    if not raw_html:
        return ""
    text = re.sub(r'<[^>]+>', '', raw_html)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def format_pub_date(date_str: str) -> str:
    """Sana formatini tushunarli holatga keltirish."""
    if not date_str:
        return "Yaqinda"
    try:
        # Masalan: Fri, 25 Sep 2026 14:53:10 +0500
        # Masalan: Fri, 25 Sep 2026 09:00:02 GMT
        dt = None
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a, %d %b %Y %H:%M:%S"
        ):
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue

        if dt:
            months_uz = {
                1: "yanvar", 2: "fevral", 3: "mart", 4: "aprel",
                5: "may", 6: "iyun", 7: "iyul", 8: "avgust",
                9: "sentabr", 10: "oktabr", 11: "noyabr", 12: "dekabr"
            }
            month_name = months_uz.get(dt.month, "")
            return f"{dt.day}-{month_name}, {dt.strftime('%H:%M')}"
    except Exception:
        pass
    return date_str.split("+")[0].strip()


class NewsService:
    def __init__(self, cache_ttl: int = 300):
        self.cache_ttl = cache_ttl
        self._cached_items: List[NewsItem] = []
        self._last_fetch_time: float = 0.0

    def _generate_id(self, link: str) -> str:
        return hashlib.md5(link.encode('utf-8')).hexdigest()[:10]

    async def _fetch_url(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    return await resp.text(encoding="utf-8", errors="replace")
                else:
                    logger.warning(f"Failed to fetch {url}, status: {resp.status}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    def _parse_bbc_rss(self, xml_content: str) -> List[NewsItem]:
        items = []
        try:
            root = ET.fromstring(xml_content)
            for it in root.findall('.//item'):
                title = clean_html(it.findtext('title', ''))
                link = (it.findtext('link', '') or '').strip()
                if not title or not link:
                    continue

                raw_desc = it.findtext('description', '')
                desc = clean_html(raw_desc)
                if len(desc) > 300:
                    desc = desc[:297] + "..."

                pub_date = format_pub_date(it.findtext('pubDate', ''))

                # Rasm olish
                image_url = None
                thumb = it.find('{http://search.yahoo.com/mrss/}thumbnail')
                if thumb is not None and 'url' in thumb.attrib:
                    image_url = thumb.attrib['url']

                item = NewsItem(
                    id=self._generate_id(link),
                    title=title,
                    description=desc,
                    link=link,
                    pub_date=pub_date,
                    source="BBC O'zbek (Jahon)",
                    category="world",
                    image_url=image_url
                )
                items.append(item)
        except Exception as e:
            logger.error(f"Error parsing BBC RSS: {e}")
        return items

    def _parse_kun_uz_rss(self, xml_content: str) -> List[NewsItem]:
        items = []
        try:
            root = ET.fromstring(xml_content)
            for it in root.findall('.//item'):
                title = clean_html(it.findtext('title', ''))
                link = (it.findtext('link', '') or '').strip()
                if not title or not link:
                    continue

                desc = clean_html(it.findtext('description', ''))
                if len(desc) > 300:
                    desc = desc[:297] + "..."

                pub_date = format_pub_date(it.findtext('pubDate', ''))
                raw_cat = (it.findtext('category', '') or '').lower()

                # Kategoriyani aniqlash
                if "jahon" in raw_cat:
                    category = "world"
                    src_label = "Kun.uz (Jahon)"
                elif "texnologiya" in raw_cat:
                    category = "tech"
                    src_label = "Kun.uz (Texnologiya)"
                elif "iqtisodiyot" in raw_cat:
                    category = "economy"
                    src_label = "Kun.uz (Iqtisodiyot)"
                elif "sport" in raw_cat:
                    category = "sport"
                    src_label = "Kun.uz (Sport)"
                elif "o‘zbekiston" in raw_cat or "ozbekiston" in raw_cat:
                    category = "uzb"
                    src_label = "Kun.uz (O'zbekiston)"
                else:
                    category = "general"
                    src_label = "Kun.uz"

                # Rasm olish (agar enclosure bo'lsa)
                image_url = None
                enc = it.find('enclosure')
                if enc is not None and 'url' in enc.attrib:
                    image_url = enc.attrib['url']

                item = NewsItem(
                    id=self._generate_id(link),
                    title=title,
                    description=desc,
                    link=link,
                    pub_date=pub_date,
                    source=src_label,
                    category=category,
                    image_url=image_url
                )
                items.append(item)
        except Exception as e:
            logger.error(f"Error parsing Kun.uz RSS: {e}")
        return items

    def _parse_gazeta_uz_rss(self, xml_content: str) -> List[NewsItem]:
        items = []
        try:
            root = ET.fromstring(xml_content)
            for it in root.findall('.//item'):
                title = clean_html(it.findtext('title', ''))
                link = (it.findtext('link', '') or '').strip()
                if not title or not link:
                    continue

                desc = clean_html(it.findtext('description', ''))
                if len(desc) > 300:
                    desc = desc[:297] + "..."

                pub_date = format_pub_date(it.findtext('pubDate', ''))

                image_url = None
                enc = it.find('enclosure')
                if enc is not None and 'url' in enc.attrib:
                    image_url = enc.attrib['url']

                item = NewsItem(
                    id=self._generate_id(link),
                    title=title,
                    description=desc,
                    link=link,
                    pub_date=pub_date,
                    source="Gazeta.uz",
                    category="general",
                    image_url=image_url
                )
                items.append(item)
        except Exception as e:
            logger.error(f"Error parsing Gazeta.uz RSS: {e}")
        return items

    async def refresh_all_news(self) -> List[NewsItem]:
        """Barcha RSS manbalaridan yangiliklarni qayta yuklash."""
        all_news: List[NewsItem] = []

        urls = [
            ("bbc", "https://feeds.bbci.co.uk/uzbek/rss.xml"),
            ("kun", "https://kun.uz/news/rss"),
            ("gazeta", "https://www.gazeta.uz/uz/rss/")
        ]

        async with aiohttp.ClientSession() as session:
            for source_key, url in urls:
                xml_data = await self._fetch_url(session, url)
                if not xml_data:
                    continue

                if source_key == "bbc":
                    parsed = self._parse_bbc_rss(xml_data)
                elif source_key == "kun":
                    parsed = self._parse_kun_uz_rss(xml_data)
                elif source_key == "gazeta":
                    parsed = self._parse_gazeta_uz_rss(xml_data)
                else:
                    parsed = []

                all_news.extend(parsed)

        # Takroriy havolalarni olib tashlash
        seen_links = set()
        unique_news = []
        for item in all_news:
            if item.link not in seen_links:
                seen_links.add(item.link)
                unique_news.append(item)

        self._cached_items = unique_news
        self._last_fetch_time = time.time()
        logger.info(f"Loaded {len(self._cached_items)} total news items to cache.")
        return self._cached_items

    async def get_all_cached(self, force_refresh: bool = False) -> List[NewsItem]:
        """Keshdagi barcha yangiliklarni olish, agar eskigan bo'lsa yangilash."""
        now = time.time()
        if force_refresh or (now - self._last_fetch_time > self.cache_ttl) or not self._cached_items:
            await self.refresh_all_news()
        return self._cached_items

    async def get_world_news(self, limit: int = 5, force_refresh: bool = False) -> List[NewsItem]:
        """Faqat Jahon / Dunyo yangiliklarini olish."""
        items = await self.get_all_cached(force_refresh=force_refresh)
        # category == 'world' yoki BBC manbasi
        world_items = [it for it in items if it.category == 'world' or "BBC" in it.source]
        return world_items[:limit]

    async def get_breaking_news(self, limit: int = 5, force_refresh: bool = False) -> List[NewsItem]:
        """Eng qaynoq / so'nggi chiqqan yangiliklar."""
        items = await self.get_all_cached(force_refresh=force_refresh)
        return items[:limit]

    async def get_by_category(self, category: str, limit: int = 5) -> List[NewsItem]:
        """Kategoriya bo'yicha olish (world, tech, economy, sport, uzb)."""
        items = await self.get_all_cached()
        if category == "world":
            return await self.get_world_news(limit=limit)

        cat_items = [it for it in items if it.category == category]
        # Agar berilgan kategoriyada kam bo'lsa, mos kalit so'zlar bo'yicha ham to'ldirish
        if len(cat_items) < limit:
            keywords = {
                "tech": ["sun'iy intellekt", "ai", "smartfon", "apple", "google", "ilon mask", "texnologiya", "robot"],
                "economy": ["narx", "dollar", "iqtisodiyot", "neft", "gaz", "bank", "moliya", "bozor"],
                "sport": ["futbol", "chempionat", "boks", "g'alaba", "match", "turnir", "real", "barselona"],
                "uzb": ["o'zbekiston", "toshkent", "prezident", "vazirlik", "viloyat"]
            }
            if category in keywords:
                for it in items:
                    if it not in cat_items:
                        lower_text = (it.title + " " + it.description).lower()
                        if any(kw in lower_text for kw in keywords[category]):
                            cat_items.append(it)
                            if len(cat_items) >= limit:
                                break

        return cat_items[:limit]

    async def search_news(self, query: str, limit: int = 5) -> List[NewsItem]:
        """Kalit so'z bo'yicha yangiliklarni qidirish."""
        if not query:
            return []
        items = await self.get_all_cached()
        q = query.strip().lower()
        results = []
        for it in items:
            if q in it.title.lower() or q in it.description.lower():
                results.append(it)
                if len(results) >= limit:
                    break
        return results

    async def get_item_by_id(self, item_id: str) -> Optional[NewsItem]:
        """ID bo'yicha aniq bitta yangilikni topish."""
        items = await self.get_all_cached()
        for it in items:
            if it.id == item_id:
                return it
        return None


# Global instansiya
news_service = NewsService()
