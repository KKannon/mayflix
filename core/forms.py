from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'profile']
        
        labels = {
            'name': 'Nome',
            'profile': 'URL da Imagem de Perfil',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Jhon Potato'}),
            'profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder':'https://i.imgur.com/J2NT0Vd.png'}),
        }