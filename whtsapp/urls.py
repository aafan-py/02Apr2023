from django.urls import path
from whtsapp import views

urlpatterns = [
    path('campaign/',views.whtsapp_campaign,name='whtsapp_campaign'),
    path('report/',views.whtsapp_report,name='whtsapp_report'),
]