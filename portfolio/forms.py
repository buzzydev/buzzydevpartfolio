import time

from django import forms
from django.core.signing import BadSignature, TimestampSigner

from .models import ContactMessage

signer = TimestampSigner(salt="contact-form")


def new_token():
    return signer.sign(str(int(time.time())))


class ContactForm(forms.ModelForm):
    # Spam himoyasi: honeypot (botlar to'ldiradi) + imzolangan vaqt tokeni
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))
    token = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "subject": forms.TextInput(attrs={"placeholder": "What is this about?"}),
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": "Tell me about your project"}),
        }

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("Spam detected.")
        return ""

    def clean_token(self):
        try:
            issued = int(signer.unsign(self.cleaned_data["token"], max_age=3600))
        except (BadSignature, ValueError):
            raise forms.ValidationError("The form expired. Reload the page and try again.")
        if time.time() - issued < 3:
            raise forms.ValidationError("That was too fast. Please try again.")
        return self.cleaned_data["token"]
