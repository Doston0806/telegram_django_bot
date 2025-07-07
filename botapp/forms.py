from django import forms
from .models import QarzBerdim ,QarzOldim

class QarzForm(forms.ModelForm):
    class Meta:
        model = QarzBerdim  # yoki QarzOldim
        fields = ['amount']  # faqat pulni tahrirlashga ruxsat
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class QarzOldimForm(forms.ModelForm):
    class Meta:
        model = QarzOldim
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }