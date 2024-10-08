# Generated by Django 5.0.3 on 2024-09-14 13:04

from django.db import migrations, models


def create_default_durations(apps, schema_editor):
    Duration = apps.get_model('settings', 'Duration')
    durations = [20, 30, 40, 45, 60, 75, 90]
    for time in durations:
        Duration.objects.get_or_create(time=time)


def create_default_language(apps, schema_editor):
    Language = apps.get_model('settings', 'Language')
    names = ['English']
    for name in names:
        Language.objects.get_or_create(name=name)


def create_default_currency(apps, schema_editor):
    Currency = apps.get_model('settings', 'Currency')
    currencies = [{
        'name': 'USD',
        'symbol': '$',
        'exchange': 1.0,
        'default': True,
    }]
    for currency in currencies:
        Currency.objects.get_or_create(name=currency['name'], symbol=currency['symbol'], exchange=currency['exchange'], default=currency['default'])


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=3, unique=True)),
                ('symbol', models.CharField(blank=True, max_length=3, null=True)),
                ('exchange', models.DecimalField(decimal_places=5, max_digits=10)),
                ('default', models.BooleanField(default=False)),
            ],
        ),
        migrations.RunPython(create_default_currency),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.IntegerField(unique=True)),
            ],
        ),
        migrations.RunPython(create_default_durations),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.RunPython(create_default_language),
    ]
