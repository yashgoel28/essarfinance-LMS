from django import forms
from . import models
from django.forms import ModelForm

class AddStaff(forms.ModelForm):
    class Meta:
        model=models.Staff
        fields=['Officer_Name','Designation','Salary']


class AddClient(forms.ModelForm):
    class Meta:
        model=models.Clients
        fields= '__all__'
        widgets = {
            'Date_Added': forms.DateInput(attrs={'type': 'date'})
        }


class AddDocs(forms.ModelForm):
    class Meta:
        model=models.Documents
        fields= ['Image']

class AddLoan(forms.ModelForm):
    class Meta:
        model=models.Loans
        fields= ['Principle_Amount','Frequency','Purpose','No_Of_Installments','Intrest_Rate','File_Charge_Percent','Date_Created','Loan_Collector']
        widgets = {
            'Date_Created': forms.DateInput(attrs={'type': 'date'})
        }

class AddGuarantor(forms.ModelForm):
    class Meta:
        model=models.Guarantors
        fields= '__all__'
        

class AddGuarantorDocs(forms.ModelForm):
    class Meta:
        model=models.Guarantor_Documents
        fields= ['Image']
        
class AddExpenditures(forms.ModelForm):
    class Meta:
        model=models.Expenditures
        fields= '__all__'
        widgets = {
            'Date': forms.DateInput(attrs={'type': 'date'})
        }

class AddPenalty(forms.ModelForm):
    class Meta:
        model=models.Penalty
        fields = ['Status','Penalty_Paid']

class ClientSearchForm(forms.Form):
    search_name =  forms.CharField(
                    required = False,
                    label='Search By name',
                    widget=forms.TextInput(attrs={'placeholder': 'search here!'})
                  )

    search_id = forms.IntegerField(
                    required = False,
                    label='Search By Client Id:'
                  )           
