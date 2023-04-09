from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyAccountManager(BaseUserManager):
    def create_user(self, username, email, password=None, is_reseller=False, reseller=1):
        """Creates and saves a User with the given email, username, password and extra fields"""
        if not email:
            raise ValueError("User must have an valid email")
        if not username:
            raise ValueError("User must have an username")
        if reseller:
            reseller = Account.objects.get(id=reseller)
            print(reseller)

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            is_reseller = is_reseller,
            reseller = reseller,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, reseller=None):
        """Creates and saves a Superuser with the given email, username, password and extra fields"""
        user = self.create_user(username, email, password, reseller=reseller)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_reseller = True
        user.reseller = None
        user.save(using=self._db)
        return user
    
class Account(AbstractBaseUser):
    #Authentication Details:
    email = models.EmailField(unique=True, verbose_name='email address')
    username = models.CharField(max_length=20, unique=True)

    #Personal Details:
    name = models.CharField(max_length=25, verbose_name="Client Name")
    phone_number = models.CharField(max_length=12)
    company_name = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=100)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    #Required Fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)

    #Required Boolean Fields
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_reseller = models.BooleanField(default=False)

    #App Permissions
    whtsapp_app = models.BooleanField(default=True)
    voice_app = models.BooleanField(default=False)

    #Reseller End User Mapper
    reseller = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='end_users')

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_staff
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

class WalletCredit(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('credit', 'Credit'),
        ('debit', 'Debit')
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, blank=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, null=True, blank=True)
    credit_on = models.DateTimeField(null=True, blank=True)
    debit_on = models.DateTimeField(null=True, blank=True)
    remark = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
    def is_credit(self):
        return self.transaction_type == 'credit'

    def is_debit(self):
        return self.transaction_type == 'debit'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_credit():
            self.user.wallet_balance = self.wallet_balance
        else:
            self.user.wallet_balance -= self.amount
        self.user.save()

class ServicePlan(models.Model):
    SERVICE_CHOICES = (
        ('Whtsapp', 'WhtsApp'),
        ('Voice Call', 'Voice Call'),
    )
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, null=True, blank=True)
    rate = models.DecimalField(max_digits=4, decimal_places=2)
    
    def __str__(self):
        return f"{self.user} - {self.service} - {self.rate}p"