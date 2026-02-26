import os
import feedparser
from google import genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from jinja2 import Template
from supabase import create_client, Client
import urllib.parse  # 검색어 변환용

load_dotenv('impormation.env') 

# 1. RSS 피드 수집 (검색어 동적 적용)
def get_news_rss(query):
    print(f"📰 구글 뉴스 검색어: [{query}] 피드를 가져옵니다...")
    # 한글 검색어가 URL에서 깨지지 않도록 인코딩
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(url)
    news_list = [f"- 제목: {entry.title}" for entry in feed.entries[:5]]
    
    if not news_list:
        return None
    return "\n".join(news_list)

# 2. AI 요약
def summarize_news_with_llm(category, news_text):
    print(f" [{category}] 분야 요약을 진행합니다...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ 오류: GEMINI_API_KEY를 찾을 수 없습니다."
        
    client = genai.Client(api_key=api_key)
    
    # 프롬프트에 '카테고리' 이름을 넣어서 더 정확한 맞춤형 요약을 유도합니다.
    prompt = f"""
    다음은 오늘 한국의 주요 [{category}] 관련 뉴스 제목들입니다.
    이 내용들을 종합하여 바쁜 대학생이 아침에 1분 만에 읽을 수 있도록, 
    가장 중요한 트렌드 3가지를 불릿 포인트로 깔끔하게 요약해 주세요.
    
    [뉴스 데이터]
    {news_text}
    """
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return response.text

# 3. DB 저장 및 이메일 발송 
def save_to_supabase(category, summary_text):
    print(f"🗄️ Supabase DB에 [{category}] 요약본 저장 중...")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        return
        
    try:
        supabase: Client = create_client(url, key)
        data = {"category": category, "summary_text": summary_text}
        supabase.table("news_summaries").insert(data).execute()
        print(f"[{category}] DB 저장 성공!")
    except Exception as e:
        print(f" DB 저장 실패: {e}")

def send_email(full_summary_html):
    print("📧 통합 HTML 뉴스레터를 발송합니다...")
    sender_email = os.getenv("SENDER_EMAIL")       
    sender_password = os.getenv("EMAIL_PASSWORD")  
    
    if not sender_email or not sender_password:
        return
        
    try:
        with open("template.html", "r", encoding="utf-8") as f:
            template_html = f.read()
            
        template = Template(template_html)
        now = datetime.now().strftime("%Y년 %m월 %d일")
        # 메일 템플릿에 전체 요약본을 꽂아 넣습니다.
        html_content = template.render(date=now, summary=full_summary_html)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = f"[일간 IT 트렌드] {now} 리포트 🤖"
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(" 이메일 발송 완료!")
    except Exception as e:
        print(f" 발송 실패: {e}")


# 4. 메인 파이프라인 (자동화 루프)
if __name__ == "__main__":
    # 우리가 원하는 카테고리와 구글 뉴스 검색어(키워드) 세팅
    target_categories = {
        "IT/과학": "IT기술 OR 인공지능 OR 반도체 OR 과학",
        "게임/e스포츠": "게임산업 OR e스포츠 OR 신작게임 OR 콘솔게임",
        "경제/주식": "거시경제 OR 주식시장 OR 기준금리 OR 금융"
    }
    
    email_content_builder = "" # 메일 한 통에 다 담기 위해 빈 텍스트 준비
    
    for category, query in target_categories.items():
        # 1. 카테고리별 수집
        crawled_data = get_news_rss(query)
        
        if crawled_data:
            # 2. 카테고리별 요약
            summary = summarize_news_with_llm(category, crawled_data)
            
            # 3. 카테고리별 DB 저장
            save_to_supabase(category, summary)
            
            # 4. 메일 내용에 추가하기 (HTML 태그로 영역 구분)
            email_content_builder += f"<h3>[{category}]</h3>\n<pre style='font-family: inherit;'>{summary}</pre>\n<hr>\n"
            
    # 모든 카테고리를 순회한 후, 하나로 합쳐진 메일 발송!
    if email_content_builder:
        send_email(email_content_builder)


