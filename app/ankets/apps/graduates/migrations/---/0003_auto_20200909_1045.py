# Generated by Django 3.1 on 2020-09-09 07:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graduates', '0002_question_field_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionblock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_name', models.TextField(verbose_name='название блока вопросов')),
                ('respondent_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='graduates.respondent')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='block_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='graduates.questionblock'),
        ),
    ]
