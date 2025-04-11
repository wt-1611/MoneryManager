from django.contrib import admin
from django.urls import include, path
from . import views
urlpatterns = [
    path('rec/', views.index,name='index'),
    path('',views.index2,name='index2'),
    path('admin/', admin.site.urls),
    path('addexpense/',views.addexpense,name='addexpense'),
    path('submit_form/',views.submit_form,name='submit_form'),
    path('debts/',views.debts,name='debts'),
    path('proc/',views.proc,name='proc'),
    path('adddebt/',views.adddebt,name='adddebt'),
    path('login/', views.login, name='login'),
    path('addreap/',views.addreap,name='addreap'),
    path('reap/',views.reap,name='reap')
]