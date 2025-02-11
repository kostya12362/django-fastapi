from django.contrib import admin

from blockchains.models import Block, Currency, Provider


class AdminBlock(admin.ModelAdmin):
    pass


class AdminCurrency(admin.ModelAdmin):
    pass


class AdminProvider(admin.ModelAdmin):
    readonly_fields = ("name",)

    def has_add_permission(self, request):
        return False


admin.site.register(Block, AdminBlock)
admin.site.register(Currency, AdminCurrency)
admin.site.register(Provider, AdminProvider)
