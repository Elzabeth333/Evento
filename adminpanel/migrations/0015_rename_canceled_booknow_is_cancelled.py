# Generated by Django 5.0.6 on 2024-09-16 05:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0014_booknow_booking_serial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booknow',
            old_name='canceled',
            new_name='is_cancelled',
        ),
    ]