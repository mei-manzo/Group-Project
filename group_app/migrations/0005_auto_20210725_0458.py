# Generated by Django 2.2 on 2021-07-25 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group_app', '0004_remove_subscription_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='the_company',
        ),
        migrations.AlterField(
            model_name='subscription',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_subscriptions', to='group_app.Company'),
        ),
    ]
