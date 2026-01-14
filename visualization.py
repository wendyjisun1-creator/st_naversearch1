import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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
                 title=f'[{keyword}] 주요 브랜드별 가격 범위 (Box Plot)',
                 labels={'lprice': '최저가 (원)', 'brand': '브랜드'},
                 color='brand',
                 template='plotly_dark')
    return fig
