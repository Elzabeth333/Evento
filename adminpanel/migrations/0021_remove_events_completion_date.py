# Generated by Django 5.1.1 on 2024-10-29 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0020_alter_events_completion_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='completion_date',
        ),
    ]