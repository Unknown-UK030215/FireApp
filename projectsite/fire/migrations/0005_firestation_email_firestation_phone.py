# Generated by Django 5.1.6 on 2025-05-21 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fire', '0004_firestation_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='firestation',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='firestation',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
