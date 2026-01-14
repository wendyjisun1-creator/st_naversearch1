import os
import requests
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

def get_api_keys():
    """자격 증명 로드 (Streamlit Cloud Secrets 또는 로컬 .env)"""
    # 1. Streamlit Cloud Secrets 확인
    try:
        if "NAVER_CLIENT_ID" in st.secrets:
            return st.secrets["NAVER_CLIENT_ID"], st.secrets["NAVER_CLIENT_SECRET"]
    except:
        pass
    
    # 2. 로컬 .env 확인
    load_dotenv()
    return os.getenv("NAVER_CLIENT_ID"), os.getenv("NAVER_CLIENT_SECRET")

CLIENT_ID, CLIENT_SECRET = get_api_keys()

@st.cache_data(ttl=3600)
def fetch_shopping_trend(keyword, start_date="2025-01-01", end_date="2025-12-31"):
    """실시간 쇼핑 트렌드 API 호출 (카테고리 ID가 없는 범용 검색은 '스포츠/레저' 50000008 기본값 사용)"""
    url = "https://openapi.naver.com/v1/datalab/shopping/categories"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    # 범용 검색을 위해 카테고리는 최상위 대분류 중 하나를 선택하거나 검색어와 매칭 필요
    # 여기서는 예시로 스포츠/레저(50000008)를 사용하거나, 실제로는 검색어별 매징 로직이 필요함
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "category": [{"name": keyword, "param": ["50000008"]}], # 범용 예시 ID
        "device": "",
        "gender": "",
        "ages": []
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if response.status_code == 200:
            data = response.json()["results"][0]["data"]
            df = pd.DataFrame(data)
            df['period'] = pd.to_datetime(df['period'])
            df['keyword'] = keyword
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Trend API Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_shopping_search(keyword):
    """실시간 쇼핑 상품 검색 API 호출"""
    url = f"https://openapi.naver.com/v1/search/shop.json?query={keyword}&display=100"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            items = response.json().get("items", [])
            df = pd.DataFrame(items)
            df['lprice'] = pd.to_numeric(df['lprice'], errors='coerce')
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Shopping API Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_blog_search(keyword):
    """실시간 블로그 검색 API 호출"""
    url = f"https://openapi.naver.com/v1/search/blog.json?query={keyword}&display=100"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            items = response.json().get("items", [])
            return pd.DataFrame(items)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Blog API Error: {e}")
        return pd.DataFrame()
