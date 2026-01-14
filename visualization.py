import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def plot_trend_comparison(df):
    """트렌드 라인 차트 (1/5)"""
    if df.empty: return None
    fig = px.line(df, x='period', y='ratio', color='keyword',
                  title='키워드별 쇼핑 검색 트렌드 비교 (2025)',
                  labels={'ratio': '검색 상대 비율', 'period': '날짜'},
                  template='plotly_white')
    fig.update_layout(hovermode='x unified')
    return fig

def plot_price_distribution(df, keyword):
    """가격 분포 히스토그램 (2/5)"""
    if df.empty: return None
    fig = px.histogram(df, x='lprice', nbins=30,
                       title=f'[{keyword}] 가격 분포 분석',
                       labels={'lprice': '최저가 (원)'},
                       color_discrete_sequence=['#ff7f0e'],
                       template='plotly_white')
    return fig

def plot_brand_share(df, keyword):
    """브랜드 점유율 바 차트 (3/5)"""
    if df.empty: return None
    brand_counts = df['brand'].value_counts().head(10).reset_index()
    brand_counts.columns = ['brand', 'count']
    fig = px.bar(brand_counts, x='brand', y='count',
                 title=f'[{keyword}] 상위 10개 브랜드 점유율',
                 labels={'count': '노출 수', 'brand': '브랜드'},
                 color='count',
                 template='plotly_dark')
    return fig

def plot_category_share(df, keyword):
    """카테고리 구성 파이 차트 (4/5)"""
    if df.empty: return None
    cat_counts = df['category3'].value_counts().head(5).reset_index()
    cat_counts.columns = ['category', 'count']
    fig = px.pie(cat_counts, values='count', names='category',
                 title=f'[{keyword}] 주요 카테고리 구성 (중분류)',
                 hole=0.4,
                 template='plotly_dark')
    return fig

def plot_brand_price_box(df, keyword):
    """브랜드별 가격 범위 박스 플롯 (5/5)"""
    if df.empty: return None
    # 데이터가 많은 상위 5개 브랜드만 추출
    top_brands = df['brand'].value_counts().head(5).index
    filtered_df = df[df['brand'].isin(top_brands)]
    fig = px.box(filtered_df, x='brand', y='lprice',
                 title=f'[{keyword}] 주요 브랜드별 가격 범위 (상태 분석)',
                 labels={'lprice': '최저가 (원)', 'brand': '브랜드'},
                 color='brand',
                 template='plotly_white')
    return fig

# --- 심화 EDA를 위한 추가 시각화 함수 ---

def plot_missing_values(df):
    """컬럼별 결측값 개수 및 비율 시각화 (Bar 2/2)"""
    if df.empty: return None
    missing_data = df.isnull().sum().reset_index()
    missing_data.columns = ['column', 'missing_count']
    missing_data['ratio'] = (missing_data['missing_count'] / len(df)) * 100
    
    fig = px.bar(missing_data, x='column', y='missing_count',
                 text=missing_data['ratio'].apply(lambda x: f'{x:.1f}%'),
                 title='데이터셋 컬럼별 결측치 현황',
                 labels={'missing_count': '결측치 개수', 'column': '컬럼명'},
                 template='plotly_white',
                 color_discrete_sequence=['#ef4444']) # Red for warning
    fig.update_traces(textposition='outside')
    return fig

def plot_correlation_heatmap(df):
    """수치형 변수 간 상관관계 분석 (Heatmap 1/2)"""
    # 쇼핑 데이터에서 수치형은 lprice 외에 많지 않으므로 파생 변수 생성
    if df.empty: return None
    numeric_df = df.copy()
    numeric_df['title_len'] = numeric_df['title'].str.len()
    numeric_df['brand_len'] = numeric_df['brand'].astype(str).apply(lambda x: len(x) if x != 'nan' else 0)
    
    corr = numeric_df[['lprice', 'title_len', 'brand_len']].corr()
    
    fig = px.imshow(corr, text_auto=True, aspect="auto",
                    title='주요 수치형 변수 상관관계 (Heatmap 1/2)',
                    color_continuous_scale='RdBu_r', 
                    template='plotly_white')
    return fig

def plot_category_brand_heatmap(df):
    """카테고리 vs 브랜드 빈도 분석 (Heatmap 2/2)"""
    if df.empty: return None
    top_brands = df['brand'].value_counts().head(8).index
    top_cats = df['category3'].value_counts().head(8).index
    
    filtered = df[df['brand'].isin(top_brands) & df['category3'].isin(top_cats)]
    pivot = pd.crosstab(filtered['category3'], filtered['brand'])
    
    fig = px.imshow(pivot, text_auto=True, aspect="auto",
                    title='카테고리별 브랜드 노출 빈도 (Heatmap 2/2)',
                    color_continuous_scale='YlGnBu',
                    template='plotly_white')
    return fig

def plot_mall_price_bar(df):
    """판매처별 평균 가격 비교 (Bar 2/2)"""
    if df.empty: return None
    mall_stats = df.groupby('mallName')['lprice'].mean().reset_index().sort_values('lprice', ascending=False).head(10)
    
    fig = px.bar(mall_stats, x='mallName', y='lprice',
                 title='주요 판매처별 평균가 비교',
                 labels={'lprice': '평균 최저가', 'mallName': '판매처'},
                 template='plotly_white',
                 color='lprice',
                 color_continuous_scale='Viridis')
    return fig
