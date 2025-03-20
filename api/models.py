from django.db import models

class Resume(models.Model):
    recruitment_notice_url = models.URLField()  # 채용공고 URL (필수)
    target_company_url = models.URLField(null=True, blank=True)  # 목표 회사 공식 사이트 URL (기존 job_url_2) #필수값 아님
    job_description = models.TextField()  # 크롤링한 채용 정보
    company_info = models.TextField(null=True, blank=True) # 회사 정보 크롤링 결과
    user_story = models.TextField()  # 사용자가 입력한 자기 이야기
    generated_resume = models.TextField()  # GPT가 생성한 자기소개서
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 날짜
  
    def __str__(self):
        return f"Resume {self.id} - {self.recruitment_notice_url}"
