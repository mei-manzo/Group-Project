# Generated by Django 2.2 on 2021-07-25 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group_app', '0002_company_entered_by_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
