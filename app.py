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

categories = {
    "경제": "📈", "사회": "👥", "생활/문화": "☕", 
    "IT/과학": "💻", "게임": "🎮", "세계": "🌍", 
    "스포츠": "⚽", "건강": "🏥", "엔터테인먼트": "🎬"
}
#딕셔너리
tabs = st.tabs([f"{icon} {cat}" for cat, icon in categories.items()])

for i, (category_name, _) in enumerate(categories.items()):
    with tabs[i]:
        st.subheader(f"오늘의 {category_name} 트렌드")
            
        # DB에서 현재 카테고리 이름과 똑같은 데이터를 꺼내옵니다.
        news_content = get_latest_news(category_name)
        st.markdown(news_content)

# 사이드바 (카카오톡 연동 안내)
with st.sidebar:
    st.header("📲 카카오톡 챗봇")
    st.write("웹사이트에 들어올 필요 없이, 카카오톡 챗봇으로 편하게 핵심 트렌드를 받아보세요!")
    
    # 1. 예쁜 링크 버튼 만들기 (본인의 채널 URL로 꼭 바꿔주세요!)
    st.link_button("💬 카카오톡 채널 추가하기", "http://pf.kakao.com/_xexbLqX")
    
    st.divider() # 구분선
    
    # 2. QR 코드 이미지 띄우기 (다운받은 이미지를 깃허브에 같이 올릴 경우)
    st.write("👇 스마트폰 카메라로 스캔하세요!")
    try:
        st.image("https://pf.kakao.com/rocket-web/web/profiles/_xexbLqX/qrcodes/image", use_column_width=True)
    except FileNotFoundError:
        st.caption("QR 코드 이미지를 준비 중입니다.")
