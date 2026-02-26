import os
import feedparser
from google import genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from jinja2 import Template

load_dotenv('impormation.env') #.env 파일 로드 (환경 변수 강제 주입)

# ==========================================
# 1. 안정적인 RSS 피드 기반 뉴스 수집
# ==========================================
def get_it_news_rss():
    print("📰 구글 뉴스(IT/과학) RSS 피드를 가져옵니다...")
    url = "https://news.google.com/rss/search?q=IT+기술+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(url)
    news_list = []
    
    for entry in feed.entries[:5]:
        news_list.append(f"- 제목: {entry.title}")
        
    return "\n".join(news_list)

# ==========================================
# 2. 최신 SDK(google.genai)를 이용한 요약
# ==========================================
def summarize_news_with_llm(news_text):
    print("🤖 최신 Gemini API를 호출하여 요약을 진행합니다...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    # 디버깅용: 키가 제대로 읽혔는지 확인 (보안상 앞 5자리만 출력)
    if api_key:
        print(f"   -> API Key 인식 성공: {api_key[:5]}...")
    else:
        return "❌ 오류: .env 파일에서 GEMINI_API_KEY를 찾을 수 없습니다."
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    다음은 오늘 한국의 주요 IT 뉴스 제목들입니다.
    이 내용들을 종합하여 바쁜 대학생이 아침에 1분 만에 읽을 수 있도록, 
    가장 중요한 IT 트렌드 3가지를 불릿 포인트로 깔끔하게 요약해 주세요.
    
    [뉴스 데이터]
    {news_text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    
    return response.text

# ==========================================
# 3. 요약 결과를 이메일로 발송
# ==========================================
def send_email(summary_text):
    print("📧 요약된 뉴스를 이메일로 발송합니다...")
    
    sender_email = os.getenv("SENDER_EMAIL")       
    sender_password = os.getenv("EMAIL_PASSWORD")  
    receiver_email = sender_email # 테스트용: 나에게 보내기
    
    if not sender_email or not sender_password:
        print("⚠️ .env 파일에서 이메일 정보를 찾을 수 없습니다.")
        return
        
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "[일간 IT 트렌드] 오늘의 핵심 뉴스 요약 봇 🤖"
    
    msg.attach(MIMEText(summary_text, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ 이메일 발송 성공! 메일함을 확인해 보세요.")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")

# ==========================================
# 메인 파이프라인 실행
# ==========================================
if __name__ == "__main__":
    # 1. RSS 뉴스 수집
    crawled_data = get_it_news_rss()
    
    if crawled_data:
        # 2. AI 요약 (기존과 동일)
        final_summary = summarize_news_with_llm(crawled_data)
        print("\n[LLM 요약 결과]\n", final_summary, "\n")
        
        # 3. 드디어! 업그레이드된 HTML 이메일 발송 함수 호출
        # (이 함수 내부에서 template.html을 읽어서 처리하게 됩니다)
        send_email(final_summary) 
        
    else:
        print("뉴스를 가져오지 못했습니다.")
def send_email(summary_text):
    print("📧 HTML 뉴스레터를 이메일로 발송합니다...")
    
    sender_email = os.getenv("SENDER_EMAIL")       
    sender_password = os.getenv("EMAIL_PASSWORD")  
    receiver_email = sender_email 
    
    if not sender_email or not sender_password:
        return
        
    # 1. HTML 템플릿 읽기
    with open("template.html", "r", encoding="utf-8") as f:
        template_html = f.read()
    
    # 2. Jinja2를 이용해 데이터 매핑
    template = Template(template_html)
    now = datetime.now().strftime("%Y년 %m월 %d일")
    html_content = template.render(date=now, summary=summary_text)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"[일간 IT 트렌드] {now} 리포트 🤖"
    
    # 중요: plain 대신 'html'로 설정하여 발송
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ HTML 뉴스레터 발송 성공!")
    except Exception as e:
        print(f"❌ 발송 실패: {e}")

