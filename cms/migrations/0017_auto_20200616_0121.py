# Generated by Django 2.2.13 on 2020-06-15 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20200606_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateTimeField(help_text='この項目は必須です。', verbose_name='開催日時'),
        ),
        migrations.AlterUniqueTogether(
            name='ticket',
            unique_together={('event', 'order'), ('event', 'customer')},
        ),
    ]