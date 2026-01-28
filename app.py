"""
새움터 일일 동향 브리핑 시스템 - Streamlit 웹앱
어디서나 브라우저로 접근 가능
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
import json
import time

from scraper import SafetyNewsScraper
from briefing_generator import BriefingGenerator


# 페이지 설정
st.set_page_config(
    page_title="새움터 일일 동향 브리핑",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #3498db;
        color: white;
        border-radius: 5px;
        padding: 0.5rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """세션 상태 초기화"""
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = None
    if 'briefing_text' not in st.session_state:
        st.session_state.briefing_text = None
    if 'collection_done' not in st.session_state:
        st.session_state.collection_done = False
    if 'briefing_done' not in st.session_state:
        st.session_state.briefing_done = False


def main():
    """메인 함수"""
    
    # 환경 변수 로드
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    # 세션 상태 초기화
    init_session_state()
    
    # 헤더
    st.markdown('<h1 class="main-header">🌟 새움터 일일 동향 브리핑</h1>', unsafe_allow_html=True)
    
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        st.subheader("데이터 수집 소스")
        
        # Playwright 가용성 체크 (scraper 모듈에서 확인)
        from scraper import PLAYWRIGHT_AVAILABLE
        
        if not PLAYWRIGHT_AVAILABLE:
            st.warning("⚠️ 일부 소스는 제한됩니다")
            st.caption("Playwright 미설치 또는 초기화 실패")
        else:
            st.success("✅ 모든 소스 사용 가능")
        
        source_moel = st.checkbox("고용노동부 보도자료", value=True)
        source_kosha = st.checkbox("산업안전포털 공지사항", value=True, 
                                  help="동적 페이지" if not PLAYWRIGHT_AVAILABLE else None)
        source_accident = st.checkbox("중대재해 발생알림", value=True,
                                     help="동적 페이지" if not PLAYWRIGHT_AVAILABLE else None)
        source_labor = st.checkbox("매일노동뉴스", value=True)
        source_bigkinds = st.checkbox("언론사 뉴스 검색", value=True,
                                     help="동적 페이지" if not PLAYWRIGHT_AVAILABLE else None)
        
        st.subheader("뉴스 검색 키워드")
        keywords = st.text_input("키워드", value="산업안전 중대재해", 
                                help="Bigkinds에서 검색할 키워드를 입력하세요")
        
        st.divider()
        
        # API 키 상태 확인
        if api_key:
            st.success("✅ API 키 설정됨")
        else:
            st.warning("⚠️ API 키 없음")
            st.info("`.env` 파일에 `ANTHROPIC_API_KEY`를 설정하세요")
        
        st.divider()
        
        # 정보
        st.caption("📅 " + datetime.now().strftime("%Y년 %m월 %d일"))
        st.caption("🕐 " + datetime.now().strftime("%H:%M:%S"))
    
    # 메인 영역
    tab1, tab2, tab3 = st.tabs(["📊 데이터 수집", "📄 브리핑 생성", "ℹ️ 도움말"])
    
    # 탭 1: 데이터 수집
    with tab1:
        st.header("📡 데이터 수집")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("선택한 소스에서 최신 안전보건 관련 정보를 수집합니다.")
        
        with col2:
            if st.button("🚀 수집 시작", type="primary", use_container_width=True):
                collect_data(source_moel, source_kosha, source_accident, 
                           source_labor, source_bigkinds, keywords)
        
        # 수집 결과 표시
        if st.session_state.collection_done and st.session_state.scraped_data:
            st.success("✅ 데이터 수집 완료!")
            
            # 요약 통계
            total = sum(len(v) for v in st.session_state.scraped_data.values())
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("총 수집", f"{total}건")
            with col2:
                st.metric("고용노동부", f"{len(st.session_state.scraped_data.get('moel_press', []))}건")
            with col3:
                st.metric("안전포털", f"{len(st.session_state.scraped_data.get('kosha_notice', []))}건")
            with col4:
                st.metric("중대재해", f"{len(st.session_state.scraped_data.get('major_accident', []))}건")
            with col5:
                st.metric("언론/뉴스", 
                        f"{len(st.session_state.scraped_data.get('labor_news', [])) + len(st.session_state.scraped_data.get('bigkinds_news', []))}건")
            
            # 상세 데이터 표시
            st.subheader("수집된 데이터")
            
            for category, items in st.session_state.scraped_data.items():
                if items:
                    with st.expander(f"📂 {get_category_name(category)} ({len(items)}건)"):
                        for i, item in enumerate(items, 1):
                            st.markdown(f"**{i}. [{item.get('date', '')}]** {item.get('title', '')}")
                            if 'link' in item:
                                st.markdown(f"🔗 [{item['link']}]({item['link']})")
                            st.divider()
    
    # 탭 2: 브리핑 생성
    with tab2:
        st.header("🤖 AI 브리핑 생성")
        
        if not st.session_state.collection_done:
            st.warning("⚠️ 먼저 데이터를 수집해주세요.")
        elif not api_key:
            st.error("❌ API 키가 설정되지 않았습니다. `.env` 파일을 확인하세요.")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info("수집된 데이터를 분석하여 안전보건 중심의 브리핑을 생성합니다.")
            
            with col2:
                if st.button("✨ 브리핑 생성", type="primary", use_container_width=True):
                    generate_briefing(api_key)
            
            # 브리핑 표시
            if st.session_state.briefing_done and st.session_state.briefing_text:
                st.success("✅ 브리핑 생성 완료!")
                
                # 브리핑 내용
                st.markdown("---")
                st.markdown(st.session_state.briefing_text)
                st.markdown("---")
                
                # 다운로드 버튼
                col1, col2 = st.columns(2)
                
                with col1:
                    today = datetime.now().strftime("%Y%m%d")
                    st.download_button(
                        label="📥 브리핑 다운로드 (Markdown)",
                        data=st.session_state.briefing_text,
                        file_name=f"briefing_{today}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col2:
                    if st.session_state.scraped_data:
                        json_data = json.dumps(st.session_state.scraped_data, 
                                             ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 원본 데이터 (JSON)",
                            data=json_data,
                            file_name=f"data_{today}.json",
                            mime="application/json",
                            use_container_width=True
                        )
    
    # 탭 3: 도움말
    with tab3:
        st.header("📖 사용 방법")
        
        st.markdown("""
        ### 1️⃣ 데이터 수집
        
        1. 왼쪽 사이드바에서 **수집할 소스 선택**
        2. 뉴스 검색 키워드 입력 (선택사항)
        3. "📊 데이터 수집" 탭에서 **"🚀 수집 시작"** 클릭
        4. 수집이 완료되면 결과를 확인
        
        ### 2️⃣ 브리핑 생성
        
        1. 데이터 수집 완료 후 **"📄 브리핑 생성"** 탭으로 이동
        2. **"✨ 브리핑 생성"** 클릭
        3. AI가 안전보건 중심으로 브리핑 생성
        4. 생성된 브리핑을 다운로드
        
        ### 💡 팁
        
        - **빠른 브리핑**: 고용노동부 + 중대재해만 선택
        - **종합 브리핑**: 모든 소스 선택
        - **키워드 예시**: 
          - `산업안전 중대재해` - 포괄적
          - `건설현장 추락사고` - 특정 업종
          - `화학물질 누출` - 특정 위험
        
        ### ⚙️ 설정 방법
        
        `.env` 파일 생성:
        ```
        ANTHROPIC_API_KEY=your_api_key_here
        ```
        
        API 키 발급: [console.anthropic.com](https://console.anthropic.com/settings/keys)
        
        ### ⚠️ 주의사항
        
        - 일부 사이트는 접속이 느리거나 불가할 수 있습니다
        - 시스템이 자동으로 건너뛰므로 걱정하지 마세요
        - 다른 소스의 데이터로도 브리핑 생성 가능합니다
        """)
        
        st.divider()
        
        st.subheader("🔧 문제 해결")
        
        with st.expander("데이터 수집이 너무 오래 걸려요"):
            st.markdown("""
            - 일부 사이트가 느릴 수 있습니다
            - 최대 20초 후 자동으로 다음 소스로 이동합니다
            - 느린 소스는 체크 해제하고 진행하세요
            """)
        
        with st.expander("API 키 오류가 발생해요"):
            st.markdown("""
            1. `.env` 파일이 프로젝트 폴더에 있는지 확인
            2. `ANTHROPIC_API_KEY=` 뒤에 실제 키가 입력되었는지 확인
            3. 앱을 재시작해보세요
            """)
        
        with st.expander("브리핑이 생성되지 않아요"):
            st.markdown("""
            - 먼저 데이터 수집이 완료되어야 합니다
            - API 키가 올바르게 설정되었는지 확인하세요
            - 수집된 데이터가 너무 적으면 브리핑이 짧을 수 있습니다
            """)


def collect_data(source_moel, source_kosha, source_accident, 
                source_labor, source_bigkinds, keywords):
    """데이터 수집 실행"""
    
    with st.spinner("🔄 데이터 수집 중..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        scraper = SafetyNewsScraper()
        sources = []
        
        if source_moel:
            sources.append('moel')
        if source_kosha:
            sources.append('kosha')
        if source_accident:
            sources.append('accident')
        if source_labor:
            sources.append('labor')
        if source_bigkinds:
            sources.append('bigkinds')
        
        total_sources = len(sources)
        
        for i, source in enumerate(sources):
            progress = (i + 1) / total_sources
            
            if source == 'moel':
                status_text.text("📄 고용노동부 보도자료 수집 중...")
                scraper.scrape_moel_press_release()
            elif source == 'kosha':
                status_text.text("📄 산업안전포털 공지사항 수집 중...")
                scraper.scrape_kosha_with_playwright()
            elif source == 'accident':
                status_text.text("🚨 중대재해 발생알림 수집 중...")
                scraper.scrape_major_accidents()
            elif source == 'labor':
                status_text.text("📰 매일노동뉴스 수집 중...")
                scraper.scrape_labor_news()
            elif source == 'bigkinds':
                status_text.text(f"🔍 뉴스 검색 중 (키워드: {keywords})...")
                scraper.search_bigkinds_news(keywords)
            
            progress_bar.progress(progress)
            time.sleep(0.5)
        
        st.session_state.scraped_data = scraper.results
        st.session_state.collection_done = True
        
        progress_bar.progress(1.0)
        status_text.text("✅ 수집 완료!")


def generate_briefing(api_key):
    """브리핑 생성 실행"""
    
    with st.spinner("🤖 AI 브리핑 생성 중... (30초~1분 소요)"):
        try:
            generator = BriefingGenerator(api_key)
            briefing = generator.generate_briefing(st.session_state.scraped_data)
            
            if briefing:
                st.session_state.briefing_text = briefing
                st.session_state.briefing_done = True
            else:
                st.error("❌ 브리핑 생성에 실패했습니다.")
                
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")


def get_category_name(category):
    """카테고리 이름 변환"""
    names = {
        'moel_press': '고용노동부 보도자료',
        'kosha_notice': '산업안전포털 공지사항',
        'major_accident': '중대재해 발생알림',
        'labor_news': '매일노동뉴스',
        'bigkinds_news': '언론사 뉴스'
    }
    return names.get(category, category)


if __name__ == "__main__":
    main()
