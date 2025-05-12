from django.urls import path
from .views import connect_smpp, send_sms_view

urlpatterns = [
    path('', connect_smpp, name='connect_smpp'),
    path('send_sms/', send_sms_view, name='send_sms'),
]
