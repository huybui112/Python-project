# Generated by Django 4.2.5 on 2023-09-28 09:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_orderitem_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='status',
        ),
    ]
