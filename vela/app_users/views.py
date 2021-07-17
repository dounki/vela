from django.shortcuts import render, redirect
from app_users.forms import UserForm, UserProfileInfoForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from curriculum.models import Standard
from .models import UserProfileInfo, Contact
from django.views.generic import CreateView

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("ACCOUNT IS DEACTIVATED")
        else:
            return HttpResponse("Please use correct id and password")
            # return HttpResponseRedirect(reverse('register'))

    else:
        return render(request, 'app_users/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


# Create your views here.
# def index(request):
#     return render(request,'app_users/index.html')

def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request, 'app_users/registration.html',
                            {'registered':registered,
                             'user_form':user_form,
                             'profile_form':profile_form})

class HomeView(TemplateView):
    template_name = 'app_users/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        standards = Standard.objects.all()
        teachers = UserProfileInfo.objects.filter(user_type='teacher')
        profiles = UserProfileInfo.objects.all()
        context['standards'] = standards
        context['teachers'] = teachers
        context['profiles'] = profiles
        return context


class ContactView(CreateView):
    model = Contact
    fields = '__all__'
    template_name = 'app_users/contact.html'

'''
The Donation Part

'''
import stripe

stripe.api_key = "sk_test_bpDvB2IABq32FB2XIn884oS7"

# Create your views here.

def index(request):

    return render(request, 'app_users/donate.html')


def charge(request):


    if request.method == 'POST':
        print('Data:', request.POST)

        amount = int(request.POST['amount'])

        customer = stripe.Customer.create(
            email=request.POST['email'],
            name=request.POST['nickname'],
            source=request.POST['stripeToken']
            )

        charge = stripe.Charge.create(
            customer=customer,
            amount=amount*100,
            currency='usd',
            description="Donation"
            )

    return redirect(reverse('success', args=[amount]))


def successMsg(request, args):
    amount = args
    return render(request, 'app_users/success.html', {'amount':amount})