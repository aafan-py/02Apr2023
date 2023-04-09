from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import WhtsappCampaignForm
from django.contrib import messages
from accounts.models import ServicePlan
from whtsapp.models import WhtsappCampaign

# Create your views here.

@login_required
def whtsapp_campaign(request):
    user_id = request.user.id
    service_plans = ServicePlan.objects.filter(user=user_id)

    if request.method == "POST":
        form = WhtsappCampaignForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign Submitted Successfully!')
            return redirect("whtsapp_campaign")
    else:
        form = WhtsappCampaignForm()
    context = {
        'form':form,
        'service_plans': service_plans
    }
    return render(request, 'whtsapp/whtsapp_campaign.html', context)

def whtsapp_report(request):
    user_id =  request.user.id
    reports = WhtsappCampaign.objects.filter(user=user_id)
    context = {'reports': reports}
    return render(request, 'whtsapp/whtsapp_report.html', context)