from django.shortcuts import render, redirect
from .forms import SMPPConnectionForm, SendSMSForm
from .smpp_utils import smpp_bind, send_sms
from .smpp_utils import smpp_bind
import smpplib

smpp_client = None  # Global client instance

def connect_smpp(request):
    global smpp_client
    connection_success = False

    if request.method == "POST":
        form = SMPPConnectionForm(request.POST)
        if form.is_valid():
            ip = form.cleaned_data['ip']
            port = form.cleaned_data['port']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            system_type = form.cleaned_data['system_type']
            bind_mode = form.cleaned_data['bind_mode']
            print("bind_mode", bind_mode)

            # Try to establish SMPP connection and bind
            smpp_client = smpp_bind(ip, port, username, password, system_type, bind_mode)

            # Check if the connection was successful
            if isinstance(smpp_client, smpplib.client.Client):
                print(f"SMPP Client Created and Bound: {smpp_client}")
                connection_success = True
            else:
                print(f"SMPP Connection Failed: {smpp_client}")
                return render(request, 'index.html', {"form": form, "error": smpp_client})

    else:
        form = SMPPConnectionForm()

    return render(request, "index.html", {"form": form, "connection_success": connection_success})

def send_sms_view(request):
    global smpp_client

    if request.method == "POST":
        form = SendSMSForm(request.POST)
        if form.is_valid() and smpp_client:
            sender = form.cleaned_data['sender']
            recipient = form.cleaned_data['recipient']
            message = form.cleaned_data['message']
            entity_id = form.cleaned_data['entity_id']
            template_id = form.cleaned_data['template_id']

            response = send_sms(smpp_client, sender, recipient, message, entity_id, template_id)

            return render(request, 'send_sms.html', {"form": form, "success": response})
    else:
        form = SendSMSForm()

    return render(request, "send_sms.html", {"form": form})