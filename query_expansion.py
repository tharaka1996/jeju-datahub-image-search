# -*- coding: utf-8 -*-
"""
query_expansion.py - Korean & English Domain Query Expansion Module
Maps colloquial natural language and English queries to official Jeju Data Hub / KSIC industry classifications.
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from pathlib import Path
from config import INDUSTRIES_PATH


@dataclass
class QueryExpansionResult:
    original_query: str
    expanded_terms: List[str] = field(default_factory=list)
    matched_categories: List[str] = field(default_factory=list)
    domain_explanation: str = ""

    def get_display_terms(self) -> List[str]:
        """Returns unique terms formatted for display badges."""
        return [t for t in self.expanded_terms if t.lower() != self.original_query.strip().lower()]


class QueryExpander:
    """
    Bilingual query expansion engine for Jeju Data Hub statistical reports.
    Supports English & Korean synonyms, KSIC industry classifications, and everyday terms.
    """

    # Core bilingual mapping of common terms to official Jeju statistical and KSIC classifications
    EXPANSION_DICTIONARY: Dict[str, Dict[str, any]] = {
        # 1. Rental Car
        "rental car": {
            "category": "자동차 임대 (Transportation)",
            "official_ksic": "자동차임대업",
            "terms": ["자동차임대업", "자동차임대", "렌터카", "렌트카", "차량대여", "차량임대", "렌트", "car rental", "rental car"]
        },
        "렌터카": {
            "category": "자동차 임대 (Transportation)",
            "official_ksic": "자동차임대업",
            "terms": ["자동차임대업", "자동차임대", "렌터카", "렌트카", "차량대여", "차량임대", "렌트", "rental car"]
        },
        "렌트카": {
            "category": "자동차 임대 (Transportation)",
            "official_ksic": "자동차임대업",
            "terms": ["자동차임대업", "자동차임대", "렌터카", "렌트카", "차량대여", "차량임대", "렌트"]
        },

        # 2. Dining Out / Restaurant
        "restaurant": {
            "category": "외식 / 식음료 (Dining & F&B)",
            "official_ksic": "음식점업",
            "terms": ["한식음식점업", "중식음식점업", "일식음식점업", "서양식음식점업", "기타외국식음식점업", "음식점", "식당", "외식", "dining out", "restaurant"]
        },
        "dining out": {
            "category": "외식 / 식음료 (Dining & F&B)",
            "official_ksic": "음식점업",
            "terms": ["한식음식점업", "중식음식점업", "일식음식점업", "서양식음식점업", "음식점", "식당", "외식", "식음료", "restaurant"]
        },
        "외식": {
            "category": "외식 / 식음료 (Dining & F&B)",
            "official_ksic": "음식점업",
            "terms": ["한식음식점업", "중식음식점업", "일식음식점업", "서양식음식점업", "음식점", "식당", "외식업", "식음료", "restaurant"]
        },
        "식당": {
            "category": "외식 / 식음료 (Dining & F&B)",
            "official_ksic": "음식점업",
            "terms": ["한식음식점업", "중식음식점업", "일식음식점업", "서양식음식점업", "음식점", "외식", "restaurant"]
        },
        "음식": {
            "category": "외식 / 식음료 (Dining & F&B)",
            "official_ksic": "음식점업",
            "terms": ["한식음식점업", "일식음식점업", "중식음식점업", "서양식음식점업", "음식점", "외식", "food"]
        },

        # 3. Hotel / Lodging / Accommodation
        "hotel": {
            "category": "숙박업 (Accommodation)",
            "official_ksic": "호텔업 / 휴양콘도운영업",
            "terms": ["호텔업", "휴양콘도운영업", "여관업", "호텔", "콘도", "리조트", "숙박", "숙박업", "lodging", "hotel"]
        },
        "accommodation": {
            "category": "숙박업 (Accommodation)",
            "official_ksic": "호텔업 / 휴양콘도운영업",
            "terms": ["호텔업", "휴양콘도운영업", "여관업", "호텔", "숙박", "리조트", "lodging", "hotel"]
        },
        "숙박": {
            "category": "숙박업 (Accommodation)",
            "official_ksic": "호텔업 / 휴양콘도운영업",
            "terms": ["호텔업", "휴양콘도운영업", "여관업", "호텔", "콘도", "리조트", "숙박", "숙박업", "hotel"]
        },
        "호텔": {
            "category": "숙박업 (Accommodation)",
            "official_ksic": "호텔업",
            "terms": ["호텔업", "휴양콘도운영업", "여관업", "숙박", "리조트", "hotel"]
        },
        "리조트": {
            "category": "숙박업 (Accommodation)",
            "official_ksic": "휴양콘도운영업",
            "terms": ["휴양콘도운영업", "호텔업", "숙박", "콘도", "resort"]
        },

        # 4. Tourism / Travel
        "tourism": {
            "category": "관광 / 여행 (Tourism & Travel)",
            "official_ksic": "여행사업 / 관광민예품및선물용품소매업",
            "terms": ["여행사업", "여행사", "관광", "관광객", "내국인관광객", "외국인관광객", "관광민예품", "travel", "tourism"]
        },
        "travel": {
            "category": "관광 / 여행 (Tourism & Travel)",
            "official_ksic": "여행사업",
            "terms": ["여행사업", "여행사", "관광", "관광객", "전시및행사대행업", "tourism"]
        },
        "관광": {
            "category": "관광 / 여행 (Tourism & Travel)",
            "official_ksic": "여행사업 / 관광민예품소매업",
            "terms": ["여행사업", "관광객", "내국인관광객", "외국인관광객", "관광민예품및선물용품소매업", "관광", "tourism"]
        },
        "여행": {
            "category": "관광 / 여행 (Tourism & Travel)",
            "official_ksic": "여행사업",
            "terms": ["여행사업", "여행사", "관광", "관광객", "travel"]
        },

        # 5. Golf Course
        "golf course": {
            "category": "골프 / 레저 (Sports & Golf)",
            "official_ksic": "골프장운영업",
            "terms": ["골프장운영업", "골프장", "골프", "그외기타스포츠시설운영업", "golf", "golf course"]
        },
        "golf": {
            "category": "골프 / 레저 (Sports & Golf)",
            "official_ksic": "골프장운영업",
            "terms": ["골프장운영업", "골프장", "골프", "golf"]
        },
        "골프장": {
            "category": "골프 / 레저 (Sports & Golf)",
            "official_ksic": "골프장운영업",
            "terms": ["골프장운영업", "골프장", "골프", "golf"]
        },
        "골프": {
            "category": "골프 / 레저 (Sports & Golf)",
            "official_ksic": "골프장운영업",
            "terms": ["골프장운영업", "골프장", "골프", "golf"]
        },

        # 6. Consumer Spending / Consumption
        "consumer spending": {
            "category": "소비 지출 / 카드 (Consumer Spending)",
            "official_ksic": "소비동향분석",
            "terms": ["소비동향", "카드이용금액", "신용카드", "소비금액", "소비지출", "BC카드", "결제금액", "spending"]
        },
        "consumption": {
            "category": "소비 지출 / 카드 (Consumer Spending)",
            "official_ksic": "소비동향분석",
            "terms": ["소비동향", "카드이용금액", "신용카드", "소비금액", "소비지출", "소비", "spending"]
        },
        "소비": {
            "category": "소비 지출 / 카드 (Consumer Spending)",
            "official_ksic": "소비동향분석",
            "terms": ["소비동향", "카드이용금액", "신용카드", "소비", "소비지출", "BC카드", "결제금액"]
        },
        "카드": {
            "category": "소비 지출 / 카드 (Consumer Spending)",
            "official_ksic": "소비동향분석",
            "terms": ["카드이용금액", "신용카드", "BC카드", "이용금액", "소비동향", "결제"]
        },

        # 7. Population / Demographics
        "population": {
            "category": "인구 통계 (Demographics)",
            "official_ksic": "주민등록인구통계",
            "terms": ["주민등록인구", "인구통계", "인구", "거주인구", "내국인", "외국인", "demographics", "population"]
        },
        "인구": {
            "category": "인구 통계 (Demographics)",
            "official_ksic": "주민등록인구통계",
            "terms": ["주민등록인구", "인구통계", "거주인구", "인구수", "인구", "population"]
        },

        # 8. Employment / Labor
        "employment": {
            "category": "고용 / 노동 (Labor & Employment)",
            "official_ksic": "고용동향",
            "terms": ["고용", "취업자", "실업률", "일자리", "종사자수", "labor", "employment"]
        },
        "고용": {
            "category": "고용 / 노동 (Labor & Employment)",
            "official_ksic": "고용동향",
            "terms": ["고용", "취업자", "실업률", "일자리", "종사자수", "employment"]
        },

        # 9. Wind Farm / Renewable Energy (Slide 4 prompt example)
        "wind farm": {
            "category": "신재생에너지 (Renewable Energy)",
            "official_ksic": "신재생에너지발전업",
            "terms": ["풍력발전", "풍력", "신재생에너지", "풍력단지", "풍력발전소", "wind power", "wind farm"]
        },
        "풍력": {
            "category": "신재생에너지 (Renewable Energy)",
            "official_ksic": "신재생에너지발전업",
            "terms": ["풍력발전", "풍력", "신재생에너지", "풍력단지", "wind power"]
        },
        "풍력발전": {
            "category": "신재생에너지 (Renewable Energy)",
            "official_ksic": "신재생에너지발전업",
            "terms": ["풍력발전", "풍력", "신재생에너지", "풍력단지", "wind farm"]
        },

        # 10. Duty Free / Shopping
        "duty free": {
            "category": "쇼핑 / 면세점 (Retail & Duty Free)",
            "official_ksic": "면세점",
            "terms": ["면세점", "종합소매업", "관광민예품및선물용품소매업", "쇼핑", "소매", "duty free"]
        },
        "면세점": {
            "category": "쇼핑 / 면세점 (Retail & Duty Free)",
            "official_ksic": "면세점",
            "terms": ["면세점", "종합소매업", "관광민예품및선물용품소매업", "쇼핑", "duty free"]
        },
        "쇼핑": {
            "category": "쇼핑 / 면세점 (Retail & Duty Free)",
            "official_ksic": "종합소매업",
            "terms": ["면세점", "종합소매업", "체인화편의점", "대형종합소매업", "슈퍼마켓", "shopping"]
        },

        # 11. Gas Station
        "gas station": {
            "category": "주유소 / 에너지 (Fuel & Gas)",
            "official_ksic": "차량용주유소운영업 / 차량용가스충전업",
            "terms": ["차량용주유소운영업", "차량용가스충전업", "주유소", "충전소", "가스충전", "gas station"]
        },
        "주유소": {
            "category": "주유소 / 에너지 (Fuel & Gas)",
            "official_ksic": "차량용주유소운영업",
            "terms": ["차량용주유소운영업", "차량용가스충전업", "주유소", "충전소", "가스충전", "gas station"]
        },

        # 12. Cafe / Beverages
        "cafe": {
            "category": "카페 / 음료 (Cafe & Beverages)",
            "official_ksic": "비알콜음료점업",
            "terms": ["비알콜음료점업", "비알콜음료", "음료점", "카페", "커피", "음료", "cafe", "coffee"]
        },
        "카페": {
            "category": "카페 / 음료 (Cafe & Beverages)",
            "official_ksic": "비알콜음료점업",
            "terms": ["비알콜음료점업", "비알콜음료", "음료점", "카페", "커피", "cafe"]
        },
        "커피": {
            "category": "카페 / 음료 (Cafe & Beverages)",
            "official_ksic": "비알콜음료점업",
            "terms": ["비알콜음료점업", "음료점", "카페", "커피", "coffee"]
        }
    }

    def __init__(self, custom_industries_path: Optional[Path] = None):
        self.industries = []
        path = custom_industries_path or INDUSTRIES_PATH
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.industries = json.load(f)
            except Exception:
                self.industries = []

    def expand_query(self, query: str) -> QueryExpansionResult:
        """
        Expands the user's natural query into related domain terms and KSIC industry terms.
        Does not replace the original query; preserves user intent while enriching context.
        """
        if not query or not query.strip():
            return QueryExpansionResult(original_query="")

        clean_query = query.strip()
        q_lower = clean_query.lower()

        expanded_terms_set: Set[str] = {clean_query}
        matched_categories: Set[str] = set()
        explanations: List[str] = []

        # 1. Match dictionary keys
        for key, info in self.EXPANSION_DICTIONARY.items():
            key_lower = key.lower()
            # Word boundary or substring match for natural phrases
            if key_lower in q_lower or q_lower in key_lower:
                for term in info["terms"]:
                    expanded_terms_set.add(term)
                matched_categories.add(info["category"])
                official = info.get("official_ksic", "")
                explanations.append(f"'{key}' -> 표준통계업종 '{official}'")

        # 2. Check overlap with KSIC official list
        for ind in self.industries:
            ind_clean = ind.replace("업", "")
            if len(ind_clean) >= 2 and (ind_clean in clean_query or clean_query in ind_clean):
                expanded_terms_set.add(ind)

        # 3. Tokenize words in multi-word query
        tokens = [t.strip() for t in re.split(r'[\s,\+\-_]+', clean_query) if len(t.strip()) > 0]
        for token in tokens:
            expanded_terms_set.add(token)
            t_lower = token.lower()
            for key, info in self.EXPANSION_DICTIONARY.items():
                if t_lower == key.lower():
                    for term in info["terms"]:
                        expanded_terms_set.add(term)
                    matched_categories.add(info["category"])

        explanation_str = ""
        if explanations:
            explanation_str = "연관 도메인 확장: " + ", ".join(list(dict.fromkeys(explanations))[:3])
        elif matched_categories:
            explanation_str = f"분류: {', '.join(matched_categories)}"
        else:
            explanation_str = "기본 자연어 검색 (확장어 없음)"

        return QueryExpansionResult(
            original_query=clean_query,
            expanded_terms=sorted(list(expanded_terms_set)),
            matched_categories=sorted(list(matched_categories)),
            domain_explanation=explanation_str
        )


if __name__ == "__main__":
    expander = QueryExpander()
    for test_q in ["rental car", "wind farm", "골프장", "dining out", "주유소", "unknown query"]:
        res = expander.expand_query(test_q)
        print(f"\nQuery: '{res.original_query}'")
        print(f"Categories: {res.matched_categories}")
        print(f"Explanation: {res.domain_explanation}")
        print(f"Expanded Terms: {res.expanded_terms[:8]} (total: {len(res.expanded_terms)})")
