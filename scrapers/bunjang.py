import requests
import time
from datetime import datetime


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bunjang.co.kr/",
    "Accept": "application/json",
}


def scrape_bunjang(keyword="포토카드", max_pages=10):
    base_url = "https://api.bunjang.co.kr/api/1/find_v2.json"
    items = []

    for page in range(max_pages):
        params = {
            "q": keyword,
            "page": page,
            "n": 100,
            "order": "date",
            "req_ref": "search",
            "stat": "1",
        }

        try:
            resp = requests.get(base_url, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            products = data.get("list", [])
            if not products:
                break

            for item in products:
                price_raw = item.get("price", "0")
                try:
                    price = int(str(price_raw).replace(",", ""))
                except (ValueError, TypeError):
                    price = 0

                if price <= 0:
                    continue

                pid = item.get("pid", "")
                items.append({
                    "platform": "번개장터",
                    "title": item.get("name", "").strip(),
                    "price": price,
                    "link": f"https://www.bunjang.co.kr/products/{pid}",
                    "image": item.get("product_image", ""),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": item.get("status", ""),
                })

            print(f"[번개장터] 페이지 {page + 1} 완료 ({len(products)}개)")
            time.sleep(0.8)

        except requests.exceptions.RequestException as e:
            print(f"[번개장터] 페이지 {page} 요청 실패: {e}")
            break
        except Exception as e:
            print(f"[번개장터] 페이지 {page} 오류: {e}")
            break

    return items
