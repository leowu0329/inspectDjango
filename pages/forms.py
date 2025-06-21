from django import forms
from .models import Case

class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = [
            'inspection_type', 'sale_type', 'customer', 'department', 'date', 
            'time', 'work_order_number', 'operator', 'drawing_revision', 
            'part_number', 'part_name', 'quantity', 'inspector', 
            'defect_category', 'defect_description', 'disposition', 
            'inspection_hours'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        } 