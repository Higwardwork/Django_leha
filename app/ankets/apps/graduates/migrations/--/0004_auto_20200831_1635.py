# Generated by Django 3.1 on 2020-08-31 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graduates', '0003_auto_20200828_1212'),
    ]

    operations = [
        migrations.CreateModel(
            name='Spravochnik',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spravochnik_number', models.IntegerField(verbose_name='код справочника с ответами')),
                ('spravochnik_kod', models.IntegerField(verbose_name='код ответа')),
                ('spravochnik_name', models.CharField(max_length=255, null=True, verbose_name='наименование')),
            ],
            options={
                'verbose_name': 'Справочник',
                'verbose_name_plural': 'Справочники',
            },
        ),
        migrations.AlterModelOptions(
            name='answer',
            options={'verbose_name': 'Ответ', 'verbose_name_plural': 'Ответы'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'verbose_name': 'Вопрос', 'verbose_name_plural': 'Вопросы'},
        ),
        migrations.AlterModelOptions(
            name='respondent',
            options={'verbose_name': 'Респондент', 'verbose_name_plural': 'Респонденты'},
        ),
        migrations.AlterModelOptions(
            name='result',
            options={'verbose_name': 'Результат', 'verbose_name_plural': 'Результаты'},
        ),
        migrations.AddField(
            model_name='answer',
            name='answer_spravochnik',
            field=models.IntegerField(null=True, verbose_name='код справочника с ответами'),
        ),
    ]
