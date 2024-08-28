from django.contrib import admin
from django.urls import path
from analysis.views import continue_conversation, analyze_text

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/continue_conversation/', continue_conversation, name='continue_conversation'),
    path('api/analyze/', analyze_text, name='analyze_text'),
]
