from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialToken, SocialApp
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        """모든 경우에 자동 회원가입 허용"""
        return True

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_token(self, request, sociallogin):
        """
        OAuth 로그인 후 Access Token을 저장 또는 갱신
        """
        try:
            social_app = SocialApp.objects.get(provider="google")
            token = sociallogin.token

            if token:
                # 기존 토큰 확인
                existing_token = SocialToken.objects.filter(
                    account=sociallogin.account,
                    app=social_app
                ).first()

                if existing_token:
                    existing_token.token = token.token  # 토큰 값 갱신
                    existing_token.save()
                    print(" 기존 토큰 갱신 완료:", existing_token.token)
                else:
                    # 새로 생성
                    new_token = SocialToken.objects.create(
                        account=sociallogin.account,
                        app=social_app,
                        token=token.token,
                        token_secret=token.token_secret
                    )
                    new_token.save()
                    print(" 새로운 토큰 저장 완료:", new_token.token)

        except ObjectDoesNotExist:
            print(" SocialApp (Google) 설정이 없습니다.")