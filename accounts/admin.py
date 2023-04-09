from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q

from accounts.models import Account, WalletCredit, ServicePlan

class AccountAdmin(UserAdmin):
    list_display = ('username','last_login','date_joined','is_active','is_reseller', 'reseller_id')
    list_display_links = ('username',)
    readonly_fields = ('last_login', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ('is_active','is_reseller')
    fieldsets = (
        (None, {'fields': ('username','email','password', 'reseller')}),
        ('Personal Info', {'fields': ('name', 'phone_number', 'company_name', 'gst_number', 'address', 'city', 'state','country', 'pincode', 'wallet_balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_reseller','whtsapp_app','voice_app')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username','email','password', 'reseller')}),
        ('Personal Info', {'fields': ('name', 'phone_number', 'company_name', 'gst_number', 'address', 'city', 'state','country', 'pincode', 'wallet_balance')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_reseller', 'whtsapp_app','voice_app')}),
    )


class WalletCreditAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_balance')
    list_display_links = ('user',)
    readonly_fields = ()
    search_fields = ('user',)
    ordering = ()

    search_fields = ['user__username']
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
            queryset |= self.model.objects.filter(Q(user__id=search_term_as_int))
        except ValueError:
            pass
        return queryset, use_distinct

class ServicePlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'rate')

admin.site.register(WalletCredit, WalletCreditAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(ServicePlan, ServicePlanAdmin)