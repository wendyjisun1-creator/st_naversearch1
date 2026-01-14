import os
import pandas as pd
import glob
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = "data"

def get_latest_csv(prefix, keyword):
    """지정된 접두사와 키워드에 해당하는 가장 최근 CSV 파일을 반환"""
    safe_keyword = keyword.replace("/", "_").replace(" ", "")
    pattern = os.path.join(DATA_DIR, f"{prefix}_{safe_keyword}*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    # 파일명 기반 정렬 (날짜가 포함되어 있으므로 최신 파일이 뒤로 감)
    return sorted(files)[-1]

def load_trend_data(keywords):
    """여러 키워드의 트렌드 데이터를 불러와 통합 데이터프레임 생성"""
    all_data = []
    for kw in keywords:
        file = get_latest_csv("shopping_trend", kw)
        if file:
            df = pd.read_csv(file)
            df['keyword'] = kw
            all_data.append(df)
    
    if not all_data:
        return pd.DataFrame(columns=['period', 'ratio', 'keyword'])
    
    combined = pd.concat(all_data, ignore_index=True)
    combined['period'] = pd.to_datetime(combined['period'])
    return combined

def load_shopping_data(keyword):
    """쇼핑 검색 결과 데이터 로드"""
    file = get_latest_csv("shop_products", keyword)
    if file:
        df = pd.read_csv(file)
        # 가격 전처리
        df['lprice'] = pd.to_numeric(df['lprice'], errors='coerce')
        return df
    return pd.DataFrame()

def load_blog_data(keyword):
    """블로그 검색 결과 데이터 로드"""
    file = get_latest_csv("blog_posts", keyword)
    if file:
        return pd.read_csv(file)
    return pd.DataFrame()
