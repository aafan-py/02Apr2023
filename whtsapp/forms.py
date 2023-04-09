from django import forms
from .models import WhtsappCampaign

class WhtsappCampaignForm(forms.ModelForm):
    class Meta:
        model = WhtsappCampaign
        fields = ['numbers', 'message', 'image1', 'image2', 'image3', 'image4', 'video', 'pdf']

    # def save(self, commit=True):
    #     campaign = super(WhtsappCampaignForm, self).save(commit=False)

    #     # Calculate the campaign cost based on the number of mobile numbers
    #     numbers = self.cleaned_data['numbers'].split('\n')
    #     count = len(numbers)
    #     campaign_cost = 0.10 * count # Assuming the rate for each number is 0.10

    #     # Deduct the campaign cost from the user's balance
    #     user = self.request.user # Assuming the user is logged in
    #     user.balance -= campaign_cost
    #     user.save()

    #     if commit:
    #         campaign.save()
    #     return campaign
