# Generated by Django 4.2.5 on 2023-10-05 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_alter_product_sizes_delete_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sizes',
            field=models.CharField(max_length=10000, null=True),
        ),
    ]
