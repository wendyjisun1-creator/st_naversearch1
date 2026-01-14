import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# .env 로드
load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def save_to_csv(df, prefix, keyword, year=""):
    """
    데이터프레임을 지시서 규칙에 따라 CSV로 저장
    파일명 형식: [내용]_[기간]_[수집날짜].csv
    """
    today = datetime.now().strftime("%Y%m%d")
    year_str = f"_{year}" if year else ""
    # 키워드 특수문자 제거 (파일명 안전용)
    safe_keyword = keyword.replace("/", "_").replace(" ", "")
    filename = f"{prefix}_{safe_keyword}{year_str}_{today}.csv"
    
    # data 폴더가 없으면 생성
    if not os.path.exists("data"):
        os.makedirs("data")
        
    path = os.path.join("data", filename)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"성공적으로 저장됨: {path}")

def get_shopping_trend(keyword, cat_id):
    """네이버 쇼핑인사이트 분야별 트렌드 API 호출 (2025년 데이터)"""
    url = "https://openapi.naver.com/v1/datalab/shopping/categories"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    body = {
        "startDate": "2025-01-01",
        "endDate": "2025-12-31",
        "timeUnit": "date",
        "category": [{"name": keyword, "param": [cat_id]}],
        "device": "",
        "gender": "",
        "ages": []
    }
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        res_json = response.json()
        if "results" in res_json and len(res_json["results"]) > 0:
            data = res_json["results"][0]["data"]
            df = pd.DataFrame(data)
            save_to_csv(df, "shopping_trend", keyword, "2025")
        else:
            print(f"데이터 결과가 없습니다: {keyword}")
    else:
        print(f"쇼핑 트렌드 API 오류 ({keyword}): {response.status_code} - {response.text}")

def get_blog_posts(keyword):
    """네이버 블로그 검색 API 호출 (최근 게시물 100개)"""
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display=100"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json().get("items", [])
        df = pd.DataFrame(items)
        save_to_csv(df, "blog_posts", keyword)
    else:
        print(f"블로그 검색 API 오류 ({keyword}): {response.status_code}")

def get_shop_products(keyword):
    """네이버 쇼핑 검색 API 호출 (최근 상품 100개)"""
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=100"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        items = response.json().get("items", [])
        df = pd.DataFrame(items)
        save_to_csv(df, "shop_products", keyword)
    else:
        print(f"쇼핑 검색 API 오류 ({keyword}): {response.status_code}")

if __name__ == "__main__":
    # 수집 대상 정의 (키워드 및 관련 카테고리 ID)
    targets = [
        {"keyword": "런닝화", "cat_id": "50000008"},  # 스포츠/레저
        {"keyword": "스마트워치", "cat_id": "50000262"}  # 디지털/가전 > 휴대폰액세서리 > 스마트워치
    ]
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("에러: .env 파일에 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET이 설정되어야 합니다.")
    else:
        for target in targets:
            kw = target["keyword"]
            cid = target["cat_id"]
            print(f"\n=== {kw} 데이터 수집 시작 ===")
            get_shopping_trend(kw, cid)
            get_blog_posts(kw)
            get_shop_products(kw)
        print("\n모든 데이터 수집 작업이 완료되었습니다.")
