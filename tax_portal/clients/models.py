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
    
class ReturnFiling(models.Model):
    RETURN_TYPES = [
        ('GSTR1', 'GSTR-1'),
        ('GSTR3B', 'GSTR-3B'),
        ('IT', 'Income Tax'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='returns')
    return_type = models.CharField(max_length=10, choices=RETURN_TYPES)
    due_date = models.DateField()
    filed_date = models.DateField(null=True, blank=True)
    filed_by_ca = models.BooleanField(default=False)

    def is_due(self):
        from datetime import date
        return (not self.filed_by_ca) and self.due_date >= date.today()

    def __str__(self):
        return f"{self.client.username} - {self.return_type} due on {self.due_date}"

