from django import forms
from .models import Etudiant
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['nom', 'matricule']


class TeacherCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_staff = forms.BooleanField(required=False, initial=True, label="Compte enseignant (is_staff)")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'is_staff')
