from django.db import models
import time
from django.utils import timezone

class Money(models.Model):
    method_choices = (
        (0,'其他'),
        (1,'购物'),
        (2,'餐饮'),
        (3,'还款')
    )


    Consumption_time = models.DateField('消费时间',default=timezone.now)
    Consumption = models.DecimalField('消费金额',max_digits=7, decimal_places=2)
    OtherInfo = models.TextField('额外说明',null=True,blank=True)
    Consumption_type = models.SmallIntegerField('消费类型',choices=method_choices,default=0)

    def __str__(self):
        return f'money-{time.time()}'

class Loan(models.Model):
    #debt = models.DecimalField('负债',max_digits=12, decimal_places=2)
    #债务名称
    name = models.TextField('债务名称')
    #本金
    principal = models.DecimalField('借款总金额',max_digits=7, decimal_places=2)
    #利息
    #interest = models.DecimalField('借款利息',max_digits=7, decimal_places=2)
    #月还款
    Tobepaid = models.DecimalField('每月待还',max_digits=7, decimal_places=2)

    def __str__(self):
        return f'loan-{time.time()}'

class Reap(models.Model):

    monery = models.DecimalField('收入金额',max_digits=7,decimal_places=2)
    Consumption_time = models.DateField('收入时间', default=timezone.now)
    def __str__(self):
        return f'reap-{time.time()}'