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

    이 회사는 intel로 다음과 같은 인재를 찾아.

    1. 인텔의 인재상
    인텔은 "지능적이고 열정적인 인재"를 중시합니다. 특히 다음 특성을 가진 사람을 선호합니다:

    창의성 : 문제를 새롭고 혁신적인 방식으로 해결할 수 있는 능력.
    적응력 : 빠르게 변화하는 기술 환경에서 유연하게 대처할 수 있는 태도 .
    협업 역량 : 다양한 배경과 전문성을 가진 사람들과 팀워크를 발휘할 수 있는 능력 .
    또한, 인텔은 포용적인 조직 문화를 지향하며, 모든 직원이 의미 있는 일에 몰입할 수 있도록 지원합니다 .

    2. 인텔의 비전
    인텔의 궁극적인 비전은 "세상을 변화시키는 기술을 개발해 전 인류의 삶을 개선하는 것"입니다. 이를 위해 다음과 같은 목표를 추구합니다:

    클라우드 컴퓨팅 및 데이터센터 효율성 향상: IT 자원의 활용도를 높이고 유연성을 제공하여 기술적 병목 현상을 해결하려 합니다 .
    반도체 기술 혁신: 최신 CPU 아키텍처 및 안정성을 개선하기 위한 연구를 지속적으로 수행합니다 .
    3. 해결하고자 하는 문제
    인텔은 다양한 기술적 도전 과제를 해결하기 위해 노력하고 있습니다:

    CPU 성능 및 안정성 문제 : 예를 들어, 13/14세대 코어 프로세서에서 발생한 전압 상승으로 인한 불안정성 문제를 해결하기 위해 마이크로코드 패치를 제공했습니다 .
    데이터 센터 요구 증가 : 클라우드 기반 서비스의 급격한 성장에 따라 더 효율적이고 확장 가능한 솔루션을 개발하는 것이 중요합니다 .
    4. 인텔이 찾는 인재 유형
    인텔은 위와 같은 문제를 해결할 수 있는 인재를 찾기 위해 특정 요소를 평가합니다:

    직무별 맞춤형 평가 : 각 직무마다 요구 사항이 다르기 때문에, 모든 면접 질문에 통과하지 않아도 됩니다. 네 명으로 구성된 채용팀이 후보자를 종합적으로 평가합니다 .
    열정과 실행력 : 단순히 지식만이 아닌, 실질적인 성과를 내고자 하는 의지를 가진 사람을 선호합니다.
    다양성 존중 : 다양한 배경과 경험을 가진 사람들을 환영하며, 이들의 시너지를 통해 더 큰 성과를 창출하려 합니다 .


    내가 지금까지 전달해준 정보를 토대로
    위에 올린 회사의 채용공고에 지원할 자기소개서를 써줘
    두괄식으로 해주고
    회사가 당면한 문제가 무엇이고
    그 문제를 해결하기 위해 이런 채용공고를 낸 것으로 사료된다
    내가 가진 경험과 역량으로 문제를 해결할 수 있다
    이런 식으로 써줘
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
