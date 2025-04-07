from sys import intern

from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from pyexpat.errors import messages

from .models import Money,Loan
from  datetime import  datetime
from django.utils import timezone
import pytz
import numpy as np
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def index(request):
    return render(request, 'index.html')

beijing_tz = pytz.timezone('Asia/Shanghai')
utc_now = timezone.now()
beijing_time = utc_now.astimezone(beijing_tz)



#求今年、当月，当天的消费
def addition(year,mounth,day):

    year_total=0
    for i in year:
        year_total=i.Consumption+year_total

    mounth_total = 0
    for i in mounth:
         mounth_total=i.Consumption+mounth_total

    day_total = 0
    for i in day:
         day_total=i.Consumption+day_total
         #print(i)
    return year_total,mounth_total,day_total



#获取今年、当月、当天的消费对象
def year_or_month_or_day():

    start_of_year = datetime(beijing_time.year, 1, 1)
    end_of_year = datetime(beijing_time.year, 12, 31)


    start_of_mounth = datetime(beijing_time.year, beijing_time.month, 1)
    if beijing_time.month == 12:
        end_of_month = datetime(beijing_time.year + 1, 1, 1) - timezone.timedelta(days=1)
    else:
        end_of_month = datetime(beijing_time.year, beijing_time.month + 1, 1) - timezone.timedelta(days=1)

    same_day=datetime(beijing_time.year, beijing_time.month, beijing_time.day)
    #print(beijing_time.year, beijing_time.month, beijing_time)

    year_monery=Money.objects.filter(Consumption_time__range=(start_of_year, end_of_year))
    mounth_monery=Money.objects.filter(Consumption_time__range=(start_of_mounth,end_of_month))
    day_monery = Money.objects.filter(Consumption_time__range=(same_day,same_day))

    return addition(year_monery,mounth_monery,day_monery)


def index2(request):

    #print(beijing_time.year)
    dic = {}
    for i in Money.objects.all():

        if str(i.Consumption_time) not in dic:
            dic[str(i.Consumption_time)] = i.Consumption
        elif str(i.Consumption_time)  in dic:
            dic[str(i.Consumption_time)] =  dic[str(i.Consumption_time)] + i.Consumption

    all = {}
    #消费
    all['monery'] = dic

    #年月日消费统计
    all['year'],all['mounth'],all['day']=year_or_month_or_day()

    other=Money.objects.filter(Consumption_type=0)
    consumption=Money.objects.filter(Consumption_type=1)
    dine=Money.objects.filter(Consumption_type=2)

    #print(other,consumption,dine)

    d = np.array([len(other),len(consumption),len(dine)])
    percentages  = np.around((d/np.sum(d))*100)
    #print(percentages)
    total=0
    #总负债
    for i in Loan.objects.all():
        total=total+i.principal+i.interest
    #print(total)
    all['loan']=total
    all['percentages']=percentages

    #print(all)
    return render(request, 'main.html',all)

def addexpense(request):
    return render(request, 'addexpense.html')

def submit_form(request):
    if request.method == 'POST':
        expense = request.POST.get('monery')
        text = request.POST.get('text')
        ty= request.POST.get('type')
        if not ty:
            ty='0'
        mg=1
        try:
            expense = float(Decimal(expense).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        except:
            message='请入输入数字!!!'
            mg=0

        #Money.objects.create(Consumption=expense, OtherInfo=text, Consumption_type=ty)
        try:
            Money.objects.create(Consumption=expense,OtherInfo=text,Consumption_type=ty)
        except:
            message="录入失败!!!"
            mg=0

        if mg !=0:
            message="录入成功"

        context={
            "mess": message,
            'mg':mg,
        }

        return render(request, 'addexpense.html',context)

    return render(request, 'addexpense.html')

#债务明细
def debts(request):
    liss = []
    lis = []


    f=0
    for i in Loan.objects.all():
        f=f+1
        lis.append(f)
        lis.append(i.name)
        lis.append(i.principal)
        lis.append(i.interest)
        #print(type(i.interest))
        #总额度
        lis.append(i.interest+i.principal)
        #每月待还
        lis.append(i.Tobepaid)

        #分期金额
        #lis.append(((i.interest+i.principal)/12).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        liss.append(lis)
        lis = []


    dic1 = {'nobody':liss}
    #print(dic1)

    return render(request, 'detailOfdebts.html',dic1)

#负债
def adddebt(request):
    return render(request,'adddebt.html')

#负债
def proc(request):
    if request.method == 'POST':
        #利息
        interest = request.POST.get('interest')
        #本金
        debtAmount = request.POST.get('debtAmount')
        debtorName = request.POST.get('debtorName')
        needpaid=request.POST.get('Tobepaid')
        mg=1
        #print(debtAmount)

        if not interest or not debtorName or not debtAmount or not needpaid:
            message='不要留空!!!'
            mg = 0

        try:
            debtAmount= float(Decimal(debtAmount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            interest= float(Decimal(interest).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            if debtAmount <= interest:
                message='总利息大于等于本金！！'
                mg=0
            elif debtAmount == 0:
                message = '本金等于0！！'
                mg=0
        except:
            message='请入输入数字!!!'
            mg=0

        if mg != 0:
            try:
                Loan.objects.create(name=debtorName,principal=debtAmount,interest=interest,Tobepaid=needpaid)
            except:
                message="录入失败!!!"
                mg=0

            if mg !=0:
                message="录入成功"

        context={
            "mess": message,
            'mg':mg,
        }

        return render(request, 'adddebt.html',context)

    return render(request, 'adddebt.html')




