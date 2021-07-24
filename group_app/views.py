from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from .models import *
from datetime import datetime
from django.core.paginator import Paginator

url_company ={
    'Netflix': 'https://www.netflix.com/',
    'Amazon':'https://www.amazon.com/gp/video/offers/ref=dvm_us_dl_sl_go_brsa_mkw_svHxbIxqC-dc_pcrid_448130500925?ie=UTF8&gclid=EAIaIQobChMI8ou9zLX88QIVNQytBh2E7wIjEAAYASAAEgK2cvD_BwE&mrntrk=slid__pgrid_29008589832_pgeo_9033288_x__ptid_kwd-45697133742',
    'Hulu' : 'https://www.hulu.com/welcome'

}
photo_company ={
    'Netflix': 'https://cdn.vox-cdn.com/thumbor/QuS2QKQys3HhosKiV-2IuKhphbo=/39x0:3111x2048/1400x1050/filters:focal(39x0:3111x2048):format(png)/cdn.vox-cdn.com/uploads/chorus_image/image/49901753/netflixlogo.0.0.png',
    'Amazon': 'https://logos-world.net/wp-content/uploads/2021/02/Amazon-Prime-Video-Logo-700x394.png',
    'Hulu': 'https://assetshuluimcom-a.akamaihd.net/h3o/facebook_share_thumb_default_hulu.jpg'
}
def index(request):
    return render(request, "index.html")


def check_registration(request):
    if request.method == "POST":
        # errors handling
        errors = User.objects.basic_validator(request.POST)
        if len(errors) > 0:
            for error in errors.values():
                messages.error(request, error)
        else:
            hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
            new_user = User.objects.create(
                first_name = request.POST['first-name'], 
                last_name = request.POST['last-name'], 
                email = request.POST['email'], 
                password = hashed_pw)
            request.session['user_id'] = new_user.id
            return redirect('/subscriptions/sd/1')
    return redirect('/')


def check_login(request):
    if request.method == "POST":
        # errors handling
        errors = User.objects.login_validator(request.POST)
        if len(errors) > 0:
            for error in errors.values():
                messages.error(request, error)
        else:
            this_user = User.objects.get(email=request.POST['email'])
            request.session['user_id'] = this_user.id
            return redirect('/subscriptions/sd/1')
    return redirect ("/")


def logout(request):
    request.session.flush()
    return redirect('/')


def subscriptions(request, order_by, page_num):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])
        
        # order by director
        if order_by == "cn":
            order_by_field = "company"
        elif order_by == "st":
            order_by_field = "level"
        elif order_by == "mr":
            order_by_field = "monthly_rate"
        else:
            order_by_field = "start_date"
        
        my_subscriptions = Subscription.objects.filter(user = logged_user).order_by(order_by_field)
        
        # pagination driver
        p = Paginator(my_subscriptions, 5)
        page = p.page(page_num)
        num_of_pages = "a" * p.num_pages
        
        
        context = {
            'user': logged_user,
            'my_subscriptions': page,
            'num_of_pages': num_of_pages,
            'order_by': order_by,
            
        }
        return render(request, 'subscription.html', context)    
    return redirect('/')


def stats(request):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])
        all_subscriptions = Subscription.objects.filter(user = logged_user)
        data_list=[]
        for subcription in all_subscriptions:

            datas = DataPoint.objects.filter(subscription= subcription).all()
            data_list.append(datas)

        context = {
            'all_subscriptions_count': len(all_subscriptions),
            'user' : logged_user,
            'my_datas' : datas,
            'data_list' : data_list
        }
        return render(request, 'stats.html', context)    
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
            # errors handling
            # errors = User.objects.edit_profile_validator(request.POST)
            # if len(errors) > 0:
            #     for error in errors.values():
            #         messages.error(request, error)
            # else:

            logged_user = User.objects.get(id=request.session['user_id'])
            the_company = Company.objects.filter(company_name=request.POST['company'])
            if len(the_company) == 0:
                new_company= Company.objects.create(
                    company_name = request.POST['company'],
                    url = url_company[request.POST['company']]
                )
                new_photo = Photo.objects.create(
                    photo_of = new_company,
                    image_src= photo_company[request.POST['company']]
                )
                new_subscription = Subscription.objects.create(
                    user = logged_user,
                    the_company = new_company,
                    company = request.POST['company'],
                    level = request.POST['level'],
                    monthly_rate = request.POST['monthly_rate'],
                    start_date = request.POST['start_date'],
                    duration = request.POST['duration'],
                    
                )
            else:
                new_subscription = Subscription.objects.create(
                    user = logged_user,
                    the_company = the_company[0],
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
        if subscription_to_edit.user == logged_user:     

            context = {
                'logged_user': logged_user,
                'subscription_to_edit': subscription_to_edit,
            }
            return render(request, "editSubscription.html", context)
        return redirect("/subscriptions/sd/1")
    return redirect("/")


def process_edit_subscription(request, subscription_id):
    if 'user_id' in request.session:
        if request.method == "POST":
            # errors handling
            errors = Subscription.objects.basic_validator(request.POST)
            if len(errors) > 0:
                for error in errors.values():
                    messages.error(request, error)
            else:
                logged_user = User.objects.get(id=request.session['user_id'])
                subscription_to_edit = Subscription.objects.get(id=request.POST['subscription_id'])
                if subscription_to_edit.user == logged_user:     
                    subscription_to_edit.company = request.POST['company']
                    subscription_to_edit.level = request.POST['level']
                    subscription_to_edit.monthly_rate = request.POST['monthly_rate']
                    subscription_to_edit.start_date = request.POST['start_date']
                    subscription_to_edit.duration = request.POST['duration']
                    subscription_to_edit.save()
        return redirect(f"/edit_subscription/{ subscription_id }")            
    return redirect("/")


def delete_subscription(request):
    if 'user_id' in request.session:
        if request.method == "POST":
            logged_user = User.objects.get(id=request.session['user_id'])
            subscription_to_delete = Subscription.objects.get(id=request.POST['subscription_id'])
            if subscription_to_delete.user == logged_user:     
                subscription_to_delete.delete()
                return redirect("/user_account")
        return redirect("/subscriptions/sd/1")
    return redirect("/")


def renew_subscription(request, subscription_id):
    if 'user_id' in request.session:
        if request.method == "POST":
            logged_user = User.objects.get(id=request.session['user_id'])
            subscription_to_renew = Subscription.objects.get(id=request.POST['subscription_id'])
            if subscription_to_renew.user == logged_user:    
                subscription_to_renew.start_date = datetime.now()
                subscription_to_renew.save()
        return redirect(f"/edit_subscription/{ subscription_id }")            
    return redirect("/")




