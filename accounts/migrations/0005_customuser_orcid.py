# Generated by Django 3.1 on 2021-06-21 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_customuser_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='orcid',
            field=models.CharField(blank=True, max_length=19, null=True),
        ),
    ]
