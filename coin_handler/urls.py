from django.urls import path

from . import views

app_name = 'coin_handler'
urlpatterns = [
    path('index/<int:person_id>', views.index, name='index'),
    path('log/<int:person_id>', views.log, name='log'),
    path('send_cash/<int:person_id>', views.send_cash, name='send cash'),
    path('process_cash_sending/<int:person_id>', views.process_cash_sending, name='process cash sending'),
    path('login', views.login, name='login'),
    path('process_login', views.process_login, name='process login'),
]
