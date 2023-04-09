


"""
there's even glitch in the below credit_debit view, I created a superuser [id '1'] from terminal and created superadmi [id '2'] from user end linked to superuser [id '1'] I credited 1000 credit in superuser from django admin panel and then I logged in the superuser from cleint end and credit the same to superadmin it works and superuser now has 0 credit and superadmin has 1000 credit, now when I again try to debit the same 1000 credit it says insuffecient balance, then I debited 500 it gets debited after that I created one more reseller [id '3'] linked to superuser [id '1'] and when I credited 500 to reseller superuser was having 500 and now it was 0 but reseller got 1000 credit

Please check the logic once again and correct it, also do add one more check if the user is inactive the transaction should not happen and it should say "User is inactive"
"""

# @login_required(login_url="signin")
# def credit_debit(request):
#     reseller = request.user
#     try:
#         reseller = Account.objects.get(id=reseller.id)
#     except Account.DoesNotExist:
#         return HttpResponseBadRequest("Invalid reseller ID")

#     users = Account.objects.filter(reseller=reseller)

#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')  # Get user ID from POST data
#         try:
#             user = Account.objects.get(id=user_id, reseller=reseller)
#         except Account.DoesNotExist:
#             return HttpResponseBadRequest("Invalid user ID")

#         form = CreditDebitForm(reseller=reseller, data=request.POST)

#         if form.is_valid():
#             wallet_credit = WalletCredit.objects.filter(user=user).last()
#             amount = form.cleaned_data['amount']
#             remark = form.cleaned_data['remark']
#             if 'credit' in request.POST:
#                 if reseller.wallet_balance >= amount:
#                     wallet_credit = WalletCredit.objects.filter(user=user).last()
#                     if wallet_credit:
#                         wallet_credit.wallet_balance += amount
#                         wallet_credit.remark = remark
#                         wallet_credit.save()
#                     else:
#                         wallet_credit = WalletCredit.objects.create(
#                             user=user,
#                             wallet_balance=amount,
#                             remark=remark
#                         )
#                     user.wallet_balance += amount
#                     user.save()
#                     reseller.wallet_balance -= amount
#                     reseller.save()
#                     messages.success(request, f"{wallet_credit} is Wallet Credited with INR {amount}")
#                     return redirect(reverse('manage_users'))
#                 else:
#                     messages.error(request, 'Insufficient balance in reseller account')

#             elif 'debit' in request.POST:
#                 if wallet_credit:
#                     wallet_balance = wallet_credit.wallet_balance
#                 else:
#                     wallet_balance = 0

#                 if wallet_balance >= amount:
#                     wallet_credit.wallet_balance = wallet_balance - amount
#                     wallet_credit.remark = remark
#                     wallet_credit.save()
#                     user.wallet_balance -= amount
#                     user.save()
#                     reseller.wallet_balance += amount
#                     reseller.save()
#                     messages.success(request, f"{wallet_credit} is Wallet Debited with INR {amount}")
#                 else:
#                     messages.error(request, 'Insufficient balance in user account')
#                 return redirect(reverse('manage_users'))

#     else:
#         form = CreditDebitForm(reseller=reseller)

#     context={'user': None,
#             'users':users,
#             'wallet_credit': None,
#             'form': form,
#             'reseller': reseller
#     }
#     return render(request, 'usermanagement/credit_debit.html', context)

"""LOGIN NEW 04:09"""

# @login_required(login_url="signin")
# def credit_debit(request):
#     reseller = request.user
#     try:
#         reseller = Account.objects.get(id=reseller.id)
#     except Account.DoesNotExist:
#         return HttpResponseBadRequest("Invalid reseller ID")

#     if not reseller.is_active:
#         messages.error(request, 'Reseller is inactive')
#         return redirect(reverse('manage_users'))

#     users = Account.objects.filter(reseller=reseller)

#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')  # Get user ID from POST data
#         try:
#             user = Account.objects.get(id=user_id, reseller=reseller)
#         except Account.DoesNotExist:
#             return HttpResponseBadRequest("Invalid user ID")
        
#         if not user.is_active:
#             messages.error(request, 'User is inactive')
#             return redirect(reverse('manage_users'))

#         form = CreditDebitForm(reseller=reseller, data=request.POST)

#         if form.is_valid():
#             wallet_credit = WalletCredit.objects.filter(user=user)
#             amount = form.cleaned_data['amount']
#             remark = form.cleaned_data['remark']
#             if 'credit' in request.POST:
#                 if reseller.wallet_balance >= amount:
#                     wallet_credit = WalletCredit.objects.get(user=user)
#                     if wallet_credit:
#                         wallet_credit.wallet_balance += amount
#                         wallet_credit.remark = remark
#                         wallet_credit.save()
#                     else:
#                         wallet_credit = WalletCredit.objects.create(
#                             user=user,
#                             wallet_balance=amount,
#                             remark=remark
#                         )
#                     user.wallet_balance += amount
#                     user.save()
#                     reseller.wallet_balance -= amount
#                     reseller.save()
#                     messages.success(request, f"{wallet_credit} is Wallet Credited with INR {amount}")
#                     return redirect(reverse('manage_users'))
#                 else:
#                     messages.error(request, 'Insufficient balance in reseller account')

#             elif 'debit' in request.POST:
#                 wallet_credits = WalletCredit.objects.filter(user=user)
#                 wallet_balance = sum(credit.wallet_balance for credit in wallet_credits)

#                 if wallet_balance >= amount:
#                     wallet_credit = WalletCredit.objects.create(
#                         user=user,
#                         wallet_balance=wallet_balance - amount,
#                         remark=remark
#                     )
#                     user.wallet_balance -= amount
#                     user.save()
#                     reseller.wallet_balance += amount
#                     reseller.save()
#                     messages.success(request, f"{wallet_credit} is Wallet Debited with INR {amount}")
#                 else:
#                     messages.error(request, 'Insufficient balance in user account')
#                 return redirect(reverse('manage_users'))

#     else:
#         form = CreditDebitForm(reseller=reseller)

#     context={'user': None,
#             'users':users,
#             'wallet_credit': None,
#             'form': form,
#             'reseller': reseller,
#     }
#     return render(request, 'usermanagement/credit_debit.html', context)

if 'credit' in request.POST:
    wallet_credit, created = WalletCredit.objects.get_or_create(user=user)
    wallet_credit.wallet_balance += amount
    wallet_credit.remark = remark
    wallet_credit.save()
    
    user.wallet_balance += amount
    user.save()
    reseller.wallet_balance -= amount
    wallet_credit.credit_on = timezone.now()
    reseller.save()
    
    messages.success(request, f"Wallet Credited with INR {amount}")
    return redirect(reverse('manage_users'))
