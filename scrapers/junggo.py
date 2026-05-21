import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def scrape_junggo(keyword="포토카드", max_pages=5):
    base_url = "https://web.joongna.com/search"
    items = []

    for page in range(1, max_pages + 1):
        params = {
            "q": keyword,
            "page": page,
        }

        try:
            resp = requests.get(base_url, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")  # lxml 없이 동작

            products = soup.select("li[data-v-app] a, .product-item, article")

            # 중고나라 구조 파싱 (구조 변경에 대응하는 범용 파싱)
            product_cards = soup.select("a[href*='/product/']")

            if not product_cards:
                break

            for card in product_cards:
                try:
                    title_el = card.select_one("h2, h3, .title, [class*='title']")
                    price_el = card.select_one("[class*='price'], .price")
                    img_el = card.select_one("img")

                    if not title_el:
                        continue

                    title = title_el.get_text(strip=True)
                    price_text = price_el.get_text(strip=True) if price_el else "0"
                    price_clean = "".join(filter(str.isdigit, price_text))
                    price = int(price_clean) if price_clean else 0
                    href = card.get("href", "")
                    link = f"https://web.joongna.com{href}" if href.startswith("/") else href
                    image = img_el.get("src", "") if img_el else ""

                    if price <= 0:
                        continue

                    items.append({
                        "platform": "중고나라",
                        "title": title,
                        "price": price,
                        "link": link,
                        "image": image,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "status": "판매중",
                    })
                except Exception:
                    continue

            print(f"[중고나라] 페이지 {page} 완료 ({len(product_cards)}개)")
            time.sleep(1.0)

        except requests.exceptions.RequestException as e:
            print(f"[중고나라] 페이지 {page} 요청 실패: {e}")
            break

    return items
