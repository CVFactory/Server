import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
import pandas as pd
import logging
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # 로그 형식
    handlers=[
        logging.StreamHandler()  # 콘솔에 로그 출력
    ]
)

logger = logging.getLogger(__name__)  # 현재 모듈(__name__)에 대한 로거 생성

# ------------------------------
# 1. 설정 (키워드 & 깊이 & 필터링)
# ------------------------------
max_depth = 2  # 크롤링 깊이 2로 제한
visited_urls = set()  # 방문한 URL 저장

# 크롤링 제외할 URL 패턴
EXCLUDE_URLS = [
    "login", "signin", "signup", "register", "user", "account", "profile",
    "password", "mypage", "session", "search", "apply", "cart", "recruit",
    "faq", "help", "terms", "privacy", "support", "subsid", "policy",
    "guide", "myform", "email", "phoneBook", "process", "return",
    "로그인", "회원가입", "비밀번호", "계정", "아이디", "고객센터",
    "문의", "이용약관", "개인정보처리방침", "약관", "법적고지", "자주 묻는 질문",
    "도움말", "지원하기", "채용 공고", "채용 절차", "이메일 문의",
    "채용 FAQ", "온라인 문의", "자주 하는 질문", "연락처"
]

# 크롤링할 주요 URL 패턴
TARGET_KEYWORDS = [
    "about", "vision", "mission", "values", "culture", "philosophy",
    "our-story", "who-we-are", "strategy", "sustainability", "esg",
    "corporate", "ethics", "principles", "history", "leadership",
    "careers", "people", "insight", "story", "team", "life",
    "company", "identity", "responsibility", "commitment",
    "work", "growth", "innovation", "environment", "future",
    "비전", "미션", "핵심가치", "철학", "가치", "목표", "전략",
    "비전선언문", "기업소개", "윤리", "기업 윤리", "사회적 책임",
    "지속 가능성", "환경", "윤리 강령", "리더십", "성장", "혁신",
    "기업문화", "조직문화", "근무 환경", "일하는 방식", "기업가정신",
    "팀워크", "경영이념", "인재상", "핵심 인재", "조직문화",
    "채용 철학", "일하기 좋은 회사", "우리의 가치"
]

# 크롤링 후 제거할 단어 목록
EXCLUDE_WORDS = [
    "로그인", "아이디", "비밀번호", "회원가입", "검색", "채용공고",
    "지원하기", "인재 등록", "공고", "상시지원", "채용 안내"
]

# ------------------------------
# 2. CSRF 획득득
# ------------------------------
def get_csrf_token_and_session_id():
    """ Selenium을 이용해 CSRF 토큰과 세션 ID를 가져오기 """
    try:
        driver.get("http://127.0.0.1:8000/")
        time.sleep(2)

        csrf_token = driver.execute_script("return document.cookie.match(/csrftoken=([^;]+)/)?.[1]")
        session_id = driver.execute_script("return document.cookie.match(/sessionid=([^;]+)/)?.[1]")

        if not csrf_token or not session_id:
            logger.error(" CSRF 토큰 또는 세션 ID를 가져오지 못했습니다.")
            return None, None

        logger.info(f" 가져온 CSRF 토큰: {csrf_token}")
        logger.info(f" 가져온 세션 ID: {session_id}")

        return csrf_token, session_id

    except Exception as e:
        logger.error(f" CSRF 토큰 및 세션 ID 가져오기 실패: {str(e)}")
        return None, None
    
# ------------------------------
# 3. Selenium 설정
# ------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(ChromeDriverManager().install())

# 전역적으로 Selenium WebDriver 인스턴스 관리
driver = webdriver.Chrome(service=service, options=chrome_options)

# ------------------------------
# 4. 정적/동적 페이지 감지
# ------------------------------
def detect_page_type(url):
    """ 페이지 유형 감지: 정적(static) 또는 동적(dynamic) """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            html = response.text
            if html.count("<script") > 5:
                return "dynamic"
            return "static"
    except requests.exceptions.RequestException:
        return "dynamic"
    return "static"

# ------------------------------
# 5. 불필요한 문장 제거
# ------------------------------
def clean_text(text):
    """ 불필요한 문구 제거 및 정제 """
    return "\n".join([line.strip() for line in text.split("\n") if len(line.strip()) > 20])

# ------------------------------
# 6. 정적 페이지 크롤링
# ------------------------------
def crawl_static(url):
    """ 정적 페이지에서 텍스트 추출 """
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return clean_text(text)
    except requests.exceptions.RequestException:
        return ""

# ------------------------------
# 7. 동적 페이지 크롤링
# ------------------------------
def crawl_dynamic(url):
    """ 동적 페이지에서 Selenium을 사용하여 텍스트 추출 """
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    text = soup.get_text(separator=" ", strip=True)
    return clean_text(text)

# ------------------------------
# 8. 재귀 크롤링 함수
# ------------------------------
def recursive_crawl(url, depth=1, max_depth=2, visited_urls=set()):
    """ 회사 홈페이지에서 관련 페이지까지 크롤링 """
    if url in visited_urls or depth > max_depth:
        return ""

    visited_urls.add(url)

    page_type = detect_page_type(url)
    if page_type == "static":
        page_text = crawl_static(url)
    else:
        page_text = crawl_dynamic(url)

    if depth == max_depth:
        return page_text  # 최대 깊이 도달 시 반환

    # 추가 크롤링 수행
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    for link in soup.find_all("a", href=True):
        sub_url = link["href"]

        if sub_url.startswith("/"):
            sub_url = url.rstrip("/") + sub_url

        return page_text + "\n" + recursive_crawl(sub_url, depth + 1, max_depth, visited_urls)

    return page_text

# ------------------------------
# 9. csrftoken과 sessionid 획득
# ------------------------------
def get_csrf_token_and_session_id():
    """ Selenium을 이용해 CSRF 토큰과 세션 ID를 가져오기 """
    try:
        logger.info("CSRF 토큰 및 세션 ID 가져오는 중...")
        
        driver.get("http://127.0.0.1:8000/")
        time.sleep(3)  # 페이지 로드 대기

        csrf_token = None
        session_id = None

        # 쿠키에서 CSRF 토큰과 세션 ID 가져오기
        for cookie in driver.get_cookies():
            if cookie["name"] == "csrftoken":
                csrf_token = cookie["value"]
            if cookie["name"] == "sessionid":
                session_id = cookie["value"]

        if not csrf_token or not session_id:
            logger.error("CSRF 토큰 또는 세션 ID를 가져오지 못했습니다.")
            return None, None

        logger.info(f"CSRF 토큰: {csrf_token}")
        logger.info(f"세션 ID: {session_id}")

        return csrf_token, session_id

    except Exception as e:
        logger.error(f"CSRF 토큰 및 세션 ID 가져오기 실패: {str(e)}")
        return None, None


# ------------------------------
# 10. 크롤링 실행
# ------------------------------

def fetch_company_info(company_url):
    """ 회사 정보를 크롤링하는 함수 """
    try:
        logger.info(f" 회사 정보 크롤링 시작: {company_url}")

        # CSRF 토큰 및 세션 ID 가져오기
        csrf_token, session_id = get_csrf_token_and_session_id()
        if not csrf_token or not session_id:
            logger.error("CSRF 토큰 또는 세션 ID를 가져오지 못해 요청이 실패했습니다.")
            return "(회사 정보 크롤링 실패 - CSRF 오류)"

        # 요청 헤더 설정 (CSRF 및 세션 추가)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "X-CSRFToken": csrf_token,  
            "Cookie": f"csrftoken={csrf_token}; sessionid={session_id}",  
            "Referer": "http://127.0.0.1:8000/"  
        }

        response = requests.get(company_url, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.error(f"HTTP 요청 실패: {response.status_code}")
            return "(회사 정보 크롤링 실패 - HTTP 오류)"

        return response.text[:1000]  # 응답 데이터 일부만 반환

    except Exception as e:
        logger.error(f" 크롤링 중 오류 발생: {str(e)}")
        return "(회사 정보 크롤링 실패)"
