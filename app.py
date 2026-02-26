import streamlit as st
from supabase import create_client, Client

# 1. 페이지 기본 설정
st.set_page_config(page_title="Daily Trend AI", page_icon="📰", layout="centered")

# 2. Supabase DB 연결 

@st.cache_resource # DB 연결을 캐싱해서 사이트 속도를 높여줌
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()


# 3. DB에서 가장 최근 뉴스 꺼내오기 함수

@st.cache_data(ttl=600) # 10분마다 새로고침 (무료 서버 과부하 방지)
def get_latest_news(category):
    try:
        # DB에서 해당 카테고리의 최신 글 1개를 가져옵니다.
        response = supabase.table("news_summaries").select("*").eq("category", category).order("created_at", desc=True).limit(1).execute()
        
        if response.data:
            return response.data[0]['summary_text']
        else:
            return "아직 요약된 뉴스가 없습니다. 😅 (내일 아침을 기대해 주세요!)"
    except Exception as e:
        return f"데이터를 불러오는 중 오류가 발생했습니다: {e}"

# 4. 웹페이지 UI 구성

st.title("🚀 AI Daily Trend Report")
st.divider() 

# 탭 메뉴
tab1, tab2, tab3 = st.tabs(["💻 IT/과학", "🎮 게임/e스포츠", "📈 경제/주식"])

with tab1:
    st.subheader("오늘의 IT/과학 트렌드")
    it_news = get_latest_news("IT/과학")
    st.markdown(it_news)

with tab2:
    st.subheader("오늘의 게임/e스포츠 트렌드")
    game_news = get_latest_news("게임/e스포츠")
    st.markdown(game_news)

with tab3:
    st.subheader("오늘의 경제/주식 트렌드")
    econ_news = get_latest_news("경제/주식")
    st.markdown(econ_news)
