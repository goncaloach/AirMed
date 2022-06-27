import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect

from .models import Cliente, Medico, Agendamento, Reviews
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.models import Permission
from django.contrib import messages
from datetime import datetime
from datetime import timedelta
import smtplib
import random


def loadDefaultContext(request):
    fs = FileSystemStorage()
    isMedic = None
    isClient = None
    if request.user.is_superuser:
        uploaded_file_url = fs.url("profile_picture.png")
    else:
        uploaded_file_url = fs.url(request.user.username + ".png")
        isMedic = request.user.groups.filter(name="Medic").exists()
        isClient = request.user.groups.filter(name="Client").exists()
    context = {'uploaded_file_url': uploaded_file_url,
               'isMedic': isMedic,
               'isClient': isClient}
    return context


def loadDefaultMedicContext(request):
    fs = FileSystemStorage()
    context = {'uploaded_file_url': fs.url(request.user.username + ".png"),
               'isMedic': request.user.groups.filter(name="Medic").exists()}
    return context


def loadDefaultClientContext(request):
    fs = FileSystemStorage()
    context = {'uploaded_file_url': fs.url(request.user.username + ".png"),
               'isClient': request.user.groups.filter(name="Client").exists()}
    return context


def check_normaluser(user):
    return not user.is_superuser


def check_superuser(user):
    return user.is_superuser


def check_medic(user):
    return user.groups.filter(name='Medic').exists()


def check_client(user):
    return user.groups.filter(name='Client').exists()


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not username or not password:
            messages.error(request, 'Fields cannot be left blank')
            return HttpResponseRedirect(reverse('marcarExame:login_view', args=()))
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid Credentials')
            return HttpResponseRedirect(reverse('marcarExame:login_view', args=()))
        login(request, user)
        return HttpResponseRedirect(reverse('marcarExame:dash', args=()))
    return render(request, 'marcarExame/login.html')


@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('marcarExame:login_view'))


@login_required
def dash(request):
    return render(request, 'marcarExame/dash.html', loadDefaultContext(request))


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        birth_date = request.POST['birth_date']
        phone = request.POST['phone']
        address = request.POST['address']
        nhs = request.POST['nhs']
        if not username or not password or not email or not first_name or not birth_date or not 'img' in request.FILES \
                or not phone or not address or not nhs or not last_name:
            messages.error(request, 'Fields cannot be left blank')
            return HttpResponseRedirect(reverse('marcarExame:register', args=()))
        if len(username) > 50 or len(password) > 50 or len(email) > 50 or len(first_name) > 50 or len(
                last_name) > 50 or len(phone) != 9 or len(nhs) != 9 or len(address) > 100 \
                or not phone.isnumeric() or not nhs.isnumeric():
            messages.error(request, 'Invalid field input(s)')
            return HttpResponseRedirect(reverse('marcarExame:register', args=()))
        birthDate = datetime.strptime(birth_date, '%Y-%m-%d').date()
        if (datetime.now().date() - birthDate) < timedelta(days=365 * 18):
            messages.error(request, 'You must be at least 18 years old to create an account')
            return HttpResponseRedirect(reverse('marcarExame:register', args=()))
        fs = FileSystemStorage()
        uploaded_file = request.FILES['img']
        fileName, extension = os.path.splitext(uploaded_file.name)
        lowerExtension = extension.lower()
        if not (
                lowerExtension == '.jpeg' or lowerExtension == '.png' or lowerExtension == '.gif' or lowerExtension == '.jpg'):
            messages.error(request, 'You must choose an image file')
            return HttpResponseRedirect(reverse('marcarExame:register', args=()))
        try:
            User.objects.get(username=username)
            messages.error(request, 'This username already exists, please choose a different one')
            return HttpResponseRedirect(reverse('marcarExame:register', args=()))
        except:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            Cliente(user=user, dataNascimento=birth_date, telefone=phone, morada=address, numUtente=nhs).save()
            p1 = Permission.objects.get(codename="view_agendamento")
            p2 = Permission.objects.get(codename="change_agendamento")
            user.user_permissions.add(p1, p2)

            group = Group.objects.get(name="Client")
            group.user_set.add(user)
            fs.save(username + '.png', request.FILES['img'])
            messages.success(request, 'Client created successfully')
            login(request, authenticate(username=username, password=password))
            return HttpResponseRedirect(reverse('marcarExame:dash', args=()))
    else:
        return render(request, 'marcarExame/register.html')


@login_required
def about(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        newPassword = request.POST['password']
        oldPassword = request.POST['current_password']
        if not first_name or not last_name or not email:
            messages.error(request, 'Fields cannot be left blank')
            return HttpResponseRedirect(reverse('marcarExame:about', args=()))
        if len(email) > 50 or len(first_name) > 50 or len(last_name) > 50:
            messages.error(request, 'Invalid field input(s)')
            return HttpResponseRedirect(reverse('marcarExame:about', args=()))
        user = User.objects.get(username=request.user.username)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        if newPassword and oldPassword:
            if authenticate(username=request.user.username, password=oldPassword):
                user.set_password(newPassword)
                login(request, user)
            else:
                messages.error(request, 'Invalid Current password')
                return HttpResponseRedirect(reverse('marcarExame:about', args=()))
        user.save()
        if not request.user.is_superuser:
            if 'img' in request.FILES:
                fs = FileSystemStorage()
                uploaded_file = request.FILES['img']
                fileName, extension = os.path.splitext(uploaded_file.name)
                lowerExtension = extension.lower()
                if not (
                        lowerExtension == '.jpeg' or lowerExtension == '.png' or lowerExtension == '.gif' or lowerExtension == '.jpg'):
                    messages.error(request, 'You must choose an image file')
                    return HttpResponseRedirect(reverse('marcarExame:about', args=()))
                fs.delete(request.user.username + ".png")
                fs.save(request.user.username + ".png", request.FILES['img'])
            phone = request.POST['phone']
            address = request.POST['address']
            if not phone or not address:
                messages.error(request, 'Fields cannot be left blank')
                return HttpResponseRedirect(reverse('marcarExame:about', args=()))
            if len(phone) != 9 or len(address) > 100 or not phone.isnumeric():
                messages.error(request, 'Invalid field input(s)')
                return HttpResponseRedirect(reverse('marcarExame:about', args=()))
            if request.user.groups.filter(name="Medic").exists():
                medic = User.objects.get(username=request.user.username).medico
                medic.telefone = phone
                medic.morada = address
                medic.save()
            elif request.user.groups.filter(name="Client").exists():
                client = User.objects.get(username=request.user.username).cliente
                client.telefone = phone
                client.morada = address
                client.save()
        messages.success(request, 'Fields updated successfully')
        return HttpResponseRedirect(reverse('marcarExame:about', args=()))

    fs = FileSystemStorage()
    context = {}
    if request.user.is_superuser:
        context["uploaded_file_url"] = fs.url("profile_picture.png")
    else:
        context["uploaded_file_url"] = fs.url(request.user.username + ".png")
        isMedic = request.user.groups.filter(name="Medic").exists()
        isClient = request.user.groups.filter(name="Client").exists()
        context["isMedic"] = isMedic
        context["isClient"] = isClient
        if isMedic:
            medic = User.objects.get(username=request.user.username).medico
            context["clinic"] = medic.clinica
            context["medicNum"] = medic.numMedico
            context["birth_date"] = medic.dataNascimento
            context["phone"] = medic.telefone
            context["address"] = medic.morada
            context["district"] = medic.distrito
        elif isClient:
            client = User.objects.get(username=request.user.username).cliente
            context["nhs"] = client.numUtente
            context["birth_date"] = client.dataNascimento
            context["phone"] = client.telefone
            context["address"] = client.morada
    return render(request, 'marcarExame/about.html', context)


@login_required
@user_passes_test(check_superuser, login_url=reverse_lazy('marcarExame:login_view'))
def registerMedic(request):
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        birth_date = request.POST['birth_date']
        phone = request.POST['phone']
        address = request.POST['address']
        medicNumber = request.POST['medicNum']
        clinic = request.POST['clinic']
        district = request.POST['district']
        if not username or not email or not first_name or not last_name or not birth_date or not address \
                or not 'img' in request.FILES or not phone or not medicNumber or not clinic or not district:
            messages.error(request, 'Fields cannot be left blank')
            return HttpResponseRedirect(reverse('marcarExame:registerMedic', args=()))
        if len(username) > 50 or len(email) > 50 or len(first_name) > 50 or len(last_name) > 50 \
                or len(phone) != 9 or len(medicNumber) != 9 or len(address) > 100 \
                or not phone.isnumeric() or not medicNumber.isnumeric():
            messages.error(request, 'Invalid field input(s)')
            return HttpResponseRedirect(reverse('marcarExame:registerMedic', args=()))
        birthDate = datetime.strptime(birth_date, '%Y-%m-%d').date()
        if (datetime.now().date() - birthDate) < timedelta(days=365 * 18):
            messages.error(request, 'The medic must be at least 18 years old')
            return HttpResponseRedirect(reverse('marcarExame:registerMedic', args=()))
        fs = FileSystemStorage()
        uploaded_file = request.FILES['img']
        fileName, extension = os.path.splitext(uploaded_file.name)
        lowerExtension = extension.lower()
        if not (
                lowerExtension == '.jpeg' or lowerExtension == '.png' or lowerExtension == '.gif' or lowerExtension == '.jpg'):
            messages.error(request, 'You must choose an image file')
            return HttpResponseRedirect(reverse('marcarExame:registerMedic', args=()))
        try:
            User.objects.get(username=username)
            messages.error(request, 'This username already exists, please choose a different one')
            return HttpResponseRedirect(reverse('marcarExame:registerMedic', args=()))
        except:
            psw = ''.join(
                random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.@_&%') for i in range(16))
            user = User.objects.create_user(username, email, psw, first_name=first_name, last_name=last_name)
            Medico(user=user, dataNascimento=birth_date, telefone=phone, morada=address, numMedico=medicNumber,
                   clinica=clinic, distrito=district).save()
            p1 = Permission.objects.get(codename="view_agendamento")
            p2 = Permission.objects.get(codename="change_agendamento")
            p3 = Permission.objects.get(codename="add_agendamento")
            p4 = Permission.objects.get(codename="delete_agendamento")
            user.user_permissions.add(p1, p2, p3, p4)
            msg = "\nHello " + str(user.username) + " thank you for joining AirMed! Your password is " + str(
                psw) + " change it as soon as possible!"

            sendEmail(user.email, msg)
            group = Group.objects.get(name="Medic")
            group.user_set.add(user)
            fs.save(username + ".png", request.FILES['img'])
            messages.success(request, 'Medic created successfully')
            return HttpResponseRedirect(reverse('marcarExame:dash', args=()))
    return render(request, 'marcarExame/registerMedic.html', loadDefaultContext(request))


@login_required
@user_passes_test(check_medic, login_url=reverse_lazy('marcarExame:login_view'))
@permission_required('marcarExame.add_agendamento', login_url=reverse_lazy('marcarExame:login_view'))
def createAppointments(request):
    if request.method == 'POST':
        dataAp = request.POST['dataAp']
        examType = request.POST['exam_type']
        slotTime = request.POST['slot_time']
        repetition = request.POST['repetition']
        if not dataAp or not examType or not repetition:
            messages.error(request, 'Fields cannot be left blank')
            return HttpResponseRedirect(reverse('marcarExame:createAppointments', args=()))
        if examType != "X-Ray" and examType != "MRI" and examType != "CAT" and examType != "ECO":
            messages.error(request, 'Exam Type can only be: X-Ray,MRI,CAT or ECO!')
            return HttpResponseRedirect(reverse('marcarExame:createAppointments', args=()))
        else:
            input_time = datetime.strptime(dataAp, '%d/%m/%Y %H:%M')
            if (input_time - datetime.now()) < timedelta(
                    seconds=0) or not slotTime.isnumeric or int(slotTime) > 3600 or not repetition.isnumeric \
                    or int(repetition) < 1 or not slotTime.isnumeric or int(slotTime) < 0:
                messages.error(request, 'Invalid input(s)')
                return HttpResponseRedirect(reverse('marcarExame:createAppointments', args=()))
            repetition = int(repetition)
            while repetition > 0:
                given_time = input_time + timedelta(weeks=repetition)
                final_time = given_time + timedelta(minutes=int(slotTime))
                Agendamento(idMedico=User.objects.get(username=request.user.username).medico, dataHoraInicio=given_time,
                            dataHoraFim=final_time, tipoExame=examType).save()
                repetition -= 1
            messages.success(request, 'Appointment created successfully')
            return HttpResponseRedirect(reverse('marcarExame:createAppointments', args=()))
    else:
        return render(request, 'marcarExame/createAppointments.html', loadDefaultMedicContext(request))


@login_required
@user_passes_test(check_medic, login_url=reverse_lazy('marcarExame:login_view'))
def pastAppointments(request):
    if request.method == 'POST':
        startDate = request.POST['start_date']
        endDate = request.POST['end_date']
        examType = request.POST['exam_type']
        if examType != "X-Ray" and examType != "MRI" and examType != "CAT" and examType != "ECO":
            messages.error(request, 'Exam Type can only be: X-Ray,MRI,CAT or ECO!')
            return HttpResponseRedirect(reverse('marcarExame:pastAppointments', args=()))
        if (datetime.strptime(startDate, '%Y-%m-%d') - datetime.strptime(endDate, '%Y-%m-%d')) > timedelta(
                seconds=0) or datetime.strptime(startDate, '%Y-%m-%d') > datetime.today():
            messages.error(request, 'Invalid Date(s)')
            return HttpResponseRedirect(reverse('marcarExame:pastAppointments', args=()))
        context = loadDefaultMedicContext(request)
        appointments_list = Agendamento.objects.filter(
            idMedico=User.objects.get(username=request.user.username).medico.id, idCliente__isnull=False,
            tipoExame=examType, dataHoraInicio__range=[startDate, endDate], dataHoraInicio__lte=datetime.now())
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/pastAppointments.html', context)
    else:
        context = loadDefaultMedicContext(request)
        appointments_list = Agendamento.objects.filter(
            idMedico=User.objects.get(username=request.user.username).medico.id, dataHoraFim__lte=datetime.now(),
            idCliente__isnull=False)
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/pastAppointments.html', context)


@login_required
@user_passes_test(check_medic, login_url=reverse_lazy('marcarExame:login_view'))
@permission_required('marcarExame.delete_agendamento', login_url=reverse_lazy('marcarExame:login_view'))
def futureAppointments(request):
    if request.method == 'POST':
        startDate = request.POST['start_date']
        endDate = request.POST['end_date']
        examType = request.POST['exam_type']
        context = loadDefaultMedicContext(request)
        appointments_list = Agendamento.objects.filter(
            idMedico=User.objects.get(username=request.user.username).medico.id, estado=False,
            idCliente__isnull=False, tipoExame=examType, dataHoraInicio__range=[startDate, endDate],
            dataHoraInicio__gte=datetime.now())
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/futureAppointments.html', context)
    else:
        context = loadDefaultMedicContext(request)
        appointments_list = Agendamento.objects.filter(
            idMedico=User.objects.get(username=request.user.username).medico.id, idCliente__isnull=False,
            estado=False, dataHoraFim__gte=datetime.now())
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/futureAppointments.html', context)


@login_required
@user_passes_test(check_medic, login_url=reverse_lazy('marcarExame:login_view'))
@permission_required('marcarExame.delete_agendamento', login_url=reverse_lazy('marcarExame:login_view'))
def myAvailability(request):
    if request.method == 'POST':
        startDate = request.POST['start_date']
        endDate = request.POST['end_date']
        examType = request.POST['exam_type']
        context = loadDefaultMedicContext(request)
        appointments_list = Agendamento.objects.filter(
            idMedico=User.objects.get(username=request.user.username).medico.id, estado=False, idCliente=None,
            tipoExame=examType, dataHoraInicio__range=[startDate, endDate], dataHoraInicio__gte=datetime.now())
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/myAvailability.html', context)
    else:
        context = loadDefaultMedicContext(request)
        appointments_list = Agendamento.objects.filter(
            idMedico=User.objects.get(username=request.user.username).medico.id, estado=False, idCliente=None,
            dataHoraInicio__gte=datetime.now())
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/myAvailability.html', context)


@login_required
@user_passes_test(check_client, login_url=reverse_lazy('marcarExame:login_view'))
def myAppointments(request):
    if request.method == 'POST':
        startDate = request.POST['start_date']
        endDate = request.POST['end_date']
        examType = request.POST['exam_type']
        context = loadDefaultClientContext(request)
        appointments_list = Agendamento.objects.filter(idCliente=Cliente.objects.get(user=request.user),
                                                       tipoExame=examType,
                                                       dataHoraInicio__range=[startDate, endDate]).order_by('-estado')
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/myAppointments.html', context)
    else:
        context = loadDefaultClientContext(request)
        appointments_list = Agendamento.objects.filter(idCliente=Cliente.objects.get(user=request.user)).order_by(
            '-estado')
        context["appointments_list"] = appointments_list
        return render(request, 'marcarExame/myAppointments.html', context)


@login_required
@user_passes_test(check_client, login_url=reverse_lazy('marcarExame:login_view'))
def scheduleAppointments(request):
    if request.method == 'POST':
        startDate = request.POST['start_date']
        endDate = request.POST['end_date']
        examType = request.POST['exam_type']
        district = request.POST['district']
        if examType != "X-Ray" and examType != "MRI" and examType != "CAT" and examType != "ECO":
            messages.error(request, 'Exam Type can only be: X-Ray,MRI,CAT or ECO!')
            return HttpResponseRedirect(reverse('marcarExame:scheduleAppointments', args=()))
        context = loadDefaultClientContext(request)
        today = datetime.now()
        appointments_list_medic = Agendamento.objects.filter(tipoExame=examType, idCliente__isnull=True,
                                                             dataHoraInicio__range=[startDate, endDate],
                                                             dataHoraInicio__gte=today).values('idMedico')
        medic_list = Medico.objects.filter(id__in=appointments_list_medic, distrito=district)
        appointments_list = Agendamento.objects.filter(idCliente__isnull=True, tipoExame=examType,
                                                       dataHoraInicio__range=[startDate, endDate],
                                                       dataHoraInicio__gte=today)
        user_list = User.objects.all()
        context["appointments_list"] = appointments_list
        context["medic_list"] = medic_list
        context["user_list"] = user_list
        return render(request, 'marcarExame/filteredAppointments.html', context)
    else:
        return render(request, 'marcarExame/scheduleAppointments.html', loadDefaultClientContext(request))


@login_required
@user_passes_test(check_medic, login_url=reverse_lazy('marcarExame:login_view'))
def addResult(request, appointment_id):
    result = request.FILES['result']
    ext = str(result).split(".")[-1]
    if ext != "zip":
        messages.error(request, 'File type must be .zip!')
        return HttpResponseRedirect(reverse('marcarExame:pastAppointments', args=()))
    fs = FileSystemStorage()
    context = {"uploaded_file_url": fs.url(request.user.username + ".png"),
               "isMedic": request.user.groups.filter(name="Medic").exists()}
    fs.save("appointment" + str(appointment_id) + "." + str(ext), result)
    appointment = get_object_or_404(Agendamento, pk=appointment_id)
    appointment.estado = True
    appointment.save()
    client_email = User.objects.get(cliente=Cliente.objects.get(id=appointment.idCliente.id)).email
    msg = "\nYour " + str(appointment.tipoExame) + " result is available for download!"
    sendEmail(client_email, msg)
    appointments_list = Agendamento.objects.filter(
        idMedico=User.objects.get(username=request.user.username).medico.id, dataHoraFim__lte=datetime.now(),
        idCliente__isnull=False)
    context["appointments_list"] = appointments_list
    return render(request, 'marcarExame/pastAppointments.html', context)


@login_required
@user_passes_test(check_normaluser, login_url=reverse_lazy('marcarExame:login_view'))
def removeAppointment(request, appointment_id):
    fs = FileSystemStorage()
    context = {"uploaded_file_url": fs.url(request.user.username + ".png")}
    isMedic = request.user.groups.filter(name="Medic").exists()
    context["isMedic"] = isMedic
    isClient = request.user.groups.filter(name="Client").exists()
    context["isClient"] = isClient
    if isMedic:
        appointment = get_object_or_404(Agendamento, pk=appointment_id)
        appointment.delete()
    elif isClient:
        appointment = get_object_or_404(Agendamento, pk=appointment_id)
        appointment.idCliente = None
        appointment.save()
    if (appointment.idCliente is not None) and (appointment.idMedico is not None):
        client_email = User.objects.get(cliente=Cliente.objects.get(id=appointment.idCliente.id)).email
        medic_email = User.objects.get(medico=Medico.objects.get(id=appointment.idMedico.id)).email
        msg = "\n" + str(appointment.tipoExame) + " with patient " + str(appointment.idCliente) + " and doctor " + str(
            appointment.idMedico) + " was canceled!"
        sendEmail(client_email, medic_email, msg)
    return render(request, 'marcarExame/dash.html', context)

@login_required
@user_passes_test(check_client, login_url=reverse_lazy('marcarExame:login_view'))
def reviews(request):
    if request.method == 'POST':
        rate = request.POST['rate']
        comment_box = request.POST['comment_box']
        Reviews(idCliente=Cliente.objects.get(user=request.user), rating=rate,review=comment_box).save()
        context = loadDefaultClientContext(request)
        reviews_list = Reviews.objects.all()
        context["reviews_list"] = reviews_list
        return render(request, 'marcarExame/reviews.html', context)
    else:
        context = loadDefaultClientContext(request)
        reviews_list = Reviews.objects.all()
        context["reviews_list"] = reviews_list
        return render(request, 'marcarExame/reviews.html', context)


@login_required
@user_passes_test(check_client, login_url=reverse_lazy('marcarExame:login_view'))
def joinAppointment(request, appointment_id):
    context = loadDefaultClientContext(request)
    appointment = get_object_or_404(Agendamento, pk=appointment_id)
    appointment.idCliente = Cliente.objects.get(user=request.user)
    appointment.save()
    msg = "\nThe appointment of a " + str(appointment.tipoExame) + " on " + str(
        appointment.dataHoraInicio) + " with doctor " + str(
        appointment.idMedico) + " is confirmed! Please rate our service at https://forms.gle/iwURKHyyYw9dhWfBA ."
    sendEmail(request.user.email, msg)
    appointments_list = Agendamento.objects.filter(idCliente=Cliente.objects.get(user=request.user))
    context["appointments_list"] = appointments_list
    return render(request, 'marcarExame/myAppointments.html', context)


def sendEmail(email, msg):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login("airmed2022@gmail.com", "rXN$8683rx7sj(n{")
    server.sendmail("airmed2022@gmail.com", str(email), msg.encode(encoding='UTF-8',errors='strict'))
    server.quit()