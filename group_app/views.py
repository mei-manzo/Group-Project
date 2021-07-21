from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *

def index(request):
    return render(request, "index.html")

def check_registration(request):
    errors = User.objects.basic_validator(request.POST)
    email = request.POST['email']
    if request.method == "GET":
        return redirect('/')
    elif len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(first_name = request.POST['first-name'], last_name = request.POST['last-name'], email = request.POST['email'], password = hashed_pw)
        request.session['user_id'] = new_user.id
        return redirect('/success')

def check_login(request):
    if request.method == "GET":
        return redirect ("/")
    else:
        errors = User.objects.login_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        this_user = User.objects.filter(email=request.POST['email'])
        request.session['user_id'] = this_user[0].id
        return redirect('/success')

def success(request):
    if 'user_id' not in request.session:
        return redirect('/')
    this_user = User.objects.filter(id = request.session['user_id'])
    context = {
        "current_user" : this_user[0], #grabs from session rather than database to prevent refreshing into login
        }
    return render(request, "success.html", context)

def logout(request):
    request.session.flush()
    return redirect('/')










def user_account(request):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])

        context = {
            'logged_user': logged_user,
            'user_subscriptions': Subscription.objects.filter(user=logged_user),
        }
        return render(request, "editUser.html", context)
    return redirect("/")  

def process_edit_user(request):
    if 'user_id' in request.session:
        if request.method == "POST":
            # errors handling
            errors = User.objects.edit_profile_validator(request.POST)
            if len(errors) > 0:
                for error in errors.values():
                    messages.error(request, error)
            else:
                logged_user = User.objects.get(id=request.session['user_id'])
                logged_user.first_name = request.POST['first_name']
                logged_user.last_name = request.POST['last_name']
                logged_user.email = request.POST['email']
                logged_user.save()
        return redirect("/user_account")
    return redirect("/")


def add_subscription(request):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])

        context = {
            'logged_user': logged_user,
        }
        return render(request, "add_subscription.html", context)
    return redirect("/")  


def process_add_subscription(request):
    if 'user_id' in request.session:
        if request.method == "POST":
            logged_user = User.objects.get(id=request.session['user_id'])

            new_subscription = Subscription.objects.create(
                user = logged_user,
                company = request.POST['company'],
                level = request.POST['level'],
                monthly_rate = request.POST['monthly_rate'],
                start_date = request.POST['start_date'],
                duration = request.POST['duration'],
            )
            return redirect(f"/edit_subscription/{ new_subscription.id }")
        return redirect("/add_subscription")
    return redirect("/")  


def edit_subscription(request, subscription_id):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])
        subscription_to_edit = Subscription.objects.get(id=subscription_id)
        context = {
            'logged_user': logged_user,
            'subscription_to_edit': subscription_to_edit,
        }
        return render(request, "editSubscription.html", context)
    return redirect("/")


def process_edit_subscription(request):
    if 'user_id' in request.session:
        if request.method == "POST":
            subscription_to_edit = Subscription.objects.get(id=request.POST['subscription_id'])
            subscription_to_edit.company = request.POST['company']
            subscription_to_edit.level = request.POST['level']
            subscription_to_edit.monthly_rate = request.POST['monthly_rate']
            subscription_to_edit.start_date = request.POST['start_date']
            subscription_to_edit.duration = request.POST['duration']
            subscription_to_edit.save()
            return redirect(f"/edit_subscription/{ subscription_to_edit.id }")
        # update to home page once built
        return redirect("/success")

    return redirect("/")