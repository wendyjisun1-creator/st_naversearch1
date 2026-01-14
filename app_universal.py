import streamlit as st
import pandas as pd
import data_manager_universal as dmu
import visualization as viz
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. 페이지 초기 설정 (Premium UI)
# ==========================================
st.set_page_config(
    page_title="Naver API Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (Glassmorphism & Gradient 스타일)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbit&family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1c2c 0%, #0e1117 100%);
    }

    /* 메트릭 카드 스타일 */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        color: #00d4ff !important;
    }
    
    /* 탭 디자인 커스텀 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px 20px;
        border-radius: 15px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 10px;
        color: #888;
        font-weight: 400;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 212, 255, 0.1);
        color: #00d4ff !important;
        font-weight: 600;
        border-bottom: 2px solid #00d4ff !important;
    }

    /* 카드형 컨테이너 */
    .premium-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
        margin-bottom: 20px;
    }
    
    h1, h2, h3 {
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 사이드바 (필터 및 설정)
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)
    st.title("Market Intel")
    st.caption("Universal Naver API Engine v2.0")
    
    st.markdown("---")
    
    # 검색 방식 선택
    search_mode = st.radio("분석 모드", ["멀티 키워드 비교", "상세 단일 분석"])
    
    if search_mode == "멀티 키워드 비교":
        user_input = st.text_input("분석 키워드 (쉼표 구분)", value="런닝화, 스마트워치")
        keywords = [k.strip() for k in user_input.split(",") if k.strip()]
    else:
        single_kw = st.text_input("분석 키워드 입력", value="갤럭시워치")
        keywords = [single_kw]

    st.markdown("---")
    st.subheader("📅 분석 기간")
    d_col1, d_col2 = st.columns(2)
    start_date = d_col1.date_input("시작일", datetime(2025, 1, 1))
    end_date = d_col2.date_input("종료일", datetime(2025, 12, 31))
    
    st.markdown("---")
    if st.button("🚀 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.caption("© 2026 Antigravity AI")

# ==========================================
# 3. 데이터 로드 로직
# ==========================================
if not keywords:
    st.warning("분석할 키워드를 입력해주세요.")
    st.stop()

# API 키 누락 체크
if not dmu.CLIENT_ID or not dmu.CLIENT_SECRET:
    st.error("API 키가 설정되지 않았습니다. .env 파일 또는 Streamlit Secrets를 확인하세요.")
    st.stop()

@st.cache_data(ttl=3600)
def load_all_dashboard_data(kws, start, end):
    with st.spinner("네이버 빅데이터 분석 중..."):
        # 트렌드 데이터
        trends = []
        for k in kws:
            df_t = dmu.fetch_shopping_trend(k, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
            if not df_t.empty:
                trends.append(df_t)
        
        trend_df = pd.concat(trends, ignore_index=True) if trends else pd.DataFrame()
        
        # 상세 데이터 (첫 번째 키워드 중심)
        main_kw = kws[0]
        shop_df = dmu.fetch_shopping_search(main_kw)
        blog_df = dmu.fetch_blog_search(main_kw)
        
        return trend_df, shop_df, blog_df

trend_df, shop_df, blog_df = load_all_dashboard_data(keywords, start_date, end_date)

# ==========================================
# 4. 메인 대시보드 화면
# ==========================================
main_kw = keywords[0]

# 상단 헤더 및 섹션
header_col1, header_col2 = st.columns([2, 1])
with header_col1:
    st.title(f"🔍 {main_kw} 및 시장 인텔리전스")
    st.markdown(f"실시간 수집 시각: `{datetime.now().strftime('%Y-%m-%d %H:%M')}`")

# 핵심 지표 (Metrics)
m_cols = st.columns(len(keywords) if len(keywords) <= 4 else 4)
if not trend_df.empty:
    for i, kw in enumerate(keywords[:4]):
        k_data = trend_df[trend_df['keyword'] == kw]
        if not k_data.empty:
            current_val = k_data.iloc[-1]['ratio']
            prev_val = k_data.iloc[-2]['ratio'] if len(k_data) > 1 else current_val
            delta = current_val - prev_val
            m_cols[i].metric(label=f"{kw} 지수", value=f"{current_val:.1f}", delta=f"{delta:.2f}")

# 탭 메뉴 구성
tab_trend, tab_shop, tab_social = st.tabs([
    "� 트렌드 분석 (Trend Analytics)", 
    "🛒 마켓 & 가격 (Market & Pricing)", 
    "💬 소셜 보이스 (Social Voice)"
])

# --- [TAB 1: 트렌드 분석] ---
with tab_trend:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("연간 검색 트렌드 타임라인")
    if not trend_df.empty:
        fig_trend = viz.plot_trend_comparison(trend_df)
        fig_trend.update_layout(height=500, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([1, 1.5])
    with col_t1:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("키워드 성과 요약 (Table 1/5)")
        if not trend_df.empty:
            stats = trend_df.groupby('keyword')['ratio'].agg(['mean', 'max', 'std']).reset_index()
            stats.columns = ['키워드', '평균 지수', '최고 피크', '변동성(STD)']
            st.table(stats.style.background_gradient(cmap='Blues').format(precision=2))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_t2:
        st.markdown('<div class="premium-card" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("트렌드 주요 변곡점 분석")
        st.info("💡 2025년 데이터 기준, 각 키워드별 최고 검색량 시점과 평균 대비 상승폭을 분석합니다.")
        # 간단한 분석 텍스트 생성
        if not trend_df.empty:
            for kw in keywords:
                max_point = trend_df[trend_df['keyword'] == kw].sort_values('ratio', ascending=False).iloc[0]
                st.write(f"- **{kw}**: `{max_point['period'].strftime('%Y-%m-%d')}`에 지수 **{max_point['ratio']:.1f}**로 정점 기록")
        st.markdown('</div>', unsafe_allow_html=True)

# --- [TAB 2: 마켓 & 가격 분석] ---
with tab_shop:
    if not shop_df.empty:
        # 그리드 레이아웃 (Graphs 1~4)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.plotly_chart(viz.plot_price_distribution(shop_df, main_kw), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.plotly_chart(viz.plot_category_share(shop_df, main_kw), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.plotly_chart(viz.plot_brand_share(shop_df, main_kw), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.plotly_chart(viz.plot_brand_price_box(shop_df, main_kw), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        
        # 테이블 섹션 (Tables 2, 4, 5)
        st.subheader("시장 상세 데이터 시트")
        tc1, tc2, tc3 = st.columns(3)
        
        with tc1:
            st.markdown("##### 최저가 리스트 TOP 10 (Table 2/5)")
            cheap_df = shop_df.sort_values('lprice').head(10)[['title', 'lprice', 'mallName']]
            cheap_df['title'] = cheap_df['title'].str.replace('<b>', '').str.replace('</b>', '')
            st.dataframe(cheap_df, use_container_width=True, hide_index=True)
            
        with tc2:
            st.markdown("##### 주요 브랜드 노출 순위 (Table 4/5)")
            brand_rank = shop_df['brand'].value_counts().reset_index().head(10)
            brand_rank.columns = ['브랜드', '노출 수']
            st.dataframe(brand_rank, use_container_width=True, hide_index=True)
            
        with tc3:
            st.markdown("##### 카테고리별 마켓 분석 (Table 5/5)")
            cat_table = shop_df.groupby('category3')['lprice'].agg(['count', 'mean']).reset_index()
            cat_table.columns = ['카테고리', '상품 수', '평균가']
            st.dataframe(cat_table.sort_values('상품 수', ascending=False), use_container_width=True, hide_index=True)
    else:
        st.error("쇼핑 상품 데이터를 로드할 수 없습니다.")

# --- [TAB 3: 소셜 보이스] ---
with tab_social:
    if not blog_df.empty:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader(f"최신 블로그 여론 리스트 (Table 3/5)")
        # 데이터 정리
        social_df = blog_df[['title', 'description', 'bloggername', 'postdate', 'link']].copy()
        social_df['title'] = social_df['title'].str.replace('<b>', '').str.replace('</b>', '')
        social_df['description'] = social_df['description'].str.replace('<b>', '').str.replace('</b>', '')
        st.dataframe(social_df.head(30), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 추가 시각화 (Area Chart)
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("블로그 포스팅 타임라인")
        blog_df['postdate'] = pd.to_datetime(blog_df['postdate'], format='%Y%m%d', errors='coerce')
        blog_timeline = blog_df['postdate'].value_counts().sort_index().reset_index()
        blog_timeline.columns = ['date', 'count']
        fig_area = px.area(blog_timeline, x='date', y='count', title="시점별 포스팅 빈도 분석",
                           template='plotly_dark', color_discrete_sequence=['#00d4ff'])
        st.plotly_chart(fig_area, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("블로그 리뷰 데이터가 없습니다.")

# 푸터
st.markdown("---")
st.caption("© 2026 Antigravity Advanced Analytics Interface. All rights reserved.")
