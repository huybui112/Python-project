# Generated by Django 4.2.5 on 2023-09-23 04:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_user_role'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
