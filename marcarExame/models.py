from xmlrpc.client import MAXINT
from django.contrib.auth.models import User
from django.db import models

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numUtente = models.CharField(max_length=9)
    dataNascimento = models.DateTimeField()
    telefone = models.CharField(max_length=9)
    morada = models.CharField(max_length=100)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class Medico(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    numMedico = models.CharField(max_length=9)
    dataNascimento = models.DateTimeField()
    telefone = models.CharField(max_length=9)
    morada = models.CharField(max_length=100)
    clinica = models.CharField(max_length=100)
    distrito = models.CharField(max_length=50)

    def __str__(self):
        return "Dr. " + self.user.first_name + " " + self.user.last_name


class Agendamento(models.Model):
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True)
    idMedico = models.ForeignKey(Medico, on_delete=models.CASCADE, blank=True, null=True)
    dataHoraInicio = models.DateTimeField(blank=True, null=True)
    dataHoraFim = models.DateTimeField(blank=True, null=True)
    tipoExame = models.CharField(max_length=50)
    estado = models.BooleanField(default=False)

class Reviews(models.Model):
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True)
    CHOICES = zip( range(1,5), range(1,5) )
    rating = models.IntegerField(choices=CHOICES, blank=True)
    review = models.CharField(max_length=200)