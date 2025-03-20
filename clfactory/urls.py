"""
URL configuration for clfactory project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
            
     
class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"

    def get(self, request, *args, **kwargs):
        """GET 요청도 POST 요청과 동일하게 처리하도록 수정"""
        response = self.post(request, *args, **kwargs)

        user = request.user

        if user.is_authenticated:
            try:
                social_account = SocialAccount.objects.get(user=user, provider="google")
                social_app = SocialApp.objects.get(provider="google")
                token, created = SocialToken.objects.get_or_create(account=social_account, app=social_app)

                if created:
                    print("새로운 OAuth 토큰 저장됨")
                else:
                    print("기존 OAuth 토큰 업데이트됨")
            except Exception as e:
                print(f"OAuth 토큰 저장 실패: {str(e)}")

        return response


    
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),  
    path("api/auth/google/", GoogleLoginView.as_view(), name="google_login"),  # Google OAuth 추가
    path("", TemplateView.as_view(template_name="index.html")),
]
