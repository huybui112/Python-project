# Generated by Django 4.2.5 on 2023-09-30 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_alter_product_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='total_price',
            field=models.IntegerField(null=True),
        ),
    ]
