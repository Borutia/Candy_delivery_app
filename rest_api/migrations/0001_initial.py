# Generated by Django 3.1.7 on 2021-03-10 13:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('courier_id', models.AutoField(primary_key=True, serialize=False)),
                ('courier_type', models.CharField(choices=[('foot', 'Пеший курьер'), ('bike', 'Велокурьер'), ('car', 'Курьер на автомобиле')], max_length=4)),
                ('regions', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None)),
                ('working_hours', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=11), size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=4)),
                ('region', models.PositiveIntegerField()),
                ('delivery_hours', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=11), size=None)),
            ],
        ),
    ]
