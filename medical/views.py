
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .models import *
from django.contrib import messages, auth
from django.db.models import Q
from .utilities import check_strong_password, check_if_manager, redirect_user
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import send_mail
from datetime import datetime, timedelta, time
from .forms import SearchrRequests
from io import BytesIO,StringIO



# Create your views here.
@login_required
def render_pdf_view(request):
    user = Hospital.objects.get(leader=request.user)
    responses = Requests.objects.filter(hospital_requested_id=user)
    template_path = 'medical/ResponseReport.html'
    context = {'responses': responses}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="response_report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def approved_pdf(request):
    user = Hospital.objects.get(leader=request.user)
    approves = Approved.objects.filter(hospital_approved_id=user)

    template_path = 'medical/ApprovedReport.html'
    context = {'approves': approves}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="approve_report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def view_med(request):
    hospital = Hospital.objects.get(leader=request.user)
    medicines=Medicine.objects.exclude(hospital=hospital)
    return render(request, 'medical/all_medicines.html', {'medicines': medicines})

@check_if_manager
def view_requests(request):
    hospital = Hospital.objects.get(leader=request.user)
    requests = Requests.objects.filter(hospital_owner_id=hospital)
    return render(request, 'medical/all_requests.html', {'requests': requests})

@check_if_manager
def view_approved(request):
    user = Hospital.objects.get(leader=request.user)
    approves = Approved.objects.filter(hospital_approved_id=user)
    return render(request, 'medical/all_approved.html', {'approves': approves})

@check_if_manager
def view_responses(request):
    user = Hospital.objects.get(leader=request.user)
    responses = Requests.objects.filter(hospital_requested_id=user)
    return render(request, 'medical/all_responses.html', {'responses': responses})

@check_if_manager
def returned(request):
    user = Hospital.objects.get(leader=request.user)
    returns = Returned.objects.filter(hospital_returned_id=user)
    return render(request, 'medical/send_returned.html', {'returns': returns})

@check_if_manager
def view_returned(request):
    user = Hospital.objects.get(leader=request.user)  
    returns = Returned.objects.filter(hospital_received_id=user)
    return render(request, 'medical/all_returned.html', {'returns': returns})

@login_required
def medical_Returned(request,id):
    returns = Returned.objects.get(id=id)
    returns.status = "RETURNED"
    returns.save()
    return redirect("returned")   

@login_required
def edit_med(request, id):
    medicine = Medicine.objects.get(id=id)
    return render(request, 'medical/request_form.html', {'medicine': medicine})




@login_required
@require_POST
def search_med(request):
    data = request.POST
    value = data.get('value')
    hospital = Hospital.objects.get(leader=request.user)
    medicines=Medicine.objects.exclude(hospital=hospital)
    medicines = medicines.filter(Q(name__icontains=value))
    if medicines.exists():
        print(medicines)
        return render(request, "medical/all_medicines.html", {"medicines": medicines})
    else:
        messages.warning(request, 'No result found')
        return render(request, 'medical/dashboard.html', {"medicines": []})

@login_required
def sending_email(request):
    if request.method=="POST":
        sub=request.POST.get('subject')
        msg=request.POST.get('message')
        email=request.POST.get('email')
        print(sub,msg,email)
        send_mail(sub,msg,'joyeusemahoro92@gmail.com',[email])
        return redirect('mails')
    return render(request ,'medical/mails.html')

@login_required
def record_request(request):
    if request.method == 'POST':
        medecine_id = request.POST['medecine_id']
        hospital_id = request.POST.get('hospital_id')
        return_date=request.POST['return_date']
        quantity = request.POST['qty']
        user = request.user
        hospital = Hospital.objects.get(leader=user)
        hospital_object = Hospital.objects.get(id=hospital_id)
        medicine = Medicine.objects.get(id=medecine_id)

        Requests.objects.create(medicine=medicine, hospital_owner=hospital_object,
                               return_date=return_date,quantity=quantity,
                               hospital_requested=hospital, status="PENDING")
        return redirect("list_responses")
    return render(request, 'medical/request_form.html', {'medicine': medicine})

@check_if_manager
def temps(request):
    hospital = Hospital.objects.get(leader=request.user)
    medicines = Medicine.objects.filter(hospital=hospital)
    return render(request, 'medical/temp.html', {'medicines': medicines})  

@login_required
def medical_approval(request,id):
    if request.method == 'GET':
     requestt = Requests.objects.get(id=id)
     medicine_id=requestt.medicine_id
     hospital_req=requestt.hospital_requested_id
     hospital_app=requestt.hospital_owner_id
     quantity=requestt.quantity
     return_date=requestt.return_date
     med=Medicine.objects.get(id=medicine_id)
     sender=Hospital.objects.get(id=hospital_app)
     receiver= Hospital.objects.get(id=hospital_req)
     senderUser=Medicine.objects.get(id=hospital_app)
     receiverUser=Medicine.objects.get(requests=hospital_req)
     senderUser.quantity-=int(quantity)
     receiverUser.quantity+=int(quantity)
     requestt.status = "APPROVED"
     Approved.objects.create(medicine=med, quantity=quantity,return_date=return_date,
                                hospital_requested=receiver,hospital_approved=sender)
     Returned.objects.create(medicine=med, quantity=quantity,return_date=return_date,
                                 hospital_returned=receiver,hospital_received=sender)
     requestt.save()
     senderUser.save()
     receiverUser.save()
     return redirect("list_requests")
    return render(request, 'medical/all_requests.html')
     

@login_required
def medical_disapproval(request,id):
    requestt = Requests.objects.get(id=id)
    requestt.status = "DENIED"
    requestt.save()
    return redirect("list_requests")


def index(request):
    if request.user.is_anonymous:
        pass
    else:
        response = redirect_user(request.user)
        if response == "ADMIN":
            return redirect('/admin/')
        elif response == "DASHBOARD":
            return redirect('dash')
    return render(request, '_partials/index.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        hospital_name = request.POST['hospital_name']
        address = request.POST['address']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            checked_password_response = check_strong_password(password)
            if checked_password_response.get('code') is False:
                messages.warning(
                    request, checked_password_response.get('message'))
                return redirect('register')
            if CustomUser.objects.filter(username=username).exists():
                messages.warning(request, 'That username is taken')
                return redirect('register')
            elif Hospital.objects.filter(hospital_name=hospital_name):
                messages.warning(request, "The Hospital already exists")
            else:
                user = CustomUser.objects.create_user(first_name=first_name, last_name=last_name,
                                                      phone_number=phone_number,
                                                      username=username, email=email, password=password

                                                      )
                Hospital.objects.create(
                    leader=user, hospital_name=hospital_name, address=address)
                return redirect("login")

        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    else:
        return render(request, 'authentications/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            # messages.success(request, 'You are now logged in')
            response = redirect_user(user)
            if response == "ADMIN":
                return redirect('/admin/')
            elif response == "DASHBOARD":
                return redirect('dash')

        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'authentications/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        # messages.success(request, 'You are now logged out')
        return redirect('index')


@login_required
def record_meds(request):
    if request.method == 'POST':
        name = request.POST['name']
        expiry_date = request.POST['expiry_date']
        manufacture_date=request.POST['manufacture_date']
        quantity = request.POST['quantity']
        user = request.user
        hospital = Hospital.objects.get(leader=user)

        Medicine.objects.create(name=name, expiry_date=expiry_date,
                               manufacture_date=manufacture_date,
                               quantity=quantity,
                               hospital=hospital)
        return redirect("temp")
    return render(request, 'medical/record_medicine.html')



@check_if_manager
def dashboard(request):
    hospital = Hospital.objects.get(leader=request.user)
    medicines = Medicine.objects.filter(hospital=hospital)
    return render(request, 'medical/dashboard.html', {'medicines': medicines})


@login_required
def edit_medication(request, id):
    medicine = Medicine.objects.get(id=id)  
    return render(request, 'medical/edit_medication.html', {'medicine': medicine})


@login_required
def update_medication(request, id):
    medicine = Medicine.objects.get(id=id)
    name = request.GET['name']
    expiry_date = request.GET['expiry_date']
    manufacture_date=request.GET['manufacture_date']
    quantity = request.GET['quantity']

    medicine.name = name
    medicine.expiry_date=expiry_date
    medicine.manufacture_date=manufacture_date
    medicine.quantity = quantity

    medicine.save()
    return redirect("temp")
  


@login_required
def delete_medication(request, id):
    medicine = Medicine.objects.get(id=id)
    medicine.delete()
    return redirect('temp')


@login_required
@require_POST
def search_medication(request):
    data = request.POST
    value = data.get('value')
    hospital = Hospital.objects.get(leader=request.user)
    medicines = Medicine.objects.filter(hospital=hospital)
    medicines = medicines.filter(Q(name__icontains=value) |
                               Q(expiry_date__icontains=value) | Q(manufacture_date__icontains=value)| Q(quantity__icontains=value))
    if medicines.exists():
        print(medicines)
        return render(request, "medical/temp.html", {"medicines": medicines})
    else:
        messages.warning(request, 'No result found')
        return render(request, 'medical/temp.html', {"medicines": []})


def wait(request):
    return render(request, 'medical/hospital_waiting.html')
@check_if_manager
def dashi(request):
    return render(request, 'medical/dash.html')
def about_view(request):
    return render(request, '_partials/about.html')


def contact_view(request):
    return render(request, '_partials/contact.html')

@login_required
def main(request):
    return render(request, 'medical/mainpage.html')

def render_to_pdf(template_src, content_dic={}):
    template = get_template(template_src)
    html = template.render(content_dic)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    else:
        return None


def print_pdf_for_all(request, case):
    if request.method == 'GET':
        try:
            user = Hospital.objects.get(leader=request.user)
            users = Hospital.objects.filter(leader=request.user)
            for us in users:
                address=us.address
                email=us.leader.email
                print('address',address)
                print('email',email)
        except:
            messages.error(request, 'Not A hospital')
            return redirect('dash')
        date = str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(
            datetime.now().year)
        title = "RESPONSES OF REQUESTS "
        today = datetime.now().date()
       
        if case == "TODAY":
            title += " FOR TODAY"
            today = datetime.now().date()
            responses = Requests.objects.filter(hospital_requested_id=user,
                                                          created_at__gte=today) 
           
        elif case == "THIS_MONTH":
            title += " OF THIS MONTH"
            months=datetime.now().month
            years=datetime.now().year
            responses = Requests.objects.filter(hospital_requested_id=user,
                                                           created_at__month=months, created_at__year=years)
                                                               
        elif case == "THIS_YEAR":
            title += " OF THIS YEAR"
            years=datetime.now().year
            responses = Requests.objects.filter(hospital_requested_id=user,
                                                          created_at__year=years)
        elif case == "BY_DATE":
            data_form = SearchrRequests(data=request.GET)
            if data_form.is_valid():
                date = data_form.cleaned_data.get('date')
                title += " : " + str(date)
                responses = Requests.objects.filter(hospital_requested_id=user,
                                                               created_at__date=date)
                
           

        elif case == "BY_DATE_RANGE":
            data=request.GET
            start_date = request.GET.get('date_start')
            end_date = request.GET.get('date_end')
            title += " : " + str(start_date) + " - " + str(end_date)
            responses = Requests.objects.filter(hospital_requested_id=user,
                created_at__date__range=(start_date, end_date))

        pdf = render_to_pdf('medical/ResponseReport.html',
                            {"responses": responses, "user": user, "date": date, 'title': title,"email":email,"address":address})
       
        return HttpResponse(pdf, content_type='application/pdf')

@login_required  
def get_report(request, case):
    try:
        user = Hospital.objects.get(leader=request.user)

    except:
        messages.error(request, 'Not A hospital')
        return redirect('dash')
    title = "RESPONSES"
    date = str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(
        datetime.now().year)
    today = datetime.now().date()
    if case == "TODAY":
        title += " FOR TODAY"
        today = datetime.now().date()
        responses = Requests.objects.filter(hospital_requested_id=user,
                                                       created_at__gte=today)
        content = {"responses": responses, "date": str(
            date) + '', "of": case, "title": title}
    elif case == "THIS_MONTH":
        title += " OF THIS MONTH"
        months=datetime.now().month
        years=datetime.now().year
        responses = Requests.objects.filter(hospital_requested_id=user,
                                                       created_at__month=months,created_at__year=years)
                                                          
                                                       
        content = {"responses": responses, "date": str(
            date) + '', "of": case, "title": title}
    elif case == "THIS_YEAR":
        title += " OF THIS YEAR"
        years=datetime.now().year
        responses = Requests.objects.filter(hospital_requested_id=user,
                                                      created_at__year=years)
        content = {"responses": responses, "date": str(
         date) + '', "of": case, "title": title}

    elif case == "BY_DATE":
        data_form = SearchrRequests(data=request.GET)
        if data_form.is_valid():
            date = data_form.cleaned_data.get('date')
            title += " : " + str(date)

            responses = Requests.objects.filter(hospital_requested_id=user,
                created_at__date=date)
            content = {"responses": responses, "date": str(
                date) + '', "of": case, "title": title}

    elif case == "BY_DATE_RANGE":
            data=request.GET
            start_date = request.GET.get('date_start')
            end_date = request.GET.get('date_end')

            title += " : " + str(start_date) + " - " + str(end_date)

            responses = Requests.objects.filter(hospital_requested_id=user,
                created_at__date__range=(start_date, end_date))
            content = {"start_date": start_date, "end_date": end_date, "responses": responses,
                       "date": str(date) + '', "of": case, "title": title}
    else:
         messages.error(request, 'Enter a valid date!')
         return redirect('healthcenter_report', case="TODAY")
    return render(request, 'medical/healthcenter_report.html', content)

  

    # paginator = Paginator(transactions_list, 10)
    # try:
    #     transactions = paginator.page(page)
    # except PageNotAnInteger:
    #     transactions = paginator.page(1)
    # except EmptyPage:
    #     transactions = paginator.page(paginator.num_pages)
    # content["transactions"] = transactions



# def healthReports(request, case):
#     user = Hospital.objects.get(leader=request.user)
#     responses = Requests.objects.filter(hospital_requested_id=user)
#     # medicines = medicines.filter(Q(name__icontains=value) |
#     if case == "TODAY":
#         today = datetime.now().date()
#         responses = responses.filter(created_at__gte=today)
#     elif case == "THIS_MONTH":
#         months=datetime.now().month
#         years=datetime.now().year
#         responses = responses.filter( created_at__month=months, created_at__year=years)

#     elif case == "THIS_YEAR":
#         years=datetime.now().year
#         responses = responses.filter( created_at__year=years)

#     elif case == "BY_DATE":
#          data = request.POST
#          value = data.get('date')
#          responses = responses.filter(Q(created_at__icontains=value))

#     elif case == "BY_DATE_RANGE":
#         data=request.GET
#         start_date = request.GET.get('date_start')
#         end_date = request.GET.get('date_end')
#         responses = responses.filter(created_at__date__range=(start_date, end_date))


#     else:
#             messages.error(request, 'Enter a valid date!')
#             return redirect('healthReport', case="TODAY")
#     return render(request, 'authentications/healthReports.html', {'responses': responses})


@login_required
def approvedd_report(request, case):
    try:
        user = Hospital.objects.get(leader=request.user)

    except:
        messages.error(request, 'Not A hospital')
        return redirect('dash')
    title = "APPROVED REQUESTS"
    date = str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(
        datetime.now().year)
    today = datetime.now().date()
    if case == "TODAY":
        title += " FOR TODAY"
        today = datetime.now().date()
        approves = Approved.objects.filter(hospital_approved_id=user,
                                                       created_at__gte=today)
        content = {"approves": approves, "date": str(
            date) + '', "of": case, "title": title}
    elif case == "THIS_MONTH":
        title += " OF THIS MONTH"
        months=datetime.now().month
        years=datetime.now().year
        approves = Approved.objects.filter(hospital_approved_id=user,
                                                       created_at__month=months,created_at__year=years)
                                                          
                                                       
        content = {"approves": approves, "date": str(
            today) + '', "of": case, "title": title}
    elif case == "THIS_YEAR":
        title += " OF THIS YEAR"
        years=datetime.now().year
        approves = Approved.objects.filter(hospital_approved_id=user,
                                                      created_at__year=years)
        content = {"approves": approves, "date": str(
            date) + '', "of": case, "title": title}

    elif case == "BY_DATE":
        data_form = SearchrRequests(data=request.GET)
        if data_form.is_valid():
            date = data_form.cleaned_data.get('date')
            title += " : " + str(date)

            approves = Approved.objects.filter(hospital_approved_id=user,
                created_at__date=date)
            content = {"approves": approves, "date": str(
                date) + '', "of": case, "title": title}

    elif case == "BY_DATE_RANGE":
            data=request.GET
            start_date = request.GET.get('date_start')
            end_date = request.GET.get('date_end')

            title += " : " + str(start_date) + " - " + str(end_date)

            approves = Approved.objects.filter(hospital_approved_id=user,
                created_at__date__range=(start_date, end_date))
            content = {"start_date": start_date, "end_date": end_date, "approves": approves,
                       "date": str(date) + '', "of": case, "title": title}
    else:
         messages.error(request, 'Enter a valid date!')
         return redirect('center', case="TODAY")
    return render(request, 'medical/center.html', content)


def print_pdf_for_approved(request, case):
    if request.method == 'GET':
        try:
            user = Hospital.objects.get(leader=request.user)
            users = Hospital.objects.filter(leader=request.user)
            for us in users:
                address=us.address
                email=us.leader.email
                print('address',address)
                print('email',email)

        except:
            messages.error(request, 'Not A hospital')
            return redirect('dash')
        date = str(datetime.now().day) + '/' + str(datetime.now().month) + '/' + str(
            datetime.now().year)
        title = "APPROVED REQUESTS"
        today = datetime.now().date()
       
        if case == "TODAY":
            title += " FOR TODAY"
            today = datetime.now().date()
            approves = Approved.objects.filter(hospital_approved_id=user,
                                                          created_at__gte=today)
           
        elif case == "THIS_MONTH":
            title += " OF THIS MONTH"
            months=datetime.now().month
            years=datetime.now().year
            approves = Approved.objects.filter(hospital_approved_id=user,
                                                           created_at__month=months, created_at__year=years)
                                                               
        elif case == "THIS_YEAR":
            title += " OF THIS YEAR"
            years=datetime.now().year
            approves = Approved.objects.filter(hospital_approved_id=user,
                                                          created_at__year=years)
        elif case == "BY_DATE":
            data_form = SearchrRequests(data=request.GET)
            if data_form.is_valid():
                date = data_form.cleaned_data.get('date')
                title += " : " + str(date)
                approves = Approved.objects.filter(hospital_approved_id=user,
                                                               created_at__date=date)
           

        elif case == "BY_DATE_RANGE":
            data=request.GET
            start_date = request.GET.get('date_start')
            end_date = request.GET.get('date_end')
            title += " : " + str(start_date) + " - " + str(end_date)
            approves = Approved.objects.filter(hospital_approved_id=user,
                created_at__date__range=(start_date, end_date))

        pdf = render_to_pdf('medical/ApprovedReport.html',
                            {"approves": approves, "user": user, "date": date, 'title': title, "address":address,
                            "email":email})
       
        return HttpResponse(pdf, content_type='application/pdf')

def directors(request):
    hospitals= Hospital.objects.all()
    users=CustomUser.objects.all()
    content = {"users": users, "hospitals": hospitals}
    return render(request, 'medical/all_directors.html',content)

@login_required
@require_POST
def search_director(request):
    data = request.POST
    value = data.get('value')
    users=CustomUser.objects.filter(Q(first_name__icontains=value)
                                |Q(last_name__icontains=value) )
    # users=CustomUser.objects.filter(Q(hospital_name=value))
                             
    if users.exists():
        return render(request, "medical/all_directors.html", {"users":users})
    else:
        messages.warning(request, 'No result found') 
        return render(request, 'medical/all_directors.html', {"users":users})

def notification(request,case):
    user = Hospital.objects.get(leader=request.user)
    
    # medicines=Medicine.objects.filter(hospital=user)
    # for medicine in medicines:
        # expiry_date=medicine.expiry_date
        # today=datetime.now().date()
        # mydate=datetime.now().date()
        # title = "Expired Medicines"
       

    #     print('insurance_expiry_date',expiry_date)
    #     print('today',today)
    #     print('mydate',mydate)

    #     if datetime.now() == expiry_date:
    #        medicines = medicines.filter(expiry_date=datetime.now().date())
           
        
    # content = {"medicines": medicines, "title": title, "counting":counting}
   
    # return render(request, 'medical/temp.html',content)
    if case == "TODAY":
        today = datetime.now().date()
        year = today.year
        month = today.month
        day = today.day
        medicines = Medicine.objects.filter(hospital=user,expiry_date__year=year, 
        expiry_date__month=month, expiry_date__day=day)
                                                       
        counting=medicines.count
        content = {"medicines": medicines,"counting":counting}
    else:
         messages.error(request, 'Enter a valid date!')
         return redirect('temp', case="TODAY")
    return render(request, 'medical/temp.html', content)

         
