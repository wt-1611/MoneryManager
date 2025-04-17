from sys import intern

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.db.models import Q
from numpy.ma.core import append
from pyexpat.errors import messages
from django.db.models import Sum
from .models import Money,Loan,Reap
from  datetime import  datetime
from django.utils import timezone
import pytz
import numpy as np
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages



@login_required
def index(request):
    return render(request, 'index.html')



#求今年、当月，当天的消费
def addition(year,mounth,day,total):

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

    t=0
    for r in total:
        t = t + r.monery
    #print(total)

    return year_total,mounth_total,day_total,t


same_day=''
#获取今年、当月、当天的消费对象
def year_or_month_or_day():
    beijing_tz = pytz.timezone('Asia/Shanghai')
    utc_now = timezone.now()
    beijing_time = utc_now.astimezone(beijing_tz)
    global same_day
    same_day = beijing_time.strftime("%Y-%m-%d")
    start_of_year = datetime(beijing_time.year, 1, 1)
    end_of_year = datetime(beijing_time.year, 12, 31)


    start_of_mounth = datetime(beijing_time.year, beijing_time.month, 1)
    if beijing_time.month == 12:
        end_of_month = datetime(beijing_time.year + 1, 1, 1) - timezone.timedelta(days=1)
    else:
        end_of_month = datetime(beijing_time.year, beijing_time.month + 1, 1) - timezone.timedelta(days=1)

    #same_day=datetime(beijing_time.year, beijing_time.month, beijing_time.day)


    print(same_day)

    # total=0
    # for r in Reap.objects.filter(Consumption_time__range=(start_of_mounth,end_of_month)):
    #     total = total + r.monery
    # print(total)

    total=Reap.objects.filter(Consumption_time__range=(start_of_mounth, end_of_month))
    year_monery=Money.objects.filter(Consumption_time__range=(start_of_year, end_of_year))
    mounth_monery=Money.objects.filter(Consumption_time__range=(start_of_mounth,end_of_month))
    #day_monery = Money.objects.filter(Consumption_time__range=(same_day,same_day))
    day_monery = Money.objects.filter(Consumption_time=same_day)

    return addition(year_monery,mounth_monery,day_monery,total)

@login_required
def index2(request):


    all = {}
    # 年月日消费统计
    all['year'], all['mounth'], all['day'], all['inmonery'] = year_or_month_or_day()



    timlis=[]
    xiaofei=[]


    result = Money.objects.values('Consumption_time').annotate(total_amount=Sum('Consumption')).order_by('Consumption_time')

    for i in result:
        #rint(i)
        timlis.append(str(i['Consumption_time']))
        xiaofei.append(float(i['total_amount']))

        #shengyu.append(all['inmonery']-i['total_amount'])



    #print(timlis)
    #print(xiaofei)
    #print(shengyu)

    line_chart_data = {
        'series': xiaofei, #[30, 40, 35, 50, 49, 60, 70],
        'categories': timlis,#['1日', '2日', '3日', '4日', '5日', '6日', '7日']
        #'shenyu': shengyu,
    }
    #消费
    all['line_chart_data'] = line_chart_data

    #print(dic)



    other=Money.objects.filter(Consumption_type=0)
    consumption=Money.objects.filter(Consumption_type=1)
    dine=Money.objects.filter(Consumption_type=2)
    m=Money.objects.filter(Consumption_type=3)
    all_monery=[other,consumption,dine,m]
    #print(other,consumption,dine)
    #print([len(other),len(consumption),len(dine),len(m)])
    # total=0
    # for r in Reap.objects.all():
    #     total = total + r.monery

    # all['inmonery']=total
    mlis=[]
    for cc in all_monery:
        ten=0
        for c in cc:
            #print(c.Consumption)
            ten=ten+c.Consumption
        # total=total-ten
        #其他，购物，餐饮，还款
        mlis.append(float(ten))
    #print(mlis)
    mlis.append(float(all['inmonery'] - all['mounth']))

    # mlis.append(float(total))

    # 准备饼图数据
    pie_data = {
        'series': mlis,  #[700, 500, 400, 600, 300, 100],
        'labels': ['其他','购物','餐饮','还款','剩余'], #['Chrome', 'Edge', 'FireFox', 'Safari', 'Opera', 'IE'],
        'colors': ['#0d6efd', '#20c997', '#ffc107', '#d63384','#adb5bd'] #'#6f42c1', '#adb5bd']
    }
    all['pie_data']=pie_data
    #print(mlis)

    #d = np.array([len(other),len(consumption),len(dine),len(m)])
    #percentages  = np.around((d/np.sum(d))*100)
    #print(percentages)
    total=0
    #总负债
    for i in Loan.objects.all():
        total=total+i.principal+i.interest
    #print(total)
    all['loan']=total

    all['today']=same_day

    #all['percentages']=percentages
    #print(percentages)

    #print(all)
    return render(request, 'main.html',all)



@login_required
def addexpense(request):
    return render(request, 'addexpense.html')
@login_required
def submit_form(request):
    if request.method == 'POST':
        expense = request.POST.get('monery')
        text = request.POST.get('text')
        ty= request.POST.get('type')
        dueDate = request.POST.get('dueDate')

        #print(dueDate)


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
            Money.objects.create(Consumption=expense,OtherInfo=text,Consumption_type=ty,Consumption_time=dueDate)
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
@login_required
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
@login_required
def adddebt(request):
    return render(request,'adddebt.html')

#负债
@login_required
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


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index2')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def addreap(requset):
    return render(requset,'addreap.html')

@login_required
def reap(request):
    if request.method == 'POST':
        mg=1
        message='录入成功！！'
        monery = request.POST.get('monery')
        monery = float(Decimal(monery).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


        try:
            Reap.objects.create(monery=monery)
        except:
            message = "录入失败!!!"
            mg = 0

        context={
            "mess": message,
            'mg':mg,
        }
        return render(request, 'addreap.html',context)

    return render(request, 'addreap.html')

