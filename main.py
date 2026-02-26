import os
import feedparser
from google import genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from jinja2 import Template
from supabase import create_client, Client  # <--- [새로 추가된 라이브러리]

load_dotenv('impormation.env') 

# ==========================================
# 1. 뉴스 수집 (기존과 동일)
# ==========================================
def get_it_news_rss():
    print("📰 구글 뉴스(IT/과학) RSS 피드를 가져옵니다...")
    url = "https://news.google.com/rss/search?q=IT+기술+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    news_list = [f"- 제목: {entry.title}" for entry in feed.entries[:5]]
    return "\n".join(news_list)

# ==========================================
# 2. AI 요약 (기존과 동일)
# ==========================================
def summarize_news_with_llm(news_text):
    print("🤖 최신 Gemini API를 호출하여 요약을 진행합니다...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ 오류: GEMINI_API_KEY를 찾을 수 없습니다."
        
    client = genai.Client(api_key=api_key)
    prompt = f"다음 IT 뉴스들을 바쁜 대학생을 위해 3가지 불릿 포인트로 요약해 줘.\n{news_text}"
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text

# ==========================================
# 3. 이메일 발송 (기존과 동일)
# ==========================================
def send_email(summary_text):
    print("📧 HTML 뉴스레터를 이메일로 발송합니다...")
    sender_email = os.getenv("SENDER_EMAIL")       
    sender_password = os.getenv("EMAIL_PASSWORD")  
    
    if not sender_email or not sender_password:
        return
        
    try:
        with open("template.html", "r", encoding="utf-8") as f:
            template_html = f.read()
    except FileNotFoundError:
        return
    
    template = Template(template_html)
    now = datetime.now().strftime("%Y년 %m월 %d일")
    html_content = template.render(date=now, summary=summary_text)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = sender_email
    msg['Subject'] = f"[일간 IT 트렌드] {now} 리포트 🤖"
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ 이메일 발송 성공!")
    except Exception as e:
        print(f"❌ 메일 발송 실패: {e}")

# ==========================================
# [NEW!] 4. Supabase DB에 저장하기
# ==========================================
def save_to_supabase(category, summary_text):
    print(f"🗄️ Supabase DB에 [{category}] 요약본을 저장합니다...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("⚠️ 환경 변수에서 Supabase URL이나 KEY를 찾을 수 없습니다.")
        return
        
    try:
        # Supabase 클라이언트 생성
        supabase: Client = create_client(url, key)
        
        # 'news_summaries' 테이블에 데이터 밀어넣기 (insert)
        data = {
            "category": category,
            "summary_text": summary_text
        }
        # execute()를 호출해야 실제로 DB에 전송됩니다.
        result = supabase.table("news_summaries").insert(data).execute()
        print("✅ DB 저장 완벽하게 성공!")
        
    except Exception as e:
        print(f"❌ DB 저장 실패: {e}")

# ==========================================
# 메인 파이프라인 실행
# ==========================================
if __name__ == "__main__":
    crawled_data = get_it_news_rss()
    
    if crawled_data:
        final_summary = summarize_news_with_llm(crawled_data)
        print("\n[LLM 요약 결과]\n", final_summary, "\n")
        
        # 1. 메일 보내기
        send_email(final_summary) 
        
        # 2. 대망의 DB 저장하기 (카테고리 이름을 'IT/과학'으로 지정)
        save_to_supabase("IT/과학", final_summary)
        
    else:
        print("뉴스를 가져오지 못했습니다.")
