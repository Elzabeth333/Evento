# Generated by Django 5.0.6 on 2024-09-11 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0009_remove_dummybanks_account_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='ticket_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]