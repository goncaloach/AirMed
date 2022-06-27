from django.contrib import admin
from .models import Medico,Cliente,Agendamento

# Register your models here.
admin.site.register(Medico)
admin.site.register(Cliente)
admin.site.register(Agendamento)
