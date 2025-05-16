from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('PAN', 'PAN Card'),
        ('AADHAAR', 'Aadhaar Card'),
        ('BANK', 'Bank Details / Passbook'),
        ('FORM16A', 'Form 16A'),
        ('INVOICE', 'Sales Invoices / Register'),
        ('PL', 'Profit & Loss Statement'),
        ('BS', 'Balance Sheet'),
        ('SALARY', 'Salary Slip'),
        ('FORM16B', 'Form 16B'),
        ('RENT', 'Rent Agreement'),
        ('CAPITAL_GAIN', 'Capital Gain Details'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.document_type}"

class FiledReturn(models.Model):
    RETURN_TYPES = [
        ('GSTR-1', 'GSTR-1'),
        ('GSTR-3B', 'GSTR-3B'),
        ('IT', 'Income Tax'),
    ]
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    return_type = models.CharField(max_length=10, choices=RETURN_TYPES)
    due_date = models.DateField()
    filed_date = models.DateField(auto_now_add=True)
    filed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='filed_by_ca')

    class Meta:
        unique_together = ('client', 'return_type', 'due_date')

    def __str__(self):
        return f"{self.client.username} - {self.return_type} filed on {self.filed_date}"

