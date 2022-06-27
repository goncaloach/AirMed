# Generated by Django 4.0.4 on 2022-05-13 20:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Medico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numMedico', models.CharField(max_length=9)),
                ('dataNascimento', models.DateTimeField()),
                ('telefone', models.CharField(max_length=9)),
                ('morada', models.CharField(max_length=100)),
                ('clinica', models.CharField(max_length=100)),
                ('distrito', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numUtente', models.CharField(max_length=9)),
                ('dataNascimento', models.DateTimeField()),
                ('telefone', models.CharField(max_length=9)),
                ('morada', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Agendamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataHoraInicio', models.DateTimeField(blank=True, null=True)),
                ('dataHoraFim', models.DateTimeField(blank=True, null=True)),
                ('tipoExame', models.CharField(max_length=50)),
                ('estado', models.BooleanField(default=False)),
                ('idCliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='marcarExame.cliente')),
                ('idMedico', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='marcarExame.medico')),
            ],
        ),
    ]