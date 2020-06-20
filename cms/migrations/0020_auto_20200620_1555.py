# Generated by Django 2.2.13 on 2020-06-20 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0019_auto_20200620_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userad',
            name='url',
            field=models.URLField(help_text='例: https://twitter.com/onacu_official', verbose_name='URL'),
        ),
        migrations.AlterUniqueTogether(
            name='userad',
            unique_together={('user', 'url')},
        ),
    ]