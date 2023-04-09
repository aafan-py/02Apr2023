from django.shortcuts import render

def voice_campaign(request):
    return render(request, 'voice/voice_campaign.html')