import os
import feedparser
from google import genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from jinja2 import Template

load_dotenv('impormation.env') 

# RSS 피드 기반 데이터 수집
def get_it_news_rss():
    print("📰 구글 뉴스(IT/과학) RSS 피드를 가져옵니다...")
    url = "https://news.google.com/rss/search?q=IT+기술+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(url)
    news_list = []
    
    for entry in feed.entries[:5]:
        news_list.append(f"- 제목: {entry.title}")
        
    return "\n".join(news_list)

# 최신 SDK GEminiAPI 호출
def summarize_news_with_llm(news_text):
    print("최신 Gemini API를 호출하여 요약을 진행합니다...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"   -> API Key 인식 성공: {api_key[:5]}...")
    else:
        return " 오류: 환경 변수에서 GEMINI_API_KEY를 찾을 수 없습니다."
        
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

# 3. 요약 결과를 HTML 형태로 이메일 발송
def send_email(summary_text):
    print("HTML 뉴스레터를 이메일로 발송합니다...")
    
    sender_email = os.getenv("SENDER_EMAIL")       
    sender_password = os.getenv("EMAIL_PASSWORD")  
    receiver_email = sender_email 
    
    if not sender_email or not sender_password:
        print("⚠️ 환경 변수에서 이메일 정보를 찾을 수 없습니다.")
        return
        
    # 1. HTML 템플릿 읽기
    try:
        with open("template.html",행
if __name__ == "__main__":
    crawled_data = get_it_news_rss()
    
    if crawled_data:
        final_summary = summarize_news_with_llm(crawled_data)
        print("\n[LLM 요약 결과]\n", final_summary, "\n")
        
        # 이제 여기서 제대로 된 새 HTML 버전을 호출합니다!
        send_email(final_summary) 
        
    else:
        print("뉴스를 가져오지 못했습니다.")

