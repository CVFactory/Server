from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialToken, SocialApp
from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
import logging
import requests


logger = logging.getLogger(__name__)

User = get_user_model()



class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """모든 경우에 자동 회원가입 허용"""

        logger.info(f"pre_social_login 호출됨: {sociallogin}")

        if sociallogin.is_existing:
            logger.info(f"기존 계정 로그인: {sociallogin.account.user.email}")
        else:
            logger.info(f"새 계정 생성: {sociallogin.account.extra_data}")

        super().pre_social_login(request, sociallogin)

        return True

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_token(self, request, sociallogin):
        """
        OAuth 로그인 후 Access Token을 저장 또는 갱신
        """

        try:
            social_app = SocialApp.objects.get(provider="google")
            token = sociallogin.token

            if not token:
                logger.error("OAuth 응답에서 token이 없음!")
                print("OAuth 응답에서 token이 없음!")
                return

            logger.info(f"save_token 실행됨 - token: {token.token}")
            print(f"save_token 실행됨 - token: {token.token}")
        
            existing_token = SocialToken.objects.filter(
                account=sociallogin.account,
                app=social_app
            ).first()

            if existing_token:
                existing_token.token = token.token  # 토큰 값 갱신
                existing_token.save()
                logger.info(f"기존 토큰 갱신 완료: {existing_token.token}")
                print("기존 토큰 갱신 완료:", existing_token.token)
            else:
                # 새로 생성
                new_token = SocialToken.objects.create(
                    account=sociallogin.account,
                    app=social_app,
                    token=token.token,
                    token_secret=""
                )
                new_token.save()
                logger.info(f"새로운 토큰 저장 완료: {new_token.token}")
                print("새로운 토큰 저장 완료:", new_token.token)

        except ObjectDoesNotExist:
            logger.error("SocialApp (Google) 설정이 없습니다.")
            print("SocialApp (Google) 설정이 없습니다.")
            
class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """OAuth 로그인 후 호출되는 함수"""
        logger.info(f"pre_social_login 실행됨 - data: {sociallogin.account.extra_data}")
        print(f"pre_social_login 실행됨 - data: {sociallogin.account.extra_data}")

        # request를 사용하도록 수정 (예: request의 path 출력)
        logger.info(f"현재 요청 URL: {request.path}")
        print(f"현재 요청 URL: {request.path}")


        # `sociallogin.token` 확인
        if hasattr(sociallogin, "token"):
            logger.info(f"OAuth token 존재함: {sociallogin.token}")
            print(f"OAuth token 존재함: {sociallogin.token}")
        else:
            logger.error("sociallogin에 token 없음!")
            print("sociallogin에 token 없음!")
            
class MyGoogleOAuth2Adapter(GoogleOAuth2Adapter):
    def complete_login(self, request, app, token, response, **kwargs):
        logger.info(f"Google OAuth2Adapter 응답 데이터: {response}")
        print(f"Google OAuth2Adapter 응답 데이터: {response}")

        if "access_token" in response:
            token.token = response["access_token"]
            logger.info(f"강제로 access_token 설정: {token.token}")
            print(f"강제로 access_token 설정: {token.token}")
            logger.info(f"Google에서 받은 access_token: {response['access_token']}")
            print(f"Google에서 받은 access_token: {response['access_token']}")
        else:
            logger.error("Google OAuth 응답에서 access_token 없음! 직접 요청 시도")

            # 직접 Google API를 호출해서 access_token을 받아오기
            token_url = "https://oauth2.googleapis.com/token"
            payload = {
                "code": request.GET.get("code"),  # OAuth 인증 코드
                "client_id": app.client_id,
                "client_secret": app.secret,
                "redirect_uri": "http://127.0.0.1:8000/accounts/google/login/callback/",
                "grant_type": "authorization_code"
            }

            response = requests.post(token_url, data=payload)
            token_data = response.json()

            logger.info(f"🔹 Google에서 직접 받은 토큰 응답: {token_data}")
            print(f"🔹 Google에서 직접 받은 토큰 응답: {token_data}")

            if "access_token" in token_data:
                token.token = token_data["access_token"]
                logger.info(f" 직접 요청한 access_token 설정: {token.token}")
                print(f" 직접 요청한 access_token 설정: {token.token}")
            else:
                logger.error(" 직접 요청했지만 access_token을 받지 못함")
                print(" 직접 요청했지만 access_token을 받지 못함")

        return super().complete_login(request, app, token, response, **kwargs)