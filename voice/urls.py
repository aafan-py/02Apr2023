from django.urls import path
from voice import views

urlpatterns = [
    path('campaign/',views.voice_campaign,name='voice_campaign'),
]