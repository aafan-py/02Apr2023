from django import forms
from django.core.exceptions import ValidationError

from accounts.models import Account, WalletCredit

class RegistrationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    is_reseller = forms.BooleanField(required=False)

    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
    }))

    email = forms.EmailField(label="Email", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
    }))

    password = forms.CharField(label="Password", widget=forms.PasswordInput(
        attrs={
        'class' : 'form-control',
        'placeholder' : 'Create Password',
    }))

    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(
        attrs={
        'class' : 'form-control',
        'placeholder' : 'Confirm Password',
    }))

    class Meta:
        model = Account
        fields = ('email', 'username')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Account.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_normalized = Account.objects.normalize_email(email)
        if Account.objects.filter(email=email_normalized).exists():
            raise ValidationError("Email already exists.")
        return email_normalized

    def clean_confirm_password(self):
        # Check that the two password entries match
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords didn't match")
        return confirm_password

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_reseller = self.cleaned_data['is_reseller']
        if commit:
            user.save()
        return user

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            'name', 'phone_number', 'company_name', 'gst_number', 'address',
            'city', 'state', 'country', 'pincode',
        )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company name',
            }),
            'gst_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your GST number',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city',
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your state',
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your country',
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your pincode',
            }),
        }

class ResellerUserForm(forms.ModelForm):

    is_reseller = forms.BooleanField(required=False)

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password',
    }))
    
    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'confirm_password', 'reseller']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
            }),   
            'reseller': forms.HiddenInput(),
        }

    def __init__(self, *args, reseller=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['reseller'].initial = reseller

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.reseller = self.fields['reseller'].initial
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Account.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_normalized = Account.objects.normalize_email(email)
        if Account.objects.filter(email=email_normalized).exists():
            raise ValidationError("Email already exists.")
        return email_normalized
    
    def clean_confirm_password(self):
        # Check that the two password entries match
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords didn't match")
        return confirm_password

class CreditDebitForm(forms.Form):
    user_id = forms.IntegerField()
    transaction_type = forms.ChoiceField(choices=WalletCredit.TRANSACTION_TYPE_CHOICES)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    remark = forms.CharField(max_length=100, required=False)

    def __init__(self, reseller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_id'].queryset = Account.objects.filter(reseller=reseller)

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            user = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            raise forms.ValidationError("Invalid user ID")
        return user_id

    # def clean_amount(self):
    #     amount = self.cleaned_data['amount']
    #     user_id = self.cleaned_data['user_id']
    #     user = Account.objects.get(id=user_id)
    #     reseller = user.reseller
    #     if self.cleaned_data['transaction_type'] == WalletCredit.TRANSACTION_TYPE_CREDIT:
    #         if amount > reseller.wallet_balance:
    #             raise forms.ValidationError("Reseller doesn't have sufficient balance to make this transaction.")
    #     elif self.cleaned_data['transaction_type'] == WalletCredit.TRANSACTION_TYPE_DEBIT:
    #         if amount <= 0:
    #             raise forms.ValidationError("Invalid amount")
    #         if amount > user.wallet_balance:
    #             raise forms.ValidationError("User doesn't have sufficient balance to make this transaction.")
    #         if amount > reseller.wallet_balance:
    #             raise forms.ValidationError("Reseller doesn't have sufficient balance to make this transaction.")
    #     return amount

