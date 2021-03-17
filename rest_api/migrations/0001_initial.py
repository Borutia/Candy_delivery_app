# Generated by Django 3.1.7 on 2021-03-17 15:02

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('courier_id', models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='id курьера')),
                ('courier_type', models.CharField(choices=[('foot', 'Пеший курьер'), ('bike', 'Велокурьер'), ('car', 'Курьер на автомобиле')], max_length=4, verbose_name='Тип курьера')),
                ('regions', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None, verbose_name='Районы')),
                ('working_hours', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=11), size=None, verbose_name='График работы')),
                ('lifting_capacity', models.PositiveIntegerField(verbose_name='Грузоподъемность курьера')),
                ('assign_time', models.DateTimeField(null=True, verbose_name='Время назначения')),
                ('last_complete_time', models.DateTimeField(null=True, verbose_name='Время последней доставки')),
                ('status_courier', models.CharField(choices=[('F', 'Свободен'), ('B', 'Занят')], default='F', max_length=1, verbose_name='Статус курьера')),
            ],
        ),
        migrations.CreateModel(
            name='QuantityOrders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foot', models.PositiveIntegerField(default=0, verbose_name='Пеший курьер')),
                ('bike', models.PositiveIntegerField(default=0, verbose_name='Велокурьер')),
                ('car', models.PositiveIntegerField(default=0, verbose_name='Курьер на автомобиле')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='id заказа')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Вес')),
                ('region', models.PositiveIntegerField(verbose_name='Район')),
                ('delivery_hours', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=11), size=None, verbose_name='Промежутки для доставки')),
                ('status_order', models.CharField(choices=[('N', 'Новый'), ('I', 'В обработке'), ('C', 'Доставлен')], default='N', max_length=1, verbose_name='Статус заказа')),
                ('assign_time', models.DateTimeField(null=True, verbose_name='Время назначения')),
                ('complete_time', models.DateTimeField(null=True, verbose_name='Время выполнения')),
                ('delivery_time', models.PositiveIntegerField(null=True, verbose_name='Время доставки в секундах')),
                ('courier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rest_api.courier')),
            ],
        ),
        migrations.AddField(
            model_name='courier',
            name='quantity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_api.quantityorders'),
        ),
    ]
