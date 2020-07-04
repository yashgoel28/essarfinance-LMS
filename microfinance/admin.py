from django.contrib import admin

# Register your models here.
from .models import Loans,Documents,Guarantor_Documents,Guarantors,Accounts,Staff,Expenditures, Installments,Clients

admin.site.register(Loans)
admin.site.register(Installments)
admin.site.register(Clients)
admin.site.register(Documents)
admin.site.register(Guarantors)
admin.site.register(Guarantor_Documents)
admin.site.register(Accounts)
admin.site.register(Staff)
admin.site.register(Expenditures)
