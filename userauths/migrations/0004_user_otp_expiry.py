# Generated by Django 4.2.7 on 2024-09-19 07:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0003_user_reset_token_alter_user_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp_expiry',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 19, 7, 19, 5, 989545, tzinfo=datetime.timezone.utc)),
        ),
    ]
