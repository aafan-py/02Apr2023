from django.urls import path
from accounts import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('register_user/', views.register_reseller_end_user, name='register_user'),
    path('signin/',views.signin,name='signin'),
    path('logout/',views.logout,name='logout'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
    path('updateprofile/', views.updateprofile, name='updateprofile'),
    path('myprofile/', views.myprofile, name='myprofile'),
    path('changepassword/', views.changepassword, name='changepassword'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('credit_debit/', views.credit_debit, name='credit_debit'),
    path('credit_history/', views.credit_history, name='credit_history'),
    path('login_as_user/<int:user_id>', views.login_as_user, name='login_as_user'),
    path('update_user_status/<int:user_id>', views.update_user_status, name='update_user_status'),
]