# Generated by Django 2.2.12 on 2020-05-14 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_auto_20200514_2010'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
