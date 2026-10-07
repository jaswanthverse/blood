from django import forms
from django.utils import timezone
from .models import BloodUnit, Reservation, IssueRecord


class BloodUnitForm(forms.ModelForm):
    class Meta:
        model = BloodUnit
        fields = ['blood_group', 'component_type', 'collection_date']
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'component_type': forms.Select(attrs={'class': 'form-select'}),
            'collection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_collection_date(self):
        date = self.cleaned_data['collection_date']
        if date > timezone.localdate():
            raise forms.ValidationError("Collection date can't be in the future.")
        return date


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['patient_name', 'ward_or_department']
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient name'}),
            'ward_or_department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ward / Department (optional)'}),
        }


class IssueForm(forms.ModelForm):
    class Meta:
        model = IssueRecord
        fields = ['issued_to', 'notes']
        widgets = {
            'issued_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issued to'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class InventoryFilterForm(forms.Form):
    blood_group = forms.ChoiceField(
        choices=[('', 'All groups')] + list(BloodUnit.BloodGroup.choices),
        required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    component_type = forms.ChoiceField(
        choices=[('', 'All components')] + list(BloodUnit.Component.choices),
        required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All statuses')] + list(BloodUnit.Status.choices),
        required=False, widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Search unit ID...'})
    )