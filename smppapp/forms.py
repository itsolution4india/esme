from django import forms

class SMPPConnectionForm(forms.Form):
    ip = forms.GenericIPAddressField(label="SMPP Server IP")
    port = forms.IntegerField(label="Port", initial=5050)
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    system_type = forms.CharField(label="System Type", required=False, max_length=50)
    bind_mode = forms.ChoiceField(choices=[('TX', 'Transmitter'), ('RX', 'Receiver'), ('TRX', 'Transceiver')])

class SendSMSForm(forms.Form):
    sender = forms.CharField(label="Sender ID", max_length=20)
    recipient = forms.CharField(label="Recipient Number", max_length=15)
    message = forms.CharField(label="Message", widget=forms.Textarea)
    entity_id = forms.CharField(label="Entity ID", max_length=50)
    template_id = forms.CharField(label="Template ID", max_length=50)

