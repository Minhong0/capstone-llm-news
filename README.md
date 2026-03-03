# 📰 AI Daily Trend Report (AI 일간 트렌드 리포트)

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Tech Stack](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat-square&logo=awslambda&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![KakaoTalk](https://img.shields.io/badge/KakaoTalk-FFCD00?style=flat-square&logo=kakaotalk&logoColor=black)

> **컴퓨터공학부 캡스톤 디자인 프로젝트**
> 
> 매일 아침 9개 분야의 핵심 뉴스를 AI가 요약하고, 웹 대시보드와 카카오톡 챗봇으로 자동 발행하는 **비용 제로(Zero-Cost) 서버리스 자동화 플랫폼**입니다.

<br>

## 프로젝트 개요 (Project Overview)

바쁜 현대인을 위해 매일 쏟아지는 방대한 양의 뉴스를 구글 뉴스 크롤링을 통해 수집하고, LLM(Gemini API)을 활용해 1분 만에 읽을 수 있도록 핵심만 요약하여 제공합니다. 

단순한 웹 서비스 구축을 넘어, **GitHub Actions를 이용한 자동화 스케줄링**, **AWS Lambda를 활용한 서버리스 챗봇 연동**을 통해 24시간 무중단으로 동작하면서도 유지보수 비용이 전혀 발생하지 않는 고효율 아키텍처를 설계 및 구현했습니다.

<br>

## 핵심 기능 (Key Features)

- **AI 기반 맞춤형 뉴스 요약:** 경제, IT/과학, 사회 등 총 9개 카테고리의 최신 트렌드를 AI가 읽기 쉽게 요약.
- **100% 무인 자동화 파이프라인:** GitHub Actions의 CRON 스케줄러를 통해 매일 정해진 시간에 크롤링 ➡️ 요약 ➡️ DB 적재 과정을 자동으로 수행.
- **카카오톡 챗봇 연동 (Quick Replies):** 웹사이트에 접속할 필요 없이, 카카오톡 챗봇 메뉴와 폴백(Fallback) 블록을 통해 사용자가 원하는 분야의 뉴스를 즉시 제공.
- **시각화된 웹 대시보드:** Streamlit을 활용하여 누구나 쉽게 접근하고 읽을 수 있는 반응형 프론트엔드 UI 제공.

<br>

## 시스템 아키텍처 (System Architecture)

본 프로젝트는 클라우드 네이티브 및 서버리스(Serverless) 환경을 기반으로 구축되었습니다.

```text
[ Data Pipeline ]
🌐 Google News ──(Crawling)──> 🐍 Python (GitHub Actions) ──(Summarize)──> 🧠 Gemini AI
                                         │
                                         └──(Insert)──> 🗄️ Supabase (PostgreSQL)

[ User Interface ]
👤 User ──(Access)──> 🖥️ Streamlit Web Dashboard <──(Select)── 🗄️ Supabase
👤 User ──(Message)──> 💬 Kakao i Open Builder ──(Webhook)──> ⚡ AWS Lambda <──(Select)── 🗄️ Supabase

기술 스택 (Tech Stack)
Backend & Data
Language: Python 3.12

Database: Supabase (PostgreSQL) - REST API 기반 데이터 연동

AI Model: Google Gemini API

Infrastructure & Automation
Serverless Compute: AWS Lambda, Amazon API Gateway

CI/CD & Automation: GitHub Actions (CRON Scheduler)

Frontend & Channel
Web Dashboard: Streamlit

Chatbot Platform: Kakao i Open Builder (카카오톡 오픈빌더)
