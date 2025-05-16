# This migration deletes the ReturnFiling model
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0006_alter_returnfiling_due_date'),
    ]
    operations = [
        migrations.DeleteModel(
            name='ReturnFiling',
        ),
    ]
