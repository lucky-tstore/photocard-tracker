"""
텔레그램 알림 봇 — GitHub Actions에서 실행
사용법: python bot/telegram_bot.py

환경변수:
  TELEGRAM_BOT_TOKEN  : BotFather에서 발급받은 토큰
  TELEGRAM_CHANNEL_ID : 채널/그룹 chat_id (예: @mychannelname 또는 -1001234567890)
"""

import json
import os
import sys

import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "")
PRICES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "prices.json")
SITE_URL = os.environ.get("SITE_URL", "https://yourusername.github.io/photocard-tracker")


def send_message(text):
    if not BOT_TOKEN or not CHANNEL_ID:
        print("TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHANNEL_ID 환경변수가 없습니다.")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    resp = requests.post(url, json=payload, timeout=10)
    return resp.ok


def format_price_report():
    """그룹별 시세 요약 메시지 생성"""
    with open(PRICES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    stats = data.get("stats", {}).get("groups", {})
    last_updated = data.get("last_updated", "")

    if not stats:
        return None

    top_groups = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)[:10]

    lines = [
        "💜 <b>포카시세 일일 업데이트</b>",
        f"📅 {last_updated}",
        "",
        "📊 <b>그룹별 평균 시세 TOP 10</b>",
    ]

    for group, s in top_groups:
        avg = f"{s['avg']:,}"
        mn = f"{s['min']:,}"
        lines.append(f"• <b>{group}</b>: 평균 {avg}원 (최저 {mn}원, {s['count']}건)")

    lines += ["", f"🔍 상세 시세 → {SITE_URL}"]
    return "\n".join(lines)


def main():
    if not os.path.exists(PRICES_PATH):
        print("prices.json 없음, 봇 실행 건너뜀")
        sys.exit(0)

    msg = format_price_report()
    if not msg:
        print("전송할 데이터 없음")
        sys.exit(0)

    ok = send_message(msg)
    print("메시지 전송 성공" if ok else "메시지 전송 실패")


if __name__ == "__main__":
    main()
