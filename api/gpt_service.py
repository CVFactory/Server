import os
import openai
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(dotenv_path="gpt.env")

# OpenAI API 클라이언트 객체 생성
# OpenAI API Key 가져오기 (예외 처리 추가)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API Key가 설정되지 않았습니다. `.env` 파일을 확인하세요.")

try:
    # OpenAI 클라이언트 객체 생성
    client = openai.OpenAI(api_key=api_key)
except Exception as e:
    raise RuntimeError(f"OpenAI 클라이언트 생성 중 오류 발생: {str(e)}")

def generate_resume(job_description, user_story, company_info = ""):
    """
    GPT API를 호출하여 자기소개서를 생성하는 함수
    """
    prompt = f"""
    채용 공고 설명: {job_description}
    사용자의 이야기: {user_story}
    회사 정보: {company_info}

    위 정보를 바탕으로 자기소개서를 작성해주세요.
    """

    try:
        # GPT API 호출
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # 최신 OpenAI 모델 사용
            messages=[
                {"role": "system", "content": "당신은 자기소개서 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        # GPT 응답에서 한글 깨짐 방지 처리
        generated_resume = response.choices[0].message.content
        print("💡 GPT 응답 (디코딩 후):", generated_resume)  # 로그 확인

        return generated_resume

    except Exception as e:
        print("OpenAI API 호출 중 오류 발생:", str(e))
        return "GPT 응답을 생성하는 중 오류가 발생했습니다."
