import streamlit as st
import pandas as pd
import data_manager as dm
import visualization as viz

# 페이지 설정
st.set_page_config(page_title="Naver API Insight Dashboard", layout="wide", initial_sidebar_state="expanded")

# 사이드바 설정
st.sidebar.title("🔍 분석 설정")
available_keywords = ["런닝화", "스마트워치"]
selected_keywords = st.sidebar.multiselect("비교할 키워드 선택", available_keywords, default=["런닝화"])

main_keyword = st.sidebar.selectbox("상세 분석 키워드 (EDA)", selected_keywords if selected_keywords else available_keywords)

st.sidebar.markdown("---")
st.sidebar.info("네이버 API 데이터를 활용한 실시간 분석 대시보드입니다.")

# 데이터 로드
trend_df = dm.load_trend_data(selected_keywords)
shop_df = dm.load_shopping_data(main_keyword)
blog_df = dm.load_blog_data(main_keyword)

# 메인 타이틀
st.title("📊 Naver API 데이터 통찰 대시보드")
st.markdown(f"**실시간 수집된 데이터를 바탕으로 {', '.join(selected_keywords)} 시장을 분석합니다.**")

# 상단 지표 (Metrics)
col1, col2, col3 = st.columns(3)
if not trend_df.empty:
    for i, kw in enumerate(selected_keywords[:3]): # 최대 3개까지 메트릭 표시
        kw_data = trend_df[trend_df['keyword'] == kw]
        if not kw_data.empty:
            latest_ratio = kw_data.iloc[-1]['ratio']
            prev_ratio = kw_data.iloc[-2]['ratio'] if len(kw_data) > 1 else latest_ratio
            delta = round(latest_ratio - prev_ratio, 2)
            [col1, col2, col3][i].metric(f"{kw} 최신 지수", f"{latest_ratio:.1f}", f"{delta}")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📈 검색 트렌드 분석", "🛍️ 쇼핑 & 가격 분석", "📝 블로그 소셜 반응"])

# --- Tab 1: 트렌드 분석 ---
with tab1:
    st.subheader("2025년 일자별 검색 추이 비교")
    fig_trend = viz.plot_trend_comparison(trend_df)
    if fig_trend:
        st.plotly_chart(fig_trend, use_container_ Luck=True)
    
    st.markdown("---")
    st.subheader("키워드 요약 통계 (Table 1/5)")
    if not trend_df.empty:
        stats = trend_df.groupby('keyword')['ratio'].agg(['mean', 'max', 'min', 'std']).reset_index()
        stats.columns = ['키워드', '평균 비율', '최대값', '최소값', '표준편차']
        st.table(stats.style.background_gradient(cmap='Blues').format(precision=2))

# --- Tab 2: 쇼핑 & 가격 분석 ---
with tab2:
    if not shop_df.empty:
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.plotly_chart(viz.plot_price_distribution(shop_df, main_keyword), use_container_width=True)
            st.plotly_chart(viz.plot_category_share(shop_df, main_keyword), use_container_width=True)
            
        with col_right:
            st.plotly_chart(viz.plot_brand_share(shop_df, main_keyword), use_container_width=True)
            st.plotly_chart(viz.plot_brand_price_box(shop_df, main_keyword), use_container_width=True)

        st.markdown("---")
        
        # 표 구현 (Tables 2, 4, 5)
        st.subheader(f"[{main_keyword}] 시장 데이터 요약")
        
        t_col1, t_col2 = st.columns(2)
        
        with t_col1:
            st.markdown("#### 최저가 상품 TOP 10 (Table 2/5)")
            top_cheap = shop_df.sort_values('lprice').head(10)[['title', 'lprice', 'mallName']]
            top_cheap.columns = ['상품명', '최저가', '판매처']
            st.dataframe(top_cheap, use_container_width=True, hide_index=True)

            st.markdown("#### 브랜드 점유율 순위 (Table 4/5)")
            brand_rank = shop_df['brand'].value_counts().reset_index()
            brand_rank.columns = ['브랜드', '노출 빈도']
            st.dataframe(brand_rank.head(10), use_container_width=True, hide_index=True)

        with t_col2:
            st.markdown("#### 카테고리별 상품 수 및 평균가 (Table 5/5)")
            cat_stats = shop_df.groupby('category3')['lprice'].agg(['count', 'mean']).reset_index()
            cat_stats.columns = ['카테고리', '상품 수', '평균 가격']
            st.dataframe(cat_stats.sort_values('count', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.warning(f"'{main_keyword}'에 대한 쇼핑 데이터가 없습니다.")

# --- Tab 3: 블로그 소셜 반응 ---
with tab3:
    if not blog_df.empty:
        st.subheader(f"[{main_keyword}] 최신 블로그 리뷰 리스트 (Table 3/5)")
        # HTML 태그 제거 및 데이터 정리
        display_blog = blog_df[['title', 'description', 'postdate', 'bloggername', 'link']].copy()
        display_blog['title'] = display_blog['title'].str.replace('<b>', '').str.replace('</b>', '')
        display_blog.columns = ['제목', '내용 요약', '작성일', '블로거', '링크']
        st.dataframe(display_blog.head(20), use_container_width=True, hide_index=True)
        
        # 추가 시각화 (예: 작성일별 포스팅 빈도 - 보너스)
        st.markdown("---")
        st.subheader("최근 블로그 포스팅 빈도")
        blog_df['postdate'] = pd.to_datetime(blog_df['postdate'], format='%Y%m%d', errors='coerce')
        blog_date_counts = blog_df['postdate'].value_counts().sort_index().reset_index()
        blog_date_counts.columns = ['date', 'count']
        fig_blog_date = px.bar(blog_date_counts, x='date', y='count', title="일자별 블로그 발행량", template='plotly_dark')
        st.plotly_chart(fig_blog_date, use_container_width=True)
    else:
        st.warning(f"'{main_keyword}'에 대한 블로그 데이터가 없습니다.")

st.sidebar.markdown("---")
st.sidebar.write("Last Updated:", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))
