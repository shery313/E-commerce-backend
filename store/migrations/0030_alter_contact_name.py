# Generated by Django 4.2.7 on 2024-09-09 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
