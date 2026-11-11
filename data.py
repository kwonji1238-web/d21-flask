import csv                                    # CSV 파일(표 파일)을 읽는 도구를 가져와요
from pathlib import Path                      # 파일 위치를 다루는 도구를 가져와요

# 이 파일(data.py)과 같은 폴더 안의 data 폴더 → classes.csv (프로젝트 폴더만 배포해도 파일이 같이 가요)
CSV_PATH = Path(__file__).resolve().parent / "data" / "classes.csv"   # CSV 파일 위치예요


def _to_number(text):                         # 글자를 숫자로 바꾸는 작은 도우미 함수예요 (_ 는 '이 파일 안에서만 써요' 표시)
    text = text.strip()                       # 글자 앞뒤 공백을 지워요
    if text == "":                            # 칸이 비어 있으면
        return None                           # '값 없음'(None)을 돌려줘요. 0도 nan도 아니에요
    return float(text)                        # 값이 있으면 숫자로 바꿔서 돌려줘요


def _valid_price(value):                      # 가격으로 쓸 수 있는 값인지 거르는 도우미 함수예요
    if value is None or value <= 0:           # 비었거나 0 이하이면
        return None                           # 가격이 없는 걸로 해요
    return value                              # 괜찮은 가격이면 그대로 써요


def load_classes():                           # CSV를 읽어서 클래스 목록을 만들어 주는 함수예요
    classes = []                              # 결과를 담을 빈 목록이에요
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:   # 파일을 열어요 (한글이 안 깨지게 utf-8)
        for row in csv.DictReader(f):         # 한 줄씩 읽어요. 첫 줄(제목)을 칸 이름으로 써요
            list_price = _valid_price(_to_number(row["정가"]))    # 정가를 읽어요 (비면 None)
            discount = _valid_price(_to_number(row["할인가"]))    # 할인가를 읽어요 (비면 None)
            price = discount if discount is not None else list_price   # 판매가: 할인가가 있으면 할인가, 없으면 정가
            on_sale = (discount is not None and list_price is not None
                       and discount < list_price)                 # 할인 중인가요? (둘 다 있고 할인가가 더 쌀 때만)
            reviews = int(_to_number(row["리뷰수"]) or 0)         # 리뷰 수를 읽어요 (비면 0)
            rating = _to_number(row["평점"])                      # 평점을 읽어요 (비면 None)
            if reviews == 0:                                      # 리뷰가 하나도 없으면
                rating = None                                     # 평점도 '없음'으로 해요
            classes.append({                                      # 클래스 한 개를 목록에 담아요
                "id": int(row["id"]),                                  # 번호
                "category": row["카테고리"],                      # 카테고리
                "region": row["지역"],                            # 지역
                "name": row["클래스명"],                          # 클래스 이름
                "list_price": list_price,                         # 정가 (없을 수 있어요)
                "price": price,                                   # 판매가 (없을 수 있어요)
                "on_sale": on_sale,                               # 할인 중인지 (True / False)
                "rating": rating,                                 # 평점 (없을 수 있어요)
                "reviews": reviews,                               # 리뷰 수
            })
    return classes                                                # 완성된 목록을 돌려줘요


def get_class(class_id):                      # 번호로 클래스 한 개를 찾는 함수예요
    for c in load_classes():                  # 클래스를 하나씩 살펴보다가
        if c["id"] == class_id:               # 번호가 같은 걸 만나면
            return c                          # 그 클래스를 돌려줘요
    return None                               # 끝까지 못 찾으면 '없음'(None)을 돌려줘요


def get_stats(classes):                       # 전체 통계를 계산해 주는 함수예요
    prices = [c["price"] for c in classes if c["price"] is not None]       # 판매가가 있는 것만 모아요 (빈칸 제외)
    ratings = [c["rating"] for c in classes if c["rating"] is not None]    # 평점이 있는 것만 모아요 (빈칸 제외)
    category_counts = {}                      # 카테고리별 개수를 담을 빈 사전이에요
    for category in get_categories(classes):  # 카테고리를 하나씩 살펴보며
        category_counts[category] = sum(1 for c in classes if c["category"] == category)   # 그 카테고리의 클래스 수를 세요
    return {                                  # 통계를 사전으로 묶어서 돌려줘요
        "total": len(classes),                                              # 전체 개수
        "avg_price": round(sum(prices) / len(prices)) if prices else None,  # 평균 판매가 (원 단위로 반올림, 값이 하나도 없으면 None)
        "price_inquiry_count": len(classes) - len(prices),                  # 가격 문의 수 (판매가가 빈 클래스 수)
        "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,   # 평균 평점 (소수 둘째 자리까지, 없으면 None)
        "no_review_count": len(classes) - len(ratings),                     # 리뷰 없음 수 (평점이 빈 클래스 수)
        "category_counts": category_counts,                                 # 카테고리별 개수
    }


def get_categories(classes):                  # 카테고리 이름을 중복 없이 모아 주는 함수예요
    return sorted({c["category"] for c in classes})   # 카테고리를 모아서 가나다순으로 정리해요


def filter_and_sort(classes, category="", sort=""):   # 거르고 정렬하는 함수예요
    result = classes                          # 일단 전체에서 시작해요
    if category:                              # 카테고리가 골라졌다면
        result = [c for c in result if c["category"] == category]   # 그 카테고리만 남겨요
    if sort == "price":                       # 싼 순으로 정렬하라고 했다면
        result = sorted(                      # 정렬해요
            result,
            key=lambda c: (c["price"] is None, c["price"] or 0),   # 먼저 '가격 문의인가?'(False가 앞), 그다음 가격 낮은 순
        )
    elif sort == "rating":                    # 평점 순으로 정렬하라고 했다면
        result = sorted(                      # 정렬해요
            result,
            key=lambda c: (c["rating"] is None, -(c["rating"] or 0), -c["reviews"]),   # 평점 없는 건 뒤로, 평점 높은 순, 같으면 리뷰 많은 순
        )
    elif sort == "reviews":                   # 리뷰 많은 순으로 정렬하라고 했다면
        result = sorted(result, key=lambda c: -c["reviews"])   # 리뷰 수가 많은 것부터 (같으면 원래 순서 유지)
    return result                             # 결과를 돌려줘요 (sort 가 비었거나 모르는 값이면 CSV 순서 = 추천순)
