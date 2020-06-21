# Generated by Django 2.2.13 on 2020-06-20 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0018_userad'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userad',
            name='content',
        ),
        migrations.AddField(
            model_name='userad',
            name='site',
            field=models.IntegerField(choices=[(1, 'YouTube'), (2, 'Twitter'), (3, 'Instagram'), (4, 'TikTok'), (0, 'その他')], default=0),
        ),
        migrations.AlterField(
            model_name='userad',
            name='url',
            field=models.URLField(),
        ),
    ]
