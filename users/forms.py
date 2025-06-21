from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
	class Meta(UserCreationForm.Meta):
		model = CustomUser
		fields = ('username', 'email', ) # new

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', ) # new

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'personal_id', 'birthday',
            'phone', 'mobile',
            'work_area',
            'city', 'district', 'village', 'neighbor',
            'street', 'section', 'lane', 'alley',
            'number', 'floor',
            'identity_type'
        ]
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }
