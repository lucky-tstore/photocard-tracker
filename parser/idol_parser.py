import json
import os
import re


_idols_cache = None


def load_idols():
    global _idols_cache
    if _idols_cache is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "idols.json")
        with open(path, "r", encoding="utf-8") as f:
            _idols_cache = json.load(f)
    return _idols_cache


def parse_idol_info(title):
    """제목에서 아이돌 그룹과 멤버 이름 추출. (group, member) 튜플 반환."""
    idols = load_idols()
    title_normalized = title.lower().replace(" ", "")

    found_group = None
    found_member = None
    best_group_match_len = 0
    best_member_match_len = 0

    for group_name, group_data in idols.items():
        # 그룹 이름 매칭
        for alias in group_data.get("aliases", [group_name]):
            alias_normalized = alias.lower().replace(" ", "")
            if alias_normalized in title_normalized and len(alias_normalized) > best_group_match_len:
                found_group = group_name
                best_group_match_len = len(alias_normalized)

        # 멤버 이름 매칭
        for member in group_data.get("members", []):
            for alias in member.get("aliases", [member["name"]]):
                alias_normalized = alias.lower().replace(" ", "")
                if len(alias_normalized) < 2:
                    continue
                if alias_normalized in title_normalized and len(alias_normalized) > best_member_match_len:
                    found_member = member["name"]
                    best_member_match_len = len(alias_normalized)
                    if found_group is None:
                        found_group = group_name

    return found_group, found_member


def is_photocard(title):
    """포토카드 관련 글인지 확인"""
    keywords = ["포토카드", "포카", "pc ", "photocard", "photo card", "트레카", "트레이딩카드"]
    title_lower = title.lower()
    return any(kw in title_lower for kw in keywords)
