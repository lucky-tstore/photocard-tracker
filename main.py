import json
import os
from datetime import datetime

from scrapers.bunjang import scrape_bunjang
from scrapers.junggo import scrape_junggo
from parser.idol_parser import parse_idol_info, is_photocard


PRICES_PATH = os.path.join(os.path.dirname(__file__), "docs", "data", "prices.json")
MAX_ITEMS = 8000


def load_existing():
    if os.path.exists(PRICES_PATH):
        with open(PRICES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"items": [], "last_updated": "", "stats": {}}


def save_data(data):
    with open(PRICES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def build_stats(items):
    """그룹/멤버별 평균 시세 계산"""
    group_prices = {}
    member_prices = {}

    for item in items:
        group = item.get("group")
        member = item.get("member")
        price = item.get("price", 0)

        if not group or price <= 0:
            continue

        group_prices.setdefault(group, []).append(price)
        if member:
            key = f"{group}::{member}"
            member_prices.setdefault(key, []).append(price)

    stats = {"groups": {}, "members": {}}

    for group, prices in group_prices.items():
        stats["groups"][group] = {
            "avg": int(sum(prices) / len(prices)),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
        }

    for key, prices in member_prices.items():
        group, member = key.split("::")
        stats["members"].setdefault(group, {})[member] = {
            "avg": int(sum(prices) / len(prices)),
            "min": min(prices),
            "max": max(prices),
            "count": len(prices),
        }

    return stats


def main():
    print(f"=== 포토카드 시세 수집 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===")

    all_new = []

    # 번개장터 수집
    print("\n[1/2] 번개장터 수집 중...")
    try:
        bunjang_items = scrape_bunjang("포토카드", max_pages=10)
        all_new.extend(bunjang_items)
        print(f"  → 번개장터 {len(bunjang_items)}개 수집")
    except Exception as e:
        print(f"  → 번개장터 오류: {e}")

    # 중고나라 수집
    print("\n[2/2] 중고나라 수집 중...")
    try:
        junggo_items = scrape_junggo("포토카드", max_pages=5)
        all_new.extend(junggo_items)
        print(f"  → 중고나라 {len(junggo_items)}개 수집")
    except Exception as e:
        print(f"  → 중고나라 오류: {e}")

    print(f"\n총 신규 수집: {len(all_new)}개")

    # 아이돌 파싱
    print("아이돌/멤버 파싱 중...")
    for item in all_new:
        group, member = parse_idol_info(item["title"])
        item["group"] = group
        item["member"] = member

    # 기존 데이터와 병합 (중복 링크 제거)
    existing = load_existing()
    existing_links = {item["link"] for item in existing["items"]}
    new_only = [item for item in all_new if item["link"] not in existing_links]

    merged = new_only + existing["items"]
    merged = merged[:MAX_ITEMS]  # 최대 8000개 유지

    # 통계 계산
    stats = build_stats(merged)

    result = {
        "items": merged,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stats": stats,
    }

    save_data(result)
    print(f"\n완료! 신규 {len(new_only)}개 추가, 총 {len(merged)}개 저장")
    print(f"인식된 그룹 수: {len(stats['groups'])}개")


if __name__ == "__main__":
    main()
