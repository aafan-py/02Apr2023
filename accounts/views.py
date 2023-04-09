from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

# Used in forgot password
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from django.contrib import auth, messages
from django.core.mail import EmailMessage

from accounts.models import Account, WalletCredit
from accounts.forms import RegistrationForm, AccountUpdateForm, ResellerUserForm, CreditDebitForm

@login_required
def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            is_reseller = form.cleaned_data.get('is_reseller')

            user = Account.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_reseller=is_reseller,
            )
            user.save()

            messages.success(
                request, 'Congratulations! Registered Successfully')
            return render(request, 'accounts/signin.html')

    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

def signin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        # Check if user exists and is active
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, 'Invalid login credentials')
            return render(request, 'accounts/signin.html')

        if not user.is_active:
            messages.error(request, 'Your account is inactive.')
            return render(request, 'accounts/signin.html')

        # Authenticate user
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid login credentials')
            return render(request, 'accounts/signin.html')
    else:
        return render(request, 'accounts/signin.html')

@login_required
def logout(request):
    auth.logout(request)
    messages.success(request=request, message='Logged out')
    return redirect('signin')


def forgotpassword(request):
    if request.method == "POST":
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()
            messages.success(
                request, 'Password reset email has been sent to your email address')
            return redirect('signin')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please enter your new password")
        return redirect('resetpassword')
    else:
        messages.error(request, "This link has been expired")
        return redirect('signin')


def resetpassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successfully")
            return redirect('signin')
        else:
            messages.error(request, 'Password do not match')
            return redirect('resetpassword')
    else:
        return render(request, "accounts/resetpassword.html")

@login_required
def changepassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # check if the current password is correct
        if request.user.check_password(password):
            # check if the new password matches the confirm password
            if new_password == confirm_password:
                # set the new password
                request.user.set_password(new_password)
                request.user.save()
                messages.success(
                    request, 'Your password was successfully updated!')
                return redirect('signin')
            else:
                messages.error(request, 'New passwords do not match.')
                return redirect('myprofile')
        else:
            messages.error(
                request, 'Your current password was entered incorrectly.')
            return redirect('myprofile')
    return render(request, 'accounts/myprofile.html')


@login_required
def updateprofile(request):
    user_profile = request.user
    if request.method == 'POST':
        form = AccountUpdateForm(
            request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request=request, message='Profile updated!')
            return redirect('myprofile')
        else:
            messages.error(request=request, message='Something went wrong!')
    else:
        form = AccountUpdateForm(instance=user_profile)

    context = {'form': form, }

    return render(request, 'accounts/updateprofile.html', context)


@login_required
def myprofile(request):
    try:
        userprofile = Account.objects.get(email=request.user.email)
    except Account.DoesNotExist:
        userprofile = None

    if userprofile is None:
        userprofile = Account.objects.create(email=request.user.email)

    if request.method == 'POST':
        form = AccountUpdateForm(
            request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save()
            return redirect('myprofile')
    else:
        form = AccountUpdateForm(instance=userprofile)

    context = {'form': form, 'userprofile': userprofile}
    return render(request, 'accounts/myprofile.html', context)


@login_required(login_url="signin")
def register_reseller_end_user(request):
    reseller = request.user
    try:
        reseller = Account.objects.get(id=reseller.id)
    except Account.DoesNotExist:
        return HttpResponseBadRequest("Invalid reseller ID")

    if request.method == 'POST':
        form = ResellerUserForm(request.POST, reseller=reseller)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.is_reseller = form.cleaned_data.get('is_reseller')
            user.reseller = reseller  # Associate user with the reseller
            user.save()
            form.save_m2m()
            if user.is_reseller == True:
                messages.success(request, 'Reseller created successfully!')
                return redirect(reverse('manage_users'))
            else:
                messages.success(request, 'User created successfully!')
                return redirect(reverse('manage_users'))
    else:
        form = ResellerUserForm(reseller=reseller)
    context = {'form': form, 'reseller': reseller}
    return render(request, 'accounts/register_user.html', context)

@login_required(login_url="signin")
def manage_users(request):
    # Retrieve the reseller object from the session data
    reseller = request.user
    if not reseller.is_reseller:
        return HttpResponseForbidden()

    # Retrieve the list of users associated with the reseller
    users = Account.objects.filter(reseller=reseller).order_by('-date_joined')

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        users = users.filter(Q(username__icontains=search_query))

    # Pagination logic
    page_number = request.GET.get('page_number', 1)
    users_per_page = 5
    paginator = Paginator(users, users_per_page)
    try:
        users = paginator.page(page_number)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    # Construct the context dictionary and render the template
    context = {'reseller': reseller, 'users': users}
    return render(request, 'usermanagement/manage_users.html', context)

@login_required(login_url="signin")
def credit_debit(request):
    reseller_id = request.user.id
    try:
        reseller = Account.objects.get(id=reseller_id)
    except Account.DoesNotExist:
        messages.error(request, "Invalid reseller ID")
        return redirect(reverse("manage_users"))

    if not reseller.is_active:
        messages.error(request, "Reseller is inactive")
        return redirect(reverse("manage_users"))

    users = Account.objects.filter(reseller=reseller_id)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            user = Account.objects.get(id=user_id, reseller=reseller_id)
        except Account.DoesNotExist:
            messages.error(request, "Invalid user ID")
            return redirect(reverse("manage_users"))

        if not user.is_active:
            messages.error(request, "User is inactive")
            return redirect(reverse("manage_users"))

        form = CreditDebitForm(reseller=reseller, data=request.POST)

        if form.is_valid():
            amount = form.cleaned_data["amount"]
            remark = form.cleaned_data["remark"]
            transaction_type = form.cleaned_data["transaction_type"]

            wallet_credits = WalletCredit.objects.filter(
                user=user).order_by('-created_at')
            wallet_balance = wallet_credits.first().wallet_balance if wallet_credits else 0

            if transaction_type == 'credit':
                if amount > reseller.wallet_balance:
                    messages.error(request, "Your account doesn't have sufficient balance to perform credit.")
                    return redirect(reverse('credit_debit'))

                updated_wallet_balance = wallet_balance + amount

                wallet_credit = WalletCredit.objects.create(
                    user=user,
                    created_at=timezone.now(),
                    wallet_balance=updated_wallet_balance,
                    amount=amount,
                    transaction_type=transaction_type,
                    credit_on=timezone.now(),
                    remark=remark
                )
                wallet_credit.save()

                reseller.wallet_balance -= amount
                reseller.save()

                messages.success(
                    request, f"Wallet of {user} is credited with INR {amount}")
                return redirect(reverse('manage_users'))

            elif transaction_type == 'debit':
                if amount <= 0:
                    messages.error(request, "Amount must be greater than 0.")
                    return redirect(reverse('credit_debit'))

                if amount > wallet_balance:
                    messages.error(request, 'User does not have sufficient balance to perform debit.')
                    return redirect(reverse('credit_debit'))

                wallet_credit = WalletCredit.objects.create(
                    user=user,
                    created_at=timezone.now(),
                    wallet_balance=wallet_balance - amount,
                    amount=amount,
                    transaction_type=transaction_type,
                    debit_on=timezone.now(),
                    remark=remark
                )
                wallet_credit.save()

                reseller.wallet_balance += amount
                reseller.save()

                user.wallet_balance = wallet_balance - amount
                user.save()

                messages.warning(
                    request, f"Wallet of {user} is debited with INR {amount}")
                return redirect(reverse('manage_users'))

            else:
                messages.error(request, "Invalid request")
                return redirect(reverse('credit_debit'))

        else:
            messages.error(request, "Form is invalid.")
            return redirect(reverse('credit_debit'))

    else:
        form = CreditDebitForm(reseller=reseller)

    context = {
        "users": users,
        "form": form,
        "reseller": reseller,
    }
    return render(request, "usermanagement/credit_debit.html", context)


def credit_history(request):
    user_id = request.user.id
    try:
        user = get_object_or_404(Account, id=user_id)
    except Account.DoesNotExist:
        messages.error(request, "Invalid user ID")
        return redirect(reverse("manage_users"))

    credits_debits = WalletCredit.objects.filter(
        user=user).order_by('-created_at')
    form = CreditDebitForm(reseller=user.reseller)
    context = {'user': user, 'credits_debits': credits_debits, 'form': form}
    return render(request, 'usermanagement/credit_history.html', context)


@login_required(login_url="signin")
def login_as_user(request, user_id):
    # Retrieve the target user object with the given ID
    user = Account.objects.get(id=user_id)

    # Check if the logged-in account is authorized to access the target user account
    if not is_authorized(request.user, user):
        messages.warning(request, "Invalid user access")
        return redirect("manage_users")

    # Log in the reseller as the selected user
    login(request, user)

    # Redirect to the user dashboard
    return redirect('index')

def is_authorized(request_account, target_account):
    # Check if the request account is the target account or a parent account of the target account
    if request_account == target_account:
        return True
    elif target_account.reseller is None:
        return False
    else:
        return is_authorized(request_account, target_account.reseller)

def update_user_status(request, user_id):
    if request.method == 'POST':
        user = Account.objects.get(id=user_id)
        user.is_active = not user.is_active  # toggle the status
        user.save()
    return redirect('manage_users')
