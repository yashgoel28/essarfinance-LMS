from calendar import month
from django.shortcuts import render,redirect
from .import forms
from .forms import AddExpenditures,AddGuarantor,AddStaff,AddClient,AddDocs,AddLoan,AddGuarantorDocs,EditClientDetail,EditLoanDetail,EditInstallmentDetail,AddInstallments,AddLoan_IntrestLoan
from .forms import ClientSearchForm
from .models import *
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from search_views.search import SearchListView,BaseFilter
from django.utils.dateparse import parse_date
from django.db.models import Q,Sum
from django.template import loader
from datetime import date
from datetime import datetime
import requests
import json
from twilio.rest import Client as twilioClient
from .filters import LoanFilter

from django.db.models import F
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO



URL = 'https://www.sms4india.com/api/v1/sendCampaign'


# get request
def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
  req_params = {
  'apikey':apiKey,
  'secret':secretKey,
  'usetype':useType,
  'phone': phoneNo,
  'message':textMessage,
  'senderid':senderId
  }
  return requests.post(reqUrl, req_params)

# Create your views here.
@login_required(login_url="/accounts/login/")
def Add_Officer(request):
    if request.method == 'POST':
        form=AddStaff(request.POST,request.FILES)
        if form.is_valid():
            form.save()
    else: 
        form=AddStaff()     
    return render(request,'microfinance/Add_Officer.html',{'form':form})

@login_required(login_url="/accounts/login/")
def Add_Client(request):
    
    Today = datetime.now()
    if request.method == 'POST':
        form=AddClient(request.POST,request.FILES)
        Phone = request.POST.get('Phone_no1_0')
        photoid = request.POST.get('Photo_Id')
        data = request.POST.get('Photo_Id_No')
        length = len(data)
        a=True
        
        if photoid == 'aadhar':
            if length != 12:
                messages.info(request, 'Photo Id No. is INVALID!')
                a=False
      
        elif photoid == 'pan':
            if length != 10:
                messages.info(request, 'Photo Id No. is INVALID!')
                a=False
            
        elif photoid == 'voter':
            if length != 10:
                messages.info(request, 'Photo Id No. is INVALID!')
                a=False
        elif photoid == 'passport':
            if length != 8:
                messages.info(request, 'Photo Id No. is INVALID!')    
                a=False        

        if form.is_valid() and a: 
            instance=form.save(commit=False)
            newobj = Accounts(Client=instance)
            instance.save()
            newobj.save()
            return redirect('microfinance:adddocs', pk=instance.pk)
        else:
            
            err =form.errors 
            form =AddClient()
            for e in err:
                if e =='Phone_no1' or e == 'Photo_Id_No':
                    Client = Clients.objects.filter(Q(Phone_no1=Phone)|Q(Photo_Id_No=data))
                    return render(request,'microfinance/Add_Client.html',{'Today':Today,'form':form,'err':err,'Client':Client})
            return render(request,'microfinance/Add_Client.html',{'Today':Today,'form':form,'err':err})
    
    else: 
        form =AddClient()
        return render(request,'microfinance/Add_Client.html',{'Today':Today,'form':form})

@login_required(login_url="/accounts/login/")
def Add_Docs(request,pk):
    if request.method == 'POST':
        form=AddDocs(request.POST,request.FILES)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.Client_id = pk
            instance.save()
            if 'm' in request.POST:
                return redirect('microfinance:adddocs', pk=pk)
            if 'n' in request.POST:
                return redirect('microfinance:addguarantor', pk=pk)
    else: 
        form=AddDocs()     
    return render(request,'microfinance/Add_Docs.html',{'form':form})

@login_required(login_url="/accounts/login/")
def Add_Loan(request,pk, sk):
    if request.method == 'POST':
        form=AddLoan(request.POST,request.FILES)
        instance=form.save(commit=False)
        client =Clients.objects.get(pk=pk)
        acc = Accounts.objects.get(Client=client)
        instance.Account =acc
        instance.Guarantor_id = sk
        if form.is_valid():            
            instance.save()
            Installment = (instance.Principle_Amount + (instance.Principle_Amount/100*instance.Intrest_Rate))/instance.No_Of_Installments
            if instance.Frequency !=2 :
                Inst = round(Installment,1)
                Installments_Inst = Installments(Installment_Paid = 0, Loan = instance, Date_Due = instance.First_Due_Date, Installment_Due = Inst,Installment_To_Be_Paid=Inst,Pending_Amount=Inst )
            else:
                Inst = round(Installment,1)
                Installments_Inst = Installments(Installment_Paid = 0, Loan = instance, Date_Due = instance.First_Due_Date, Installment_Due = round(Inst*7),Installment_To_Be_Paid=round(Inst*7),Pending_Amount=round(Inst*7) )
            Installments_Inst.save()   
            
            if instance.Frequency == 1:
                Date_Due = instance.First_Due_Date 
                for i in range(1,instance.No_Of_Installments):
                    Inst = round(Installment,1)
                    Date_Due = Date_Due + timedelta(1)
                    Installments_Inst = Installments(Installment_Paid = 0, Loan = instance,Date_Due = Date_Due, Installment_Due = round(Installment,1),Installment_To_Be_Paid=round(Installment,1),Pending_Amount=round(Installment,1))
                    Installments_Inst.save()
            if instance.Frequency == 2:
                Date_Due = instance.First_Due_Date 
                Extra_Days = instance.No_Of_Installments % 7
                for i in range(1,int(instance.No_Of_Installments/7)):                
                    Inst = Installment                
                    Date_Due = Date_Due + timedelta(7)
                    Installments_Inst = Installments(Installment_Paid = 0, Loan = instance, Date_Due = Date_Due, Installment_Due = round(Inst*7),Installment_To_Be_Paid=round(Inst*7),Pending_Amount=round(Inst*7))
                    Installments_Inst.save()
                if Extra_Days>0:
                    Inst = Installment
                    Date_Due = Date_Due + timedelta(Extra_Days)
                    Installments_Inst = Installments(Installment_Paid = 0, Loan = instance,Date_Due = Date_Due, Installment_Due = round(Inst*Extra_Days),Installment_To_Be_Paid=round(Inst*Extra_Days),Pending_Amount=round(Inst *Extra_Days))
                    Installments_Inst.save()
            if instance.Frequency == 3:
                Date_Due = instance.First_Due_Date 
                for i in range(1,int(instance.No_Of_Installments)):
                    Inst = round(Installment,1)
                    Date_Due = Date_Due + relativedelta(months=1)
                    Installments_Inst = Installments(Installment_Paid = 0, Loan = instance,Date_Due = Date_Due, Installment_Due = round(Installment,1),Installment_To_Be_Paid=round(Installment,1),Pending_Amount=round(Installment,1) )
                    Installments_Inst.save()
        return redirect('microfinance:clientdetail' ,pk=pk)
    else: 
        form=AddLoan()     
    return render(request,'microfinance/Add_Loan.html',{'form':form})

@login_required(login_url="/accounts/login/")
def Add_Guarantor(request,pk):
    if request.method == 'POST':
        form=AddGuarantor(request.POST,request.FILES)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect('microfinance:addguarantordocs', pk=pk, sk=instance.pk)
    else: 
        form=AddGuarantor()     
    return render(request,'microfinance/Add_Guarantor.html',{'form':form})


@login_required(login_url="/accounts/login/")
def Add_Guarantor_Docs(request,pk,sk):
    if request.method == 'POST':        
        form=AddGuarantorDocs(request.POST,request.FILES)      
        instance=form.save(commit=False)
        instance.Guarantor_id = sk
        instance.save()
        if 'k' in request.POST:            
            return redirect('microfinance:addguarantordocs', pk=pk,sk=sk)
        if 'l' in request.POST:    
            return redirect('microfinance:addloan', pk=pk,  sk=sk)      
    else: 
        form=AddGuarantorDocs()     
    return render(request,'microfinance/Add_Guarantor_Docs.html',{'form':form})


@login_required(login_url="/accounts/login/")
def Add_Expense(request):
    if request.user.is_superuser:    
        if request.method == 'POST':
            Date = request.POST.get('Month')
            form=AddExpenditures(request.POST,request.FILES)
            Expense = Expenditures.objects.filter(Date__month=Date,Date__year=timezone.now().date().year).order_by('Date','-Amount')
            if form.is_valid():
                form.save()
            return render(request,'microfinance/Add_Expense.html',{'form':form,'expense':Expense})
        else: 
            Expense = Expenditures.objects.filter(Date__month=timezone.now().date().month,Date__year=timezone.now().date().year).order_by('Date','-Amount')
            form=AddExpenditures()     
            return render(request,'microfinance/Add_Expense.html',{'form':form,'expense':Expense})
    else:
        return HttpResponse('you dont have access to this page. Contact admin')

        
@login_required(login_url="/accounts/login/")
def AllExpense(request):
    if request.user.is_superuser:
        Expense = Expenditures.objects.all().order_by('Date','-Amount')
        return render(request,'microfinance/Add_Expense.html',{'expense':Expense})
    else:
        return HttpResponse('you dont have access to this page. Contact admin')

@login_required(login_url="/accounts/login/")
def Client_Detail(request,pk):
    Client =Clients.objects.get(pk=pk)
    Account =Accounts.objects.get(Client=Client)
    Loan = Loans.objects.filter(Account =Account).distinct()
    if request.method == "POST" :
        if "save" in request.POST:
            pk=request.POST['pk']
            rem = request.POST['Reminder']
            remark=request.POST['remark']
            loan =Loan.get(pk=pk)
            loan.remark =remark
            loan.reminder=rem
            loan.save()
            
            return render(request,'microfinance/Client_Detail.html',{'Client':Client,'Account':Account,'Loan':Loan})
        if "IntrestLoan" in request.POST:
            return redirect('microfinance:addguarantor_intrestloan', pk=pk)
        return redirect('microfinance:addguarantor', pk=pk)
    else:        
        return render(request,'microfinance/Client_Detail.html',{'Client':Client,'Account':Account,'Loan':Loan})


@login_required(login_url="/accounts/login/")
def Loan_Detail(request,pk):
    Loan=Loans.objects.get(pk=pk)
    Installment = Installments.objects.filter(Loan=Loan).order_by('Date_Due','Date_Paid','-Installment_To_Be_Paid')
    Account =Accounts.objects.get(loans=Loan)  
    Client =Clients.objects.get(accounts=Account)    
    Total = Loan.Principle_Amount + Loan.Principle_Amount * Loan.Intrest_Rate / 100
    Total=round(Total,1)
    Penalties = Penalty.objects.filter(Loan=Loan)
    DatePaid= request.POST.get('date_paid')    
    Total_Pending = 0


    lastinst = Installment.filter(Date_Paid__isnull=False).filter(Installment_Paid__gt=0).order_by('Date_Paid').last()  

    if request.method == "POST":  
        Total_Pending = Total   #total amount stored in starting to calculate amnt pending 
        if 'status' in request.POST:    #To change the current status
            stat = bool(request.POST.get('Status'))
            Loan.Status =stat
            Loan.save()              
        
        
        if "pay" in request.POST:   #Code to add amount paid 
            if DatePaid is None or DatePaid =='':
                DatePaid=datetime.now()
            else:
                DatePaid =datetime.strptime(DatePaid, "%Y-%m-%d")                

            Amount_Paid = float(request.POST.get('amount'))             #amount entered
            Amount_Paid=round(Amount_Paid,1)
            Total_Pending = round(Total,1)              #total amount stored in starting to calculate amnt pending 
            for i in Installment:               #for loop to calc amount pending
                Total_Pending = Total_Pending - i.Installment_Paid
            
            if(Amount_Paid>Total_Pending):              #if the amount entered is more than the amount pending change amount paid to amount pending
                Amount_Paid = Total_Pending
            
            Inst_Obj = Installment.filter(Date_Paid__isnull=True).filter(Installment_To_Be_Paid__gt=0).order_by('Date_Due').first()         #new installment
            SameDate_Obj = Installment.filter(Date_Paid=DatePaid).first()                 #installment object having same date as today
            
            if SameDate_Obj is not None:                #code to pay on same date more than once
                SameDate_Obj.Installment_Paid = SameDate_Obj.Installment_Paid + Amount_Paid             #adding new amount to installment paid prev on same date
                Balance = Amount_Paid - SameDate_Obj.Installment_To_Be_Paid                     #calc balance 
                
                if Amount_Paid >= SameDate_Obj.Installment_To_Be_Paid:        #checking if the total amount recieved on that day is greater than the installment to be paid if yes then checking for penalty of that day and adding end date if penalty exists   
                    SameDate_Obj.Installment_To_Be_Paid = 0
                    SameDate_Obj.Pending_Amount = 0
                    Del =Installment.filter(Date_Due = SameDate_Obj.Date_Due).filter(Date_Paid__isnull=True).filter(Installment_Due =0).delete()       #del the new inst if created 
                    # try: #check this later to reduce code repeated multiple times
                    #     Penalty_Obj = Penalty.objects.filter(Loan=Loan).filter(Date_Ended__isnull=True).get(Date_Started=SameDate_Obj.Date_Due)
                    # except Penalty.DoesNotExist:
                    #     Penalty_Obj = None
                    # if Penalty_Obj is not None:
                    #     Penalty_Obj.Date_Ended = SameDate_Obj.Date_Paid
                    #     Days = (Penalty_Obj.Date_Ended - Penalty_Obj.Date_Started).days                 #no of days for which penalty is to be applied
                    #     Penalty_Obj.Penalty_Calc = Penalty_Obj.Amount*Penalty_Obj.Percent*Days/100 
                    #     Penalty_Obj.Penalty_Calc = round(Penalty_Obj.Penalty_Calc,1)     #calc penalty
                    #     Penalty_Obj.save()
                                 
                else:
                    SameDate_Obj.Installment_To_Be_Paid =SameDate_Obj.Installment_To_Be_Paid - Amount_Paid
                    SameDate_Obj.Pending_Amount = SameDate_Obj.Pending_Amount - Amount_Paid
                    SameDate_Obj.Installment_To_Be_Paid = round(SameDate_Obj.Installment_To_Be_Paid,1)
                    SameDate_Obj.Pending_Amount = round(SameDate_Obj.Pending_Amount,1)

                    if SameDate_Obj.Pending_Amount < SameDate_Obj.Installment_Paid:
                        # try:     #repeated pemtaly code. if pending amnt is less than install paid calc penaly and add date ended 
                        #     Penalty_Obj = Penalty.objects.filter(Loan=Loan).filter(Date_Ended__isnull=True).get(Date_Started=SameDate_Obj.Date_Due)
                        # except Penalty.DoesNotExist:
                        #     Penalty_Obj = None
                        # if Penalty_Obj is not None:
                        #     Penalty_Obj.Date_Ended = SameDate_Obj.Date_Paid
                        #     Days = (Penalty_Obj.Date_Ended - Penalty_Obj.Date_Started).days                 #no of days for which penalty is to be applied
                        #     Penalty_Obj.Penalty_Calc = Penalty_Obj.Amount*Penalty_Obj.Percent*Days/100 
                        #     Penalty_Obj.Penalty_Calc = round(Penalty_Obj.Penalty_Calc,1)     #calc penalty
                        #     Penalty_Obj.save()
                            # if SameDate_Obj.Pending_Amount<SameDate_Obj.Installment_Paid:
                            #     if SameDate_Obj.Installment_Due == 0:
                            #         PenaltyAmnt = SameDate_Obj.Installment_To_Be_Paid
                            #     else:
                            #         PenaltyAmnt = SameDate_Obj.Installment_Due
                            #     Penalty_Obj  = Penalty(Loan=Loan,Installment=SameDate_Obj,Date_Started=SameDate_Obj.Date_Due,Date_Ended=SameDate_Obj.Date_Paid,Amount=PenaltyAmnt)   
                            #     Days = (Penalty_Obj.Date_Ended - Penalty_Obj.Date_Started).days #check this later
                            #     Penalty_Obj.Penalty_Calc = Penalty_Obj.Amount*Penalty_Obj.Percent*Days/100 #this too
                            # else:
                            #     Penalty_Obj  = Penalty(Loan=Loan,Installment=SameDate_Obj,Date_Started=SameDate_Obj.Date_Due,Amount=PenaltyAmnt)
                        
                        Next = Installment.filter(Date_Due=SameDate_Obj.Date_Due).filter(Date_Paid__isnull =True).filter(Installment_Due = 0).first()       #code for changing the pending amount and the install to be paid of the installment created earlier with same date and 0 installment due
                        Next.Installment_To_Be_Paid = SameDate_Obj.Installment_To_Be_Paid
                        Next.Pending_Amount = SameDate_Obj.Pending_Amount
                        Next.save()
                SameDate_Obj.save()
            
            #same date installment case code ended here
            
            
            else:               #code for adding payment in a null date paid install obj
                Inst_Obj.Date_Paid = DatePaid
                Inst_Obj.Installment_Paid = Amount_Paid
                Balance = Amount_Paid - Inst_Obj.Installment_To_Be_Paid
                Balance = round(Balance,1)
                if Amount_Paid >= Inst_Obj.Installment_To_Be_Paid:             
                    Inst_Obj.Installment_To_Be_Paid = 0
                    Inst_Obj.Pending_Amount = 0
                else:       #if amount paid is less than creating a new inst obj with inst due 0 and same date due
                    Inst_Obj.Installment_To_Be_Paid = round((Inst_Obj.Installment_To_Be_Paid - Amount_Paid),1)
                    Inst_Obj.Pending_Amount = round(Inst_Obj.Installment_To_Be_Paid,1) 
                    NewObj = Installments(Loan = Loan,Installment_Due = 0,Installment_To_Be_Paid= Inst_Obj.Pending_Amount,Pending_Amount=Inst_Obj.Pending_Amount,Date_Due= Inst_Obj.Date_Due)  
                    NewObj.save()
                Inst_Obj.save()
                
                # if Inst_Obj.Date_Paid.date() > Inst_Obj.Date_Due:               
                #     if Inst_Obj.Installment_Due == 0:           #when the penalty is calculated from new inst obj with installment due 0
                #         PenaltyAmnt = Inst_Obj.Installment_To_Be_Paid
                #     else:                                       #when the penalty is calculated from inst obj with installment due >0
                #         PenaltyAmnt = Inst_Obj.Installment_Due
                #     try:           #checking if penalty exists or not . if doesnt exist then create one
                #         Penalty_Obj = Penalty.objects.filter(Loan=Loan).get(Date_Started=Inst_Obj.Date_Due)                       
                #         if Inst_Obj.Pending_Amount < Inst_Obj.Installment_Paid:             #adding end date if amnt paid>amnt pending
                #             Penalty_Obj.Date_Ended = Inst_Obj.Date_Paid
                #             Days = (Penalty_Obj.Date_Ended.date() - Penalty_Obj.Date_Started).days 
                #             Penalty_Obj.Penalty_Calc = Penalty_Obj.Amount*Penalty_Obj.Percent*Days/100 
                #             Penalty_Obj.Penalty_Calc = round(Penalty_Obj.Penalty_Calc,1)
                #             Penalty_Obj.save()
                #     except Penalty.DoesNotExist:            #creating a new penalty with end date if amnt paid>amnt pending
                #         if Inst_Obj.Pending_Amount < Inst_Obj.Installment_Paid:            
                #             Penalty_Obj  = Penalty(Loan=Loan,Installment=Inst_Obj,Date_Started=Inst_Obj.Date_Due,Date_Ended=Inst_Obj.Date_Paid,Amount=PenaltyAmnt)
                #             Days = (Penalty_Obj.Date_Ended.date() - Penalty_Obj.Date_Started).days 
                #             Penalty_Obj.Penalty_Calc = Penalty_Obj.Amount*Penalty_Obj.Percent*Days/100 
                #             Penalty_Obj.Penalty_Calc = round(Penalty_Obj.Penalty_Calc,1)
                #         else:               #creating a new penalty without end date
                #             Penalty_Obj  = Penalty(Loan=Loan,Installment=Inst_Obj,Date_Started=Inst_Obj.Date_Due,Amount=PenaltyAmnt)
                #         Penalty_Obj.save()
            #code for adding payment in a null date paid install obj ended here
            
            #code to handle conditions when balance>0 
            if SameDate_Obj is not None:
                Obj = SameDate_Obj
            else:
                Obj = Inst_Obj
            while(Balance > 0):
                NextObj = Installment.filter(Date_Due__gte = Obj.Date_Due).filter(Date_Paid__isnull=True).filter(Installment_To_Be_Paid__gt=0).order_by('Date_Due','Date_Paid','-Installment_To_Be_Paid').first()
                if Balance >= NextObj.Installment_To_Be_Paid:   
                    
                    Balance = Balance - round(NextObj.Installment_To_Be_Paid,1)
                    NextObj.Pending_Amount = 0
                    NextObj.Installment_To_Be_Paid = 0
                    NextObj.Date_Paid = DatePaid 
                     
                else:
                    
                    NextObj.Pending_Amount  = NextObj.Pending_Amount - Balance
                    Balance = Balance - NextObj.Installment_To_Be_Paid
                    NextObj.Installment_To_Be_Paid =NextObj.Pending_Amount
                NextObj.save()
            
                   
        if "penalty" in request.POST:
            PenBal = float(request.POST.get('Penalty_Paid'))
            List = request.POST.getlist('Status')
    
                      
                
            # if Penalty_Obj.Penalty_Calc == Penalty_Obj.Penalty_Paid:
            #     Penalty_Obj = Penalties.filter(Status = False).exclude(Penalty_Calc =F('Penalty_Paid')).order_by("Date_Started").first()
                
            # Penalty_Obj.Penalty_Paid = Penalty_Obj.Penalty_Paid + Pen_Paid 
            #Penalty_Obj.Status = bool(request.POST.get('Status'))
            # Penalty_Obj.Penalty_Paid_Date =datetime.now()
            # Penalty_Obj.save()
            # PenBal = Pen_Paid - Penalty_Obj.Penalty_Calc
            while PenBal >0:
                Penalty_Obj = Penalties.filter(Status = False).exclude(Penalty_Calc = F('Penalty_Paid')).order_by("Date_Started").first()
                
                if PenBal >= Penalty_Obj.Penalty_Calc-Penalty_Obj.Penalty_Paid:
                    PenBal = PenBal - (Penalty_Obj.Penalty_Calc-Penalty_Obj.Penalty_Paid)
                    Penalty_Obj.Penalty_Paid = round(Penalty_Obj.Penalty_Calc)
                    Penalty_Obj.Date_Paid = datetime.now()
                    
                    if Penalty_Obj.Date_Ended is not None:
                        Penalty_Obj.Status = True
                    Penalty_Obj.save()
                else:
                    Penalty_Obj.Penalty_Paid = Penalty_Obj.Penalty_Paid+PenBal
                    Penalty_Obj.Date_Paid = datetime.now()
                    PenBal = 0
                    Penalty_Obj.save()               
            for i in List:
                n = Penalty.objects.get(id=i)
                n.Status =True
                n.save()  
        return redirect("microfinance:home")

    else:
        ii = Installments.objects.filter(Loan=Loan).filter(Date_Due__lt = timezone.now()).filter(Installment_Due__gt = 0)
        for i in ii:
            Amnt = round(i.Installment_Due/2,1)
            paid = i.Installment_Paid
            try:
                p= Penalty.objects.filter(Loan=Loan).filter(Date_Started=i.Date_Due).filter(Penalty_Calc__lt=F('Penalty_Paid')).first()
                if ((i.Installment_To_Be_Paid < i.Installment_Due/2) and (i.Date_Paid is None) and p):
                    p.Date_Ended = Installments.objects.filter(Loan=Loan).filter(Date_Due__lt=i.Date_Due).exclude(Date_Paid = None).order_by('-Date_Due','-Date_Paid').first().Date_Paid
                    if p.Date_Ended>p.Date_Started:
                        Days = (p.Date_Ended - p.Date_Started).days
                        p.Penalty_Calc = round(Days*p.Amount*2/100)
                        p.save()
                    else:
                        p.delete()
            except Penalty.DoesNotExist:
                        PObj =Penalty(Loan=Loan,Installment=i,Date_Started=i.Date_Due,Amount=i.Installment_Due)
                        PObj.save()
                        if ((i.Installment_To_Be_Paid < i.Installment_Due/2) and (i.Date_Paid is None)):
                            PObj.Date_Ended = Installments.objects.filter(Loan=Loan).filter(Date_Due__lt=i.Date_Due).exclude(Date_Paid = None).order_by('-Date_Due','-Date_Paid').first().Date_Paid
                            if PObj.Date_Ended>PObj.Date_Started:     
                                Days = (PObj.Date_Ended - PObj.Date_Started).days
                                PObj.Penalty_Calc = round(Days*PObj.Amount*2/100)                                       
                                PObj.save()
                            else:
                                PObj.delete()
            if i.Date_Paid is not None:
                if ((i.Date_Due >= i.Date_Paid) and (i.Installment_To_Be_Paid < i.Installment_Due/2)):
                    try:
                        pen = Penalties.get(Date_Started = i.Date_Due).delete()
                        continue
                    except (Penalty.DoesNotExist,AttributeError):
                        continue
                elif ((i.Date_Due < i.Date_Paid) and (i.Installment_To_Be_Paid < i.Installment_Due/2)):
                    try:
                        pen = Penalties.get(Date_Started = i.Date_Due)
                        pen.Date_Ended =i.Date_Paid
                        Days = (pen.Date_Ended - pen.Date_Started).days
                        pen.Penalty_Calc = round(Days*pen.Amount*2/100)
                        pen.save()
                    except (Penalty.DoesNotExist,AttributeError):
                        PObj =Penalty(Loan=Loan,Installment=i,Date_Started=i.Date_Due,Date_Ended=i.Date_Paid,Amount=i.Installment_Due)
                        Days = (PObj.Date_Ended - PObj.Date_Started).days
                        PObj.Penalty_Calc = round(Days*PObj.Amount*2/100)
                        
                        PObj.save()
                    continue

            for j in Installments.objects.filter(Loan=Loan).filter(Date_Due=i.Date_Due).filter(Installment_Due = 0):
                paid = paid + j.Installment_Paid
                try:       
                               
                    PObj = Penalty.objects.filter(Loan=Loan).filter(Date_Started=j.Date_Due).first()
                    if ((j.Installment_To_Be_Paid<=j.Installment_Due/2) or (paid>Amnt)):
                        
                        if j.Date_Paid is not None:
                            PObj.Date_Ended = j.Date_Paid

                        elif j.Date_Paid is None:
                            PObj.Date_Ended = Installments.objects.filter(Loan=Loan).filter(Date_Due__lt=j.Date_Due).order_by('-Date_Due','-Date_Paid').first().Date_Paid
                        PObj.save()
                        Days = (PObj.Date_Ended- PObj.Date_Started).days
                        
                        PObj.Penalty_Calc = round(PObj.Amount*PObj.Percent*Days/100)                    
                        PObj.save()        
                        break      
                except (Penalty.DoesNotExist,AttributeError):
                    if(paid>Amnt):
                        
                        PObj =Penalty(Loan=Loan,Installment=i,Date_Started=i.Date_Due,Date_Ended=j.Date_Paid,Amount=i.Installment_Due)
                        Days = (PObj.Date_Ended- PObj.Date_Started).days
                        
                        PObj.Penalty_Calc = round(PObj.Amount*PObj.Percent*Days/100)                    
                        PObj.save()

                        break
                    else:
                        PObj =Penalty(Loan=Loan,Installment=i,Date_Started=i.Date_Due,Amount=i.Installment_Due)
                        PObj.save()
                        break
                
        
        amnt_pen = 0
        inst = Installments.objects.filter(Loan=Loan).filter(Q(Date_Paid__lte=timezone.now())|Q(Date_Due__lte=timezone.now())).distinct()
        
        for i in inst:
            amnt_pen = amnt_pen + i.Installment_Due - i.Installment_Paid
            
        Total_Pending = round(Total,1)
        for i in Installment:
            Total_Pending = Total_Pending - i.Installment_Paid
        Total_Penalty = 0
        for p in Penalties:
            if p.Status is True:
                pass
            else:
                if p.Date_Ended is None:
                    days = (datetime.now().date() - p.Date_Started).days
                    pcal = p.Amount*days*p.Percent/100
                    p.Penalty_Calc = round(pcal)
                    p.save()
                    
                    Total_Penalty = Total_Penalty + pcal - p.Penalty_Paid
                else: 
                    Total_Penalty = Total_Penalty + p.Penalty_Calc - p.Penalty_Paid
        Total_Penalty =round(Total_Penalty,1)

        return render(request,'microfinance/Loan_Detail.html',{'Total_Penalty':Total_Penalty,'Total':Total,'Installment':Installment,'Loan':Loan,'Client':Client,'Penalty':Penalties,'Total_Pending':round(Total_Pending,1),'amnt_pen':round(amnt_pen,1),'lastinst':lastinst})


class ClientFilter(BaseFilter):
    search_fields = {
        'search_name' : ['Name'],
        'search_id' : { 'operator' : '__exact', 'fields' : ['pk'] },
        'search_phone' : ['Phone_no1','Phone_no2']
    }

class ClientSearchList(SearchListView):
    model = Clients
    template_name = "microfinance/Client_Result.html"
    form_class = ClientSearchForm
    filter_class = ClientFilter


def Loanidsearch(request):    
    loanid=request.POST.get('loan_id')
    if len(loanid)==0  or loanid ==0:
        return redirect('/Home')
    loan = Loans.objects.get(pk=int(loanid))
    Clientid= Clients.objects.filter(pk=loan.Account.Client.pk)
    return redirect('microfinance:loandetail',pk=loan.pk)


@login_required(login_url="/accounts/login/")
def Reports(request):
    staff =Staff.objects.all().distinct()
    return render(request,'microfinance/Reports.html',{'users':staff})

@login_required(login_url="/accounts/login/")
def Officer_And_Frequency_Wise_Report(request):
    Staff_pk=int(request.POST.get('name'))
    status =(request.POST.get('status'))
    if status == 'False':
        Loanstat =Loans.objects.all().filter(Status=False)
    else:
        Loanstat =Loans.objects.all().filter(Status=True)
    Frequency=int(request.POST.get('loan'))
    if Staff_pk != 0 and Frequency != 0: 
        Loan =Loanstat.filter(Loan_Collector=Staff_pk,Frequency =Frequency)
    if Staff_pk == 0 and Frequency !=0:
        Loan =Loanstat.filter(Frequency =Frequency).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10)
    if Staff_pk !=0 and Frequency ==0:
        Loan =Loanstat.filter(Loan_Collector=Staff_pk)
    if Staff_pk == 0 and Frequency == 0:
        Loan =Loanstat.exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10)
    Installment = Installments.objects.filter(Loan__in=Loan).order_by('Date_Due').filter(Date_Due__lte =datetime.now())
    Advance_Inst =Installments.objects.filter(Date_Due__gt=datetime.now()).filter(Date_Paid=datetime.now())
    Today = datetime.now()
    Total_Daily_inst = 0
    Total_Amnt_to_be_coll=0
    Total_amnt_col =0
    Total_bal = 0
    Dic1 ={}
    Dic2={}
    dic3={}
    dic4={}
    for l in Loan:
        Total_Daily_inst =Total_Daily_inst + l.installments_set.first().Installment_Due
        Total_Amnt_to_be_coll=0
        Total_amnt_col =0
        Total_bal = 0
        All1 =Installments.objects.all().filter(Loan =l).order_by('Date_Due').filter(Date_Due__lte = datetime.now())
        All = Installments.objects.all().filter(Loan =l).order_by('Date_Due').exclude(Date_Due__lte= datetime.now())
        All2 =  Installments.objects.all().filter(Loan =l).order_by('Date_Due').filter(Date_Paid__isnull = False)
        for a in All1:
            Total_Amnt_to_be_coll = Total_Amnt_to_be_coll + a.Installment_Due
        for a in All2:
            Total_amnt_col = Total_amnt_col + a.Installment_Paid
        Total_bal = Total_bal + Total_Amnt_to_be_coll - Total_amnt_col
        for a in All:
            Total_bal = Total_bal + a.Installment_Due
        Dic1[l.pk]=round(Total_Amnt_to_be_coll,1)
        Dic2[l.pk]=round(Total_amnt_col,1)
        dic3[l.pk] = round(abs(Dic1[l.pk]-Dic2[l.pk]),1)
        dic4[l.pk]=round(Total_bal,1)
        
    Total_Amnt_Pending=0
    Dic ={}
    for l in Loan:
        Total_Amnt_Pending=0
        All =Installments.objects.all().filter(Loan =l).order_by('Date_Due')
        for a in All:
            Total_Amnt_Pending = Total_Amnt_Pending + a.Installment_Due - a.Installment_Paid
        Dic[l.pk]=Total_Amnt_Pending
    
    Total_Amnt_Pending=0
    
    for i,j in dic3.items():
        Total_Amnt_Pending+=j
    Total_Amnt_balance=0
    for i,j in Dic.items():
        Total_Amnt_balance+=j
       
    if Advance_Inst is not None:
        return render(request,'microfinance/Officer_And_Frequency_Wise_Report.html',{'adv':Advance_Inst,'loans':Loan,'insts':Installment,'Today':Today,'Staff':Staff_pk,'Frequency':Frequency,'totalpendingdict':Dic,'TotalAmnt':Total_Amnt_Pending,'Total_bal_dic':dic4,'Total_amt_to_be_col_dic':Dic1,'Total_amt_col_dic':Dic2,'Total_Pen_dic':dic3,'Total_Daily_inst':Total_Daily_inst,'Total_Amnt_balance':Total_Amnt_balance})
    else:
        return render(request,'microfinance/Officer_And_Frequency_Wise_Report.html',{'loans':Loan,'insts':Installment,'Today':Today,'Staff':Staff_pk,'Frequency':Frequency,'totalpendingdict':Dic,'TotalAmnt':Total_Amnt_Pending,'Total_bal_dic':dic4,'Total_amt_to_be_col_dic':Dic1,'Total_amt_col_dic':Dic2,'Total_Pen_dic':dic3,'Total_Daily_inst':Total_Daily_inst,'Total_Amnt_balance':Total_Amnt_balance})

@login_required(login_url="/accounts/login/")
def Officer_And_Frequency_Wise_pdf(request):
    if request.method =="POST":
        List = request.POST.getlist('Check') 
        
        status =(request.POST.get('status'))
        Loan = Loans.objects.none()
        for i in List:
            n = Loans.objects.filter(id=i)            
            Loan= Loan | n
        
        Installment = Installments.objects.filter(Loan__in=Loan).order_by('Date_Due').filter(Date_Due__lte =datetime.now())
        Advance_Inst =Installments.objects.filter(Date_Due__gt=datetime.now()).filter(Date_Paid=datetime.now())
        Today = datetime.now()
        
        Total_Amnt_to_be_coll=0
        Total_amnt_col =0
        Total_bal = 0
        Dic1 ={}
        Dic2={}
        dic3={}
        dic4={}
        for l in Loan:
            
            Total_Amnt_to_be_coll=0
            Total_amnt_col =0
            Total_bal = 0
            All1 =Installments.objects.all().filter(Loan =l).order_by('Date_Due').filter(Date_Due__lte = datetime.now())
            All = Installments.objects.all().filter(Loan =l).order_by('Date_Due').exclude(Date_Due__lte= datetime.now())
            All2 =  Installments.objects.all().filter(Loan =l).order_by('Date_Due').filter(Date_Paid__isnull = False)
            for a in All1:
                Total_Amnt_to_be_coll = Total_Amnt_to_be_coll + a.Installment_Due
            for a in All2:
                Total_amnt_col = Total_amnt_col + a.Installment_Paid
            Total_bal = Total_bal + Total_Amnt_to_be_coll - Total_amnt_col
            for a in All:
                Total_bal = Total_bal + a.Installment_Due
            Dic1[l.pk]=round(Total_Amnt_to_be_coll,1)
            Dic2[l.pk]=round(Total_amnt_col,1)
            dic3[l.pk] = round(abs(Dic1[l.pk]-Dic2[l.pk]),1)
            dic4[l.pk]=round(Total_bal,1)
            
        Total_Amnt_Pending=0
        Dic ={}
        for l in Loan:
            Total_Amnt_Pending=0
            All =Installments.objects.all().filter(Loan =l).order_by('Date_Due')
            for a in All:
                Total_Amnt_Pending = Total_Amnt_Pending + a.Installment_Due - a.Installment_Paid
            Dic[l.pk]=Total_Amnt_Pending
        
        Total_Amnt_Pending=0
        for i,j in Dic.items():
            Total_Amnt_Pending+=j
        if Advance_Inst is not None:
            return render(request,'microfinance/pdfs/Officer_And_Frequency_Wise_pdf.html',{'adv':Advance_Inst,'loans':Loan,'insts':Installment,'Today':Today,'totalpendingdict':Dic,'TotalAmnt':Total_Amnt_Pending,'Total_bal_dic':dic4,'Total_amt_to_be_col_dic':Dic1,'Total_amt_col_dic':Dic2,'Total_Pen_dic':dic3})
        else:
            return render(request,'microfinance/pdfs/Officer_And_Frequency_Wise_pdf.html',{'loans':Loan,'insts':Installment,'Today':Today,'totalpendingdict':Dic,'TotalAmnt':Total_Amnt_Pending,'Total_bal_dic':dic4,'Total_amt_to_be_col_dic':Dic1,'Total_amt_col_dic':Dic2,'Total_Pen_dic':dic3})


@login_required(login_url="/accounts/login/")
def Total_Finance_And_Collection_Report(request):
    start=request.POST.get('from')
    end=request.POST.get('to')
    if(start == '' or end == ''):
        return render(request,'microfinance/error/report_datenull.html')
    sdate = parse_date(start)    
    edate =parse_date(end)
    dd = [sdate + timedelta(days=x) for x in range((edate-sdate).days + 1)]
    Today= datetime.now()
    Lo = Loans.objects.filter(First_Due_Date__range=[start,end])
    Loan = Loans.objects.filter(Q(installments__Date_Due__range=[start,end])|Q(installments__Date_Paid__range=[start,end])).distinct()
    Installment =Installments.objects.filter(Q(Date_Due__range=[start,end])|Q(Date_Paid__range=[start,end])).order_by("Loan")
    Installment2 = Installments.objects.filter(Date_Due__range=[start,end]).order_by('Loan')
    Penalties =Penalty.objects.filter(Date_Started__range=[start,end])
    Pen =Penalty.objects.filter(Penalty_Paid_Date__range=[start,end])
    Total_Amnt_Financed =0
    Total_FileCharge=0
    Total_Amnt_Collected=0
    Total_Amnt_To_Be_Collected=0
    Total_Intrest_To_Be_Collected=0
    Total_Intrest_Collected=0
    Total_Penalty =0
    Total_Penalty_Coll =0
    for Inst in Installment2:
        Total_Amnt_To_Be_Collected = Total_Amnt_To_Be_Collected + Inst.Installment_Due   
        Total_Intrest_To_Be_Collected =Total_Intrest_To_Be_Collected + Inst.Installment_Due * Inst.Loan.Intrest_Rate/100
    for p in Penalties:
        if p.Status == True:
            Total_Penalty= Total_Penalty + p.Penalty_Paid
            
        else:
            Total_Penalty= Total_Penalty + p.Penalty_Calc
            
    for p in Pen:
        Total_Penalty_Coll =Total_Penalty_Coll + p.Penalty_Paid
    for L in Lo:
        Total_Amnt_Financed = Total_Amnt_Financed + L.Principle_Amount
        Total_FileCharge = Total_FileCharge + L.File_Charge_Percent*L.Principle_Amount/100

    for Inst in Installment:
        Total_Intrest_Collected = Total_Intrest_Collected + Inst.Installment_Paid*Inst.Loan.Intrest_Rate/100
        Total_Amnt_Collected = Total_Amnt_Collected + Inst.Installment_Paid
            
    return render(request,'microfinance/Total_Finance_And_Collection_Report.html',{'Total_pencol':Total_Penalty_Coll,'start':start,'end':end,'loans':Loan,'insts':Installment,'dates':dd,'totalloan':Total_Amnt_Financed,'totalfc':Total_FileCharge,'totalinst':Total_Amnt_Collected,
    'totalamnt':Total_Amnt_To_Be_Collected,'intrest':Total_Intrest_To_Be_Collected,'totalpenalty':Total_Penalty,'intrestrec':Total_Intrest_Collected})

@login_required(login_url="/accounts/login/")
def Total_Finance_And_Collection_pdf(request):
    start=request.POST.get('from')
    end=request.POST.get('to')
    sdate = parse_date(start)
    edate =parse_date(end)
    dd = [sdate + timedelta(days=x) for x in range((edate-sdate).days + 1)]
    Today= datetime.now()
    Loan = Loans.objects.filter(Q(installments__Date_Due__range=[start,end])|Q(installments__Date_Paid__range=[start,end])).distinct()
    Installment =Installments.objects.filter(Date_Due__range=[start,end]).order_by("Loan")
    Installment2 = Installments.objects.filter(Date_Due__range=[start,end]).order_by('Loan')
    Penalties =Penalty.objects.filter(Date_Started__range=[start,end])
    Pen =Penalty.objects.filter(Penalty_Paid_Date__range=[start,end])
    Total_Amnt_Financed =0
    Total_FileCharge=0
    Total_Amnt_Collected=0
    Total_Amnt_To_Be_Collected=0
    Total_Intrest_To_Be_Collected=0
    Total_Intrest_Collected=0
    Total_Penalty =0
    Total_Penalty_Coll =0
    for Inst in Installment2:
        Total_Amnt_To_Be_Collected = Total_Amnt_To_Be_Collected + Inst.Installment_Due        
        Total_Intrest_To_Be_Collected =Total_Intrest_To_Be_Collected + Inst.Installment_Due * Inst.Loan.Intrest_Rate/100
    for p in Penalties:
        if p.Status == True:
            Total_Penalty= Total_Penalty + p.Penalty_Paid
        else:
            Total_Penalty= Total_Penalty + p.Penalty_Calc
    for p in Pen:
        Total_Penalty_Coll =Total_Penalty_Coll + p.Penalty_Paid
    for L in Loan:
        Total_Amnt_Financed = Total_Amnt_Financed + L.Principle_Amount
        Total_FileCharge = Total_FileCharge + L.File_Charge_Percent*L.Principle_Amount/100
    for Inst in Installment:
        Total_Intrest_Collected = Total_Intrest_Collected + Inst.Installment_Paid*Inst.Loan.Intrest_Rate/100
        Total_Amnt_Collected = Total_Amnt_Collected + Inst.Installment_Paid
    return render(request,'microfinance/pdfs/Total_Finance_And_Collection_pdf.html',{'Total_pencol':Total_Penalty_Coll,'start':start,'end':end,'loans':Loan,'insts':Installment,'dates':dd,'totalloan':Total_Amnt_Financed,'totalfc':Total_FileCharge,'totalinst':Total_Amnt_Collected,
    'totalamnt':Total_Amnt_To_Be_Collected,'intrest':Total_Intrest_To_Be_Collected,'totalpenalty':Total_Penalty,'intrestrec':Total_Intrest_Collected})


@login_required(login_url="/accounts/login/")
def Officerwise_Total_Finance_And_Collection_Report(request):
    Staff_pk=int(request.POST.get('name'))
    Frequency=int(request.POST.get('loan'))
    start=request.POST.get('from')
    end=request.POST.get('to')
    if(start == '' or end == ''):
        return render(request,'microfinance/error/report_datenull.html')
    sdate = parse_date(start)
    edate =parse_date(end)
    
    Today= datetime.now()
    if Staff_pk != 0 and Frequency != 0: 
        Loan = Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(Frequency=Frequency).filter(Q(installments__Date_Paid__range=[start,end])|Q(installments__Date_Due__range=[start,end])).distinct().order_by("id")
        Loan2 = Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(Frequency=Frequency).filter(penalty__Penalty_Paid_Date__range=[start,end]).distinct().order_by("id")
        Loan3 =Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(Frequency=Frequency).filter(Loan_Date__range=[start,end]).distinct()
 
    if Staff_pk == 0 and Frequency !=0:
        Loan = Loans.objects.filter(Frequency=Frequency).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10).filter(Q(installments__Date_Paid__range=[start,end])|Q(installments__Date_Due__range=[start,end])).distinct().order_by("id")
        Loan2 = Loans.objects.filter(Frequency=Frequency).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10).filter(penalty__Penalty_Paid_Date__range=[start,end]).distinct().order_by("id")
        Loan3 =Loans.objects.filter(Frequency=Frequency).filter(Loan_Date__range=[start,end]).distinct()

    if Staff_pk !=0 and Frequency ==0:
        Loan = Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(Q(installments__Date_Paid__range=[start,end])|Q(installments__Date_Due__range=[start,end])).distinct().order_by("id")
        Loan2 = Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(penalty__Penalty_Paid_Date__range=[start,end]).distinct().order_by("id")
        Loan3 =Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(Loan_Date__range=[start,end]).distinct()

    if Staff_pk == 0 and Frequency == 0:
        Loan = Loans.objects.filter(Q(installments__Date_Paid__range=[start,end])|Q(installments__Date_Due__range=[start,end])).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10).distinct().order_by("id")
        Loan2 = Loans.objects.filter(penalty__Penalty_Paid_Date__range=[start,end]).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10).distinct().order_by("id")
        Loan3 =Loans.objects.filter(Loan_Date__range=[start,end]).distinct()

    AmntCollected =PenaltyCollected=File_ChargeCollected =AmntToBeCollected= 0
    Amnt_Collected = {}
    Penalty_Collected = {}
    File_Charge={}
    Amnt_To_Be_Collected = {}
    
        
    for i in Loan3:
        File_Charge[i.pk] = i.Principle_Amount*i.File_Charge_Percent/100
        File_ChargeCollected = File_ChargeCollected + File_Charge[i.pk]
    for i in Loan:
        Amnt_Collected[i.pk] = Installments.objects.filter(Loan=i).filter(Date_Paid__range=[start,end]).distinct().aggregate(Sum('Installment_Paid'))
        Amnt_To_Be_Collected[i.pk] = Installments.objects.filter(Loan=i).filter(Date_Due__range=[start,end]).distinct().aggregate(Sum('Installment_Due'))
        if Amnt_Collected[i.pk]["Installment_Paid__sum"]:
            AmntCollected = AmntCollected + Amnt_Collected[i.pk]["Installment_Paid__sum"]
        if Amnt_To_Be_Collected[i.pk]["Installment_Due__sum"]:
            AmntToBeCollected = AmntToBeCollected + Amnt_To_Be_Collected[i.pk]["Installment_Due__sum"] 
    for i in Loan2:
        Penalty_Collected[i.pk]=Penalty.objects.filter(Loan=i).filter(Penalty_Paid_Date__range=[start,end]).distinct().aggregate(Sum('Penalty_Paid'))
        PenaltyCollected = PenaltyCollected + Penalty_Collected[i.pk]["Penalty_Paid__sum"]
    return render(request,'microfinance/Officerwise_Total_Finance_And_Collection_Report.html',{'start':start,'end':end,'Staff':Staff_pk,'amnt_collected':Amnt_Collected,'Loan':Loan,'Loan3':Loan3,'Loan2':Loan2,'amntcollected':AmntCollected,'amnttobecollected':AmntToBeCollected,'amnt_to_be_collected':Amnt_To_Be_Collected,'penalty_collected':Penalty_Collected,'penaltycollected':PenaltyCollected,'file_charge':File_Charge,'filecollected':File_ChargeCollected})

@login_required(login_url="/accounts/login/")
def Officerwise_Total_Finance_And_Collection_pdf(request):
    Staff_pk=int(request.POST.get('name'))
    Frequency=int(request.POST.get('loan'))
    start=request.POST.get('from')
    end=request.POST.get('to')
    if(start == '' or end == ''):
        return render(request,'microfinance/error/report_datenull.html')
    sdate = parse_date(start)
    edate =parse_date(end)
    dd = [sdate + timedelta(days=x) for x in range((edate-sdate).days + 1)]
    Today= datetime.now()
    if Staff_pk != 0 and Frequency != 0: 
        Loan = Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(Frequency=Frequency).filter(Q(installments__Date_Due__range=[start,end])|Q(installments__Date_Paid__range=[start,end])).distinct().order_by("id").filter(Status=False)
    if Staff_pk == 0 and Frequency !=0:
        Loan = Loans.objects.filter(Frequency=Frequency).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10).filter(Q(installments__Date_Due__range=[start,end])|Q(installments__Date_Paid__range=[start,end])).distinct().order_by("id").filter(Status=False)
    if Staff_pk !=0 and Frequency ==0:
        Loan = Loans.objects.filter(Loan_Collector_id=Staff_pk).filter(Q(installments__Date_Due__range=[start,end])|Q(installments__Date_Paid__range=[start,end])).distinct().order_by("id").filter(Status=False)
    if Staff_pk == 0 and Frequency == 0:
        Loan = Loans.objects.filter(Q(installments__Date_Due__range=[start,end])|Q(installments__Date_Paid__range=[start,end])).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10).distinct().order_by("id").filter(Status=False)
    Installment =Installments.objects.filter(Q(Date_Due__range=[start,end])|Q(Date_Paid__range=[start,end])).filter(Loan__in=Loan).order_by("Loan")
    Installment2 = Installments.objects.filter(Date_Due__range=[start,end]).filter(Loan__in=Loan)
    Installment5 = Installments.objects.filter(Date_Paid__range=[start,end]).filter(Loan__in=Loan)
    Total_Amnt_Pending=0
    Amnt_Collected = 0
    Dic ={}
    Dic2={}
    for l in Loan:
        Total_Amnt_Pending=0
        Amnt_Collected = 0
        All =Installments.objects.all().filter(Loan =l).filter(Date_Due__lte=end).order_by('Date_Due')
        for a in All:
            Total_Amnt_Pending = Total_Amnt_Pending + a.Installment_Due - a.Installment_Paid
            
        Dic[l.pk]=Total_Amnt_Pending
        install= Installments.objects.all().filter(Q(Date_Due__lte=end)|Q(Date_Paid__lte=end)).filter(Loan =l).order_by('Date_Due')
        for x in install:
            Amnt_Collected = Amnt_Collected + x.Installment_Paid
        Dic2[l.pk]=Amnt_Collected
    Total_Amnt_Financed =0
    Total_Amnt_Collected=0
    Total_Intrest_Collected=0
    for Inst in Installment5:
        Total_Intrest_Collected = Total_Intrest_Collected + Inst.Installment_Paid*Inst.Loan.Intrest_Rate/100
        Total_Amnt_Collected = Total_Amnt_Collected + Inst.Installment_Paid
    return render(request,'microfinance/pdfs/Officerwise_Total_Finance_And_Collection_pdf.html',{'Dic':Dic,'Dic2':Dic2,'loans':Loan,'insts':Installment,'dates':dd,'totalinst':Total_Amnt_Collected,
    'start':start,'end':end,'intrestrec':Total_Intrest_Collected,'Freq':Frequency,'Staff':Staff_pk})

@login_required(login_url="/accounts/login/")
def All_Clients_List(request):
    Staff_pk=int(request.POST.get('name'))
    if Staff_pk !=0 :
        Loan=Loans.objects.all().filter(Loan_Collector_id=Staff_pk).filter(Status=False).filter(Frequency=1)
    else:
        Loan=Loans.objects.all().filter(Status=False).filter(Frequency=1).exclude(Loan_Collector_id=9).exclude(Loan_Collector_id=10)
    Total_Amount_To_Be_Collected = 0
    for i in Loan:
        Total_Amount_To_Be_Collected = Total_Amount_To_Be_Collected + i.installments_set.first().Installment_Due
    return render(request,'microfinance/All_Clients_List.html',{'loanee':Loan,'Staff':Staff_pk,'Total_Amount_To_Be_Collected':Total_Amount_To_Be_Collected})


@login_required(login_url="/accounts/login/")
def SMSselect(request):

    if request.method =='POST' and 'DateWiseSms' in request.POST:
        Date =request.POST.get('DatePaid')
        if Date == '':
            Date=timezone.now().date()    
        Loan = Loans.objects.filter(installments__Date_Paid=Date).distinct()
        dic ={}
        for l in Loan:
            Installment = Installments.objects.filter(Date_Paid = Date).filter(Loan =l).order_by('Date_Due','-Installment_To_Be_Paid').first()
            dic[l] = Installment.Installment_Paid
        return render(request,'microfinance/SMSLIST.html',{'Date':Date,'loan':Loan,'dic':dic})
    elif request.method =='POST' and 'CustomSmsSendList' in request.POST:
        Loan = Loans.objects.filter(Status=False)
        Acc = Accounts.objects.filter(loans__in= Loan).distinct()
        Client = Clients.objects.filter(accounts__in=Acc)  
        Date =timezone.now().date()
        return render(request,'microfinance/SMSLIST.html',{'Date':Date,'Client':Client})
    else:
        return render(request,'microfinance/Homepage.html')

@login_required(login_url="/accounts/login/")
def SMS(request):

    List = request.POST.getlist('Check')
    Date =request.POST.get('Date')
    if request.method=='POST' and 'Datewise' in request.POST:      
        for l in List:
            Loan = Loans.objects.get(pk=int(l))
            Installment = Installments.objects.filter(Loan=Loan).filter(Date_Paid=Date).order_by('Date_Due','-Installment_To_Be_Paid').first()
            x=str(Loan.Account.Client.Phone_no1)
            name = str(Loan.Account.Client.Name)
            Amount_Paid = str(Installment.Installment_Paid)    
            cid = str(Loan.Account.Client.pk) 
                
            from_num = 'whatsapp:+14155238886'
            to_num =  'whatsapp:+919810897802'
            TWILIO_ACCOUNT_SID='AC4d6c8a4366514eb2023d5bfec126db50'
            TWILIO_AUTH_TOKEN='cf743112770219fc1964b4b731beb6d5'
            client = twilioClient(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)  
            client.messages.create(body='Ess Arr Finance: Hi '+name+' this is to confirm that we have recieved a deposit of Rs.'+Amount_Paid+' in your account having client id: '+cid+' and loan id: '+l+' Thank you!',from_=from_num,to=to_num)
            return HttpResponse('done')
            #response = sendPostRequest(URL, 'WTI5CKKSHCQX0R2DPS0NPCRELPIWAANG', '062SNUSN0LQX2ZMG', 'stage',x, 'essarr', 'ESSARR FINANCE : '+y+', Amount paid: '+ Amount_Paid + ' on Date:' + Date )
    elif request.method == 'POST' and 'CustomSms' in request.POST:
        message = request.POST.get('message')
        for i in List:
            Client = Clients.objects.get(pk =int(i))
            x=str(Client.Phone_no1)
            #response = sendPostRequest(URL, 'WTI5CKKSHCQX0R2DPS0NPCRELPIWAANG', '062SNUSN0LQX2ZMG', 'stage',x, 'essarr', 'ESSARR FINANCE :'+message  )

    return redirect('microfinance:home')

@login_required(login_url="/accounts/login/")
def ViewGuarantorDocs(request,pk):
    Guarantor = Guarantor_Documents.objects.filter(Guarantor_id = pk)
    return render(request,'microfinance/ViewGuarantorDocs.html',{'GDocs':Guarantor})

@login_required(login_url="/accounts/login/")
def ViewClientDocs(request,pk):
    ClientDocs = Documents.objects.filter(Client_id = pk)
    return render(request,'microfinance/ViewClientDocs.html',{'CDocs':ClientDocs})
    

@login_required(login_url="/accounts/login/")
def Total_Amount_Collected_Report(request):
    Date=request.POST.get('Date')
    Installment=Installments.objects.filter(Date_Paid=Date).filter(Installment_Paid__gt=0).order_by('Loan__Loan_Collector')
    Loan =Loans.objects.filter(Loan_Date=Date)
    pen =Penalty.objects.filter(Penalty_Paid_Date=Date)
    Total_File_Charge=0
    Total_Collection=0
    tot_pen = 0
    filec ={}
    for p in pen:
        tot_pen = tot_pen + p.Penalty_Paid
    for l in Loan:
        Total_File_Charge+=l.Principle_Amount*l.File_Charge_Percent/100
        filec[l.pk] = l.Principle_Amount*l.File_Charge_Percent/100
    for i in Installment:
        Total_Collection+=i.Installment_Paid    
    return render(request,'microfinance/Total_Amnt_Collected_Report.html',{'tot_pen':tot_pen,'Date':Date,'Inst':Installment,'Total_coll':Total_Collection,'file_charge':Total_File_Charge,'pen':pen,'Loan':Loan,'filec':filec})

def EditClient(request,pk):
    Client = Clients.objects.all().get(pk=pk)
    if request.method=='POST':  

        
        form=EditClientDetail(request.POST,request.FILES,instance=Client)
        if form.is_valid():

           
            form.save()
            
        return redirect('microfinance:clientdetail',pk=pk)
    else:
        form=EditClientDetail(instance=Client)
        return render(request,'microfinance/EditClient.html',{'form':form})

@login_required(login_url="/accounts/login/")
def Client_Detail_Pdf(request,pk):    
    Client =Clients.objects.get(pk=pk)
    Account =Accounts.objects.get(Client=Client)
    Loan = Loans.objects.filter(Account =Account).distinct()

    if request.method == "POST":
        
        return render(request,'microfinance/pdfs/clientform.html',{'Client':Client,'Account':Account,'Loan':Loan})
    else:        
        return render(request,'microfinance/Client_Detail.html',{'Client':Client,'Account':Account,'Loan':Loan})

@login_required(login_url="/accounts/login/")
def Home(request):
    loan=Loans.objects.filter(reminder__lte=datetime.now()).filter(Status=False).distinct()    
    dic={}
    for i in Loans.objects.all().filter(reminder__lt=datetime.now()).filter(Status=False).distinct():
        if i.reminder < datetime.now().date():
            if i.installments_set.order_by('-Date_Due').first().Date_Due <datetime.now().date():
                i.reminder=datetime.now().date()            
            
            else:
                if i.installments_set.filter(Date_Due__gt=datetime.now()).filter(Date_Paid__isnull=True).order_by('Date_Paid').first() is not None:
                    i.reminder= i.installments_set.filter(Date_Due__gt=datetime.now()).filter(Date_Paid__isnull=True).order_by('Date_Paid').first().Date_Due
            i.remark ='None'
            i.save()
    for l in loan:
        i = Installments.objects.all().filter(Loan_id =l.pk).filter(Date_Due__lte=datetime.now()).filter(Installment_Due__gt=0).filter(Date_Paid__isnull=True).aggregate(Sum('Installment_Due')) 
        
        j= Installments.objects.all().filter(Loan_id =l.pk).filter(Date_Due__lte=datetime.now()).filter(Installment_Due=0).filter(Date_Paid__isnull=True).aggregate(Sum('Installment_To_Be_Paid'))
        if j['Installment_To_Be_Paid__sum'] and i['Installment_Due__sum']:
            i['Installment_Due__sum']+=j['Installment_To_Be_Paid__sum']
        if j['Installment_To_Be_Paid__sum'] and not i['Installment_Due__sum']:
            i['Installment_Due__sum']=j['Installment_To_Be_Paid__sum']
        if not j['Installment_To_Be_Paid__sum'] and not i['Installment_Due__sum']:
            i['Installment_Due__sum']=0
        dic[l.pk]=i['Installment_Due__sum']
    staff =Staff.objects.all().distinct()
    if request.method == 'POST':
        user_filter = LoanFilter(request.POST, queryset=loan)
        return render(request,'microfinance/Homepage.html',{'month':timezone.now().date().month,'loan':loan,'filter': user_filter,'users':staff,'dic':dic})
    else:
        return render(request,'microfinance/Homepage.html',{'month':timezone.now().date().month,'users':staff})

@login_required(login_url="/accounts/login/")
def DeleteIntsallment(request):
    if request.user.is_superuser: 
        List = request.POST.getlist('Check')
        for l in List:
            x=Installments.objects.filter(pk=l).delete()
        return redirect('microfinance:home')
        
        
    else:
        return HttpResponse('you dont have access to this page. Contact admin')

@login_required(login_url="/accounts/login/")
def EditInstallment(request,pk):
    if request.user.is_superuser: 
        Installment =Installments.objects.get(pk=pk)        
        if request.method=='POST':
            form=EditInstallmentDetail(request.POST,request.FILES)
            instance=form.save(commit=False)
            if form.is_valid():            
                instance.save()
                try:
                    Penal=Penalty.objects.get(Installment=Installment)
                    Penal.delete()
                    Installment.delete()
                except:
                    Installment.delete()
            return redirect('microfinance:loandetail',pk=instance.Loan.pk)
        else:
            form = form=EditInstallmentDetail(instance=Installment)
            return render(request,'microfinance/EditIInstallment.html',{'form':form})
            
    else:
        return HttpResponse('you dont have access to this page. Contact admin')

@login_required(login_url="/accounts/login/")
def InstallmentList(request,pk):
    if request.user.is_superuser: 
        loan=Loans.objects.get(pk=pk)
        Installment =Installments.objects.filter(Loan=loan)
        return render(request,'microfinance/IntsallmentList.html',{'Installment':Installment,'loan':loan})
    else:
        return HttpResponse('you dont have access to this page. Contact admin')

@login_required(login_url="/accounts/login/")
def AddInstallment(request,pk):
    if request.user.is_superuser:
        loan=Loans.objects.get(pk=pk)
        if request.method=="POST":
            form=AddInstallments(request.POST,request.FILES)
            instance=form.save(commit=False)
            instance.Loan=loan
            if form.is_valid():
                instance.save()
            return redirect('microfinance:loandetail',pk=instance.Loan.pk)
        else:
            form = form=AddInstallments()
            return render(request,'microfinance/EditIInstallment.html',{'form':form})
            
    else:
        return HttpResponse('you dont have access to this page. Contact admin')


@login_required(login_url="/accounts/login/")
def Week_Chart_List(request):
    Staff_pk=int(request.POST.get('name'))
    Weekday = int(request.POST.get('Weekday'))  
    sdate= (datetime.now() - timedelta(days=1)).date()
    edate= (datetime.now() - timedelta(days=7)).date()
    dd = [sdate - timedelta(days=x) for x in range((sdate-edate).days)]
    lon = Loans.objects.none()
    if Staff_pk !=0 and Weekday !=0:
        Loan=Loans.objects.all().filter(Loan_Collector_id=Staff_pk).filter(Status=False).filter(Frequency=2).filter(First_Due_Date__week_day = Weekday)
        lon = Loans.objects.all().filter(Loan_Collector_id=Staff_pk).filter(Status=False).filter(Frequency=2).exclude(First_Due_Date__week_day = Weekday)
    elif Staff_pk != 0 and Weekday == 0:
        Loan=Loans.objects.all().filter(Loan_Collector_id=Staff_pk).filter(Status=False).filter(Frequency=2)
   
    elif Staff_pk == 0 and Weekday != 0:
        Loan=Loans.objects.all().filter(Status=False).filter(Frequency=2).filter(First_Due_Date__week_day = Weekday)
        lon=Loans.objects.all().filter(Status=False).filter(Frequency=2).exclude(First_Due_Date__week_day = Weekday)
    else:
        Loan=Loans.objects.all().filter(Status=False).filter(Frequency=2)

    dic ={}
    dic2 ={}
    Dic1={0:0,1:0,2:0,3:0,4:0,5:0,6:0}
    Dic2={0:0,1:0,2:0,3:0,4:0,5:0,6:0} 
    Def1=0
    Def2=0
    x=Loans.objects.none()
    if lon:
        for i in dd:
            for j in lon.filter(First_Due_Date__week_day = (i.isoweekday()%7)+1):
                if j.installments_set.filter(Date_Paid__isnull=False).order_by('-Date_Paid','-Date_Due').first():
                    if j.installments_set.filter(Date_Paid__isnull=False).order_by('-Date_Paid','-Date_Due').first().Date_Paid < i:
                        print(j.pk,i,i.weekday(),j.First_Due_Date,j.First_Due_Date.weekday())
                        x|= lon.filter(pk=j.pk)     
                else:   
                    x|= lon.filter(pk=j.pk)  
                    
    if x:   
        for l in x:
        
            Def1 = Def1 + l.installments_set.first().Installment_Due
            totalPending =0
            inst =Installments.objects.filter(Loan=l).filter(Q(Date_Paid__lte=datetime.now())|Q(Date_Due__lte=datetime.now())).distinct()
            for i in inst:
                            
                totalPending  = totalPending + (i.Installment_Due - i.Installment_Paid)
            dic2[l.pk]=totalPending
            Def2 = Def2 + totalPending
            if totalPending <= 0:
                x=x.exclude(pk=l.pk)
    for l in Loan:

        Dic1[int(l.installments_set.first().Date_Due.weekday())] = Dic1[int(l.installments_set.first().Date_Due.weekday())] + l.installments_set.first().Installment_Due
        totalPending =0
        inst =Installments.objects.filter(Loan=l).filter(Q(Date_Paid__lte=datetime.now())|Q(Date_Due__lte=datetime.now())).distinct()
        for i in inst:
            Dic2[int(i.Date_Due.weekday())] =Dic2[int(i.Date_Due.weekday())] + (i.Installment_Due-i.Installment_Paid)             
            totalPending  = totalPending + (i.Installment_Due - i.Installment_Paid)
        dic[l.pk]=totalPending
    
    if int(Weekday) == 0:               
        return render(request,'microfinance/Week_Chart.html',{'Loan':Loan,'dic':dic,'Staff':Staff_pk,'Total':Dic1,'TotalPen':Dic2})
    else:
        
        return render(request,'microfinance/week_chart2.html',{'Loan':Loan,'dic':dic,'dic2':dic2,'Staff':Staff_pk,'Total':Dic1,'TotalPen':Dic2,'Def1':Def1,'Def2':Def2,'lon':x})

@login_required(login_url="/accounts/login/")
def PrintInstallmentsPDF(request):
    Lid=request.POST.get('printlid')
    inst= Installments.objects.filter(Loan_id = Lid)
    return render(request,'microfinance/pdfs/installments.html',{'inst':inst})


@login_required(login_url="/accounts/login/")
def optimizeimg(request):
    Client =Clients.objects.all()
    for j in Client:
        try:
           
            # image = Image.open(i.Image.path)
            # image.save(i.Image.path,quality=20,optimize=True)
            i = Image.open(j.Image)
            thumb_io = BytesIO()
            i.save(thumb_io, format='JPEG', quality=20)
            inmemory_uploaded_file = InMemoryUploadedFile(thumb_io, None, 'foo.jpeg', 
                                              'image/jpeg', thumb_io.tell(), None)
            j.Image = inmemory_uploaded_file
            j.save()
        except:
            print(j.pk)
    return HttpResponse('Images OP')

@login_required(login_url="/accounts/login/")
def EditLoan(request,pk):
    if request.user.is_superuser: 
        Loan=Loans.objects.get(pk=pk)
        acc=Loan.Account.pk
        gk=Loan.Guarantor.pk
                
        if request.method=='POST' and 'edit' in request.POST:
            form=EditLoanDetail(instance=Loan)
            return render(request,'microfinance/EditLoan.html',{'form':form})
        if 'changeLoan' in request.POST:  
            form=EditLoanDetail(request.POST)
            instance=form.save(commit=False)
            if form.is_valid():
                
                instance.Account=Loan.Account
                instance.Guarantor=Loan.Guarantor
                instance.save()
                Installment = (instance.Principle_Amount + (instance.Principle_Amount/100*instance.Intrest_Rate))/instance.No_Of_Installments
                if instance.Frequency !=2 :
                    Inst =round(Installment,1)
                    Installments_Inst = Installments(Installment_Paid = 0, Loan = instance, Date_Due = instance.First_Due_Date, Installment_Due = Inst,Installment_To_Be_Paid=Inst,Pending_Amount=Inst )
                else:
                    Inst = round(Installment,1)
                    Installments_Inst = Installments(Installment_Paid = 0, Loan = instance, Date_Due = instance.First_Due_Date, Installment_Due = round(Inst*7),Installment_To_Be_Paid=round(Inst*7),Pending_Amount=round(Inst*7) )
                Installments_Inst.save()   
                
                if instance.Frequency == 1:
                    Date_Due = instance.First_Due_Date 
                    for i in range(1,instance.No_Of_Installments):
                        Inst = Installment
                        Date_Due = Date_Due + timedelta(1)
                        Installments_Inst = Installments(Installment_Paid = 0, Loan = instance,Date_Due = Date_Due, Installment_Due = round(Installment,1),Installment_To_Be_Paid=round(Installment,1),Pending_Amount=round(Installment,1) )
                        Installments_Inst.save()
                if instance.Frequency == 2:
                    Date_Due = instance.First_Due_Date 
                    Extra_Days = instance.No_Of_Installments % 7
                    for i in range(1,int(instance.No_Of_Installments/7)):
                        Inst = Installment
                        Date_Due = Date_Due + timedelta(7)
                        Installments_Inst = Installments(Installment_Paid = 0, Loan = instance, Date_Due = Date_Due, Installment_Due = round(Inst*7),Installment_To_Be_Paid=round(Inst*7),Pending_Amount=round(Inst *7))
                        Installments_Inst.save()
                    if Extra_Days>0:
                        Inst = Installment
                        Date_Due = Date_Due + timedelta(Extra_Days)
                        Installments_Inst = Installments(Installment_Paid = 0, Loan = instance,Date_Due = Date_Due, Installment_Due = round(Inst*Extra_Days),Installment_To_Be_Paid=round(Inst*Extra_Days),Pending_Amount=round(Inst *Extra_Days))
                        Installments_Inst.save()
                if instance.Frequency == 3:
                    Date_Due = instance.First_Due_Date 
                    for i in range(1,int(instance.No_Of_Installments)):
                        Inst = round(Installment,1)
                        Date_Due = Date_Due + relativedelta(months=1)
                        Installments_Inst = Installments(Installment_Paid = 0, Loan = instance,Date_Due = Date_Due, Installment_Due =round(Installment,1),Installment_To_Be_Paid=round(Installment,1),Pending_Amount=round(Installment,1) )
                        Installments_Inst.save()
                
            return redirect('microfinance:clientdetail' ,pk=Loan.Account.Client.pk)
   
        if 'del' in request.POST:
            Pen =Penalty.objects.filter(Loan=Loan).delete()
            inst=Installments.objects.filter(Loan=Loan).delete()
            Loan.delete()
            return redirect('microfinance:clientdetail' ,pk=Loan.Account.Client.pk)
            
    else:
        return HttpResponse('you dont have access to this page. Contact admin')


    
@login_required(login_url="/accounts/login/")
def temporary(request):
    inst =  Installments.objects.filter(Date_Due__lte ="2020-10-24").distinct()
    inst2 =  Installments.objects.filter(Date_Paid__lte ="2020-10-24").distinct()
    Loan = Loans.objects.filter(installments__in=inst).distinct()
    Amnt_Collected = {}
    Amnt_To_Be_Collected = {}
    AmntCollected=AmntToBeCollected=0
    inst3 = Installments.objects.filter(Loan__in = Loan).exclude(id__in=inst).distinct()
    inst4 = Installments.objects.filter(Loan__in = Loan).exclude(id__in=inst2).distinct()
    Amnt_Collected2 = {}
    Amnt_To_Be_Collected2 = {}
    AmntCollected2=AmntToBeCollected2=0    
    amnt_pen ={}
    for i in Loan:
        Amnt_To_Be_Collected[i.pk]=inst.filter(Loan = i).aggregate(Sum('Installment_Due')) 
        Amnt_Collected[i.pk]=inst2.filter(Loan = i).aggregate(Sum('Installment_Paid'))
        if Amnt_To_Be_Collected[i.pk]["Installment_Due__sum"]:
            AmntToBeCollected = AmntToBeCollected + Amnt_To_Be_Collected[i.pk]["Installment_Due__sum"] 
            amnt_pen[i.pk]=Amnt_To_Be_Collected[i.pk]["Installment_Due__sum"]
        if Amnt_Collected[i.pk]["Installment_Paid__sum"]:
            AmntCollected = AmntCollected + Amnt_Collected[i.pk]["Installment_Paid__sum"]
            amnt_pen[i.pk]-= Amnt_Collected[i.pk]["Installment_Paid__sum"]
        Amnt_To_Be_Collected2[i.pk]=inst3.filter(Loan = i).aggregate(Sum('Installment_Due')) 
        Amnt_Collected2[i.pk]=inst4.filter(Loan = i).aggregate(Sum('Installment_Paid'))
        if Amnt_Collected2[i.pk]["Installment_Paid__sum"]:
            AmntCollected2 = AmntCollected2 + Amnt_Collected2[i.pk]["Installment_Paid__sum"]
        if Amnt_To_Be_Collected2[i.pk]["Installment_Due__sum"]:
            AmntToBeCollected2 = AmntToBeCollected2 + Amnt_To_Be_Collected2[i.pk]["Installment_Due__sum"] 
            amnt_pen[i.pk]+=Amnt_To_Be_Collected2[i.pk]["Installment_Due__sum"]
    Loan2 = Loan.filter(Status =True)
    Loan = Loan.exclude(id__in =Loan2)
    return render(request,'microfinance/temp.html',{'amnt_pen':amnt_pen,'amnt_collected':Amnt_Collected,'amnt_collected2':Amnt_Collected2,'Loan':Loan,'amntcollected':AmntCollected,'amnttobecollected':AmntToBeCollected,'amnt_to_be_collected':Amnt_To_Be_Collected,'amnttobecollected2':AmntToBeCollected2,'amntcollected2':AmntCollected2,'Loan2':Loan2})






@login_required(login_url="/accounts/login/")
def Add_Guarantor_IntrestLoan(request,pk):
    if request.method == 'POST':
        form=AddGuarantor(request.POST,request.FILES)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.save()
            return redirect('microfinance:addguarantordocs_intrestloan', pk=pk, sk=instance.pk)
    else:
        form=AddGuarantor()     
    return render(request,'microfinance/Add_Guarantor.html',{'form':form})


@login_required(login_url="/accounts/login/")
def Add_Guarantor_Docs_IntrestLoan(request,pk,sk):
    if request.method == 'POST':        
        form=AddGuarantorDocs(request.POST,request.FILES)      
        instance=form.save(commit=False)
        instance.Guarantor_id = sk
        instance.save()
        if 'k' in request.POST:            
            return redirect('microfinance:addguarantordocs_intrestloan', pk=pk,sk=sk)
        if 'l' in request.POST:    
           pass  
           return redirect('microfinance:addloan_intrestloan', pk=pk,  sk=sk) 
    else: 
        form=AddGuarantorDocs()     
    return render(request,'microfinance/Add_Guarantor_Docs.html',{'form':form})



@login_required(login_url="/accounts/login/")
def Add_Loan_IntrestLoan(request,pk, sk):
        if request.method == 'POST':
            form=AddLoan_IntrestLoan(request.POST,request.FILES)
            instance=form.save(commit=False)
            client =Clients.objects.get(pk=pk)
            acc = Accounts.objects.get(Client=client)
            instance.Account =acc
            instance.Guarantor_id = sk
            pass
            if form.is_valid():            
                instance.Intrest_Generated = instance.Principle_Amount * instance.Intrest_Rate/100
                instance.Balance_Principle_Amount = instance.Principle_Amount
                instance.save()
            return redirect('microfinance:clientdetail' ,pk=pk)
        else: 
            form=AddLoan_IntrestLoan()     
        return render(request,'microfinance/Add_Loan_intrestloan.html',{'form':form})


@login_required(login_url="/accounts/login/")
def Loan_Detail_IntrestLoan(request,pk): #IntestLoan pk

    Iloan = IntrestLoans.objects.get(pk=pk)
    datee = Iloan.First_Due_Date
    datev = Iloan.First_Due_Date+relativedelta(days=1)
    return HttpResponse((datev.year-datee.year)*12 + (datev.month-datee.month))
    return render(request,'microfinance/Loan_Detail_IntrestLoan.html',{'form':form})