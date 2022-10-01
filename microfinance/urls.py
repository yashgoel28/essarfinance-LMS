
from django.contrib import admin
from django.conf.urls import url
from django.urls import path
from .import views
from .views import ClientSearchList
from django.conf import settings
from django.conf.urls.static import static

app_name='microfinance'


urlpatterns = [

    path('add_officer/',views.Add_Officer,name='addofficer'),
    path('add_client/',views.Add_Client,name='addclient'),
    url(r'^loan/(?P<pk>\d+)/(?P<sk>\d+)/$', views.Add_Loan,name="addloan"),
    url(r'^loan/intrest/(?P<pk>\d+)/(?P<sk>\d+)/$', views.Add_Loan_IntrestLoan,name="addloan_intrestloan"),
    url(r'^docs/(?P<pk>\d+)/$', views.Add_Docs,name="adddocs"),
    url(r'ClientDetails/(?P<pk>\d+)$', views.Client_Detail ,name="clientdetail"),
    url(r'^Expenditure/$', views.Add_Expense,name="addexpense"),
    url(r'^All-Expenditure/$', views.AllExpense,name="allexpense"),
    url(r'^Reports/$', views.Reports,name="reports"),
    url(r'^Report-Officer&Freq/$', views.Officer_And_Frequency_Wise_Report,name="report1"),
    url(r'^PDF-Officer&Freq/$', views.Officer_And_Frequency_Wise_pdf,name="pdf1"),
    url(r'^Report-TotalFinance&Collection/$', views.Total_Finance_And_Collection_Report,name="report2"), 
    url(r'^PDF-Officer&Freq/$', views.Total_Finance_And_Collection_pdf,name="pdf2"),
    url(r'^Report-Officerwise-TotalFinance&Collection/$', views.Officerwise_Total_Finance_And_Collection_Report,name="report"), 
    url(r'^PDF-Officer&Freq-Total/$', views.Officerwise_Total_Finance_And_Collection_pdf,name="pdf3"),
    url(r'^PDF-ClientForm/(?P<pk>\d+)/$', views.Client_Detail_Pdf,name="pdf4"),   
    url(r'^Total-Amount-Collected/$', views.Total_Amount_Collected_Report,name="report5"), 
    url(r'^All-Client_List/$', views.All_Clients_List,name="report6"), 
    url(r'^Week_Chart/$', views.Week_Chart_List,name="report7"), 
    url(r'^GuarantorDocs/(?P<pk>\d+)/$', views.ViewGuarantorDocs,name="viewgdocs"),
    url(r'^ClientDocs/(?P<pk>\d+)/$', views.ViewClientDocs,name="viewdocs"),
    url(r'SMS/$', views.SMSselect,name="smsselect"),
    url(r'^Search-by-loanid/$', views.Loanidsearch,name="searchloan"),
    url(r'PDF-PrintInstallments/$', views.PrintInstallmentsPDF,name="printinst"),
    url(r'SMS-Clients/$', views.SMS,name="sms"),
    url(r'opt/$', views.optimizeimg,name="optimizeimg"),

    url(r'Search/$', ClientSearchList.as_view(),name="search"),
    url(r'Home/$', views.Home,name="home"),
    url(r'LoanDetail/(?P<pk>\d+)$', views.Loan_Detail ,name="loandetail"),    
    url(r'LoanDetail/Intrest/(?P<pk>\d+)$', views.Loan_Detail_IntrestLoan ,name="loandetail_intrestloan"),    
    url(r'^Guarantor/(?P<pk>\d+)/$', views.Add_Guarantor,name="addguarantor"),
    url(r'^Guarantor/(?P<pk>\d+)/IntrestLoan/$', views.Add_Guarantor_IntrestLoan,name="addguarantor_intrestloan"),
    url(r'^GuarantorDocs/(?P<pk>\d+)/(?P<sk>\d+)/$', views.Add_Guarantor_Docs,name="addguarantordocs"),
    url(r'^GuarantorDocs/(?P<pk>\d+)/(?P<sk>\d+)/IntrestLoan/$', views.Add_Guarantor_Docs_IntrestLoan,name="addguarantordocs_intrestloan"),
    url(r'Edit/ClientDetails/(?P<pk>\d+)/$', views.EditClient, name="editclient"),
    url(r'Edit/LoanDetails/(?P<pk>\d+)/$', views.EditLoan, name="editloan"),
    url(r'Installment-List/(?P<pk>\d+)/$', views.InstallmentList, name="installmentlist"),
    url(r'Delete-Installment/$', views.DeleteIntsallment ,name="deleteinstallment"),   
    url(r'Add-Installment/(?P<pk>\d+)/$', views.AddInstallment ,name="addinstallment"),   
    url(r'Edit/Installments/(?P<pk>\d+)/$', views.EditInstallment, name="editinstallments"),
    url(r'temp/$', views.temporary ,name="tempview"),
]
