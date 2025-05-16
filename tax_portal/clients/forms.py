from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and not file.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        if file.size > 5*1024*1024:  # 5MB limit, optional
            raise forms.ValidationError("File size must be under 5MB.")
        return file
