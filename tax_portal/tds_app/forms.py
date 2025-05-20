from django import forms

TDS_SECTIONS = [
    ('194C', '194C - Contractor'),
    ('194J', '194J - Professional Fees'),
    ('194H', '194H - Commission or Brokerage'),
]

class TDSForm(forms.Form):
    section = forms.ChoiceField(
        choices=TDS_SECTIONS,
        label="TDS Section",
        widget=forms.Select()
    )
    amount = forms.DecimalField(
        label="Amount Paid",
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Enter amount',
                'step': '0.01'
            }
        )
    )
    pan_available = forms.ChoiceField(
        choices=[('yes', 'Yes'), ('no', 'No')],
        label="Is PAN Available?",
        widget=forms.RadioSelect()
    )

    