from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from .models import *
from datetime import datetime
from datetime import date
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import base64
from io import BytesIO



url_company ={
    'Netflix': 'https://www.netflix.com/',
    'Amazon':'https://www.amazon.com/gp/video/offers/ref=dvm_us_dl_sl_go_brsa_mkw_svHxbIxqC-dc_pcrid_448130500925?ie=UTF8&gclid=EAIaIQobChMI8ou9zLX88QIVNQytBh2E7wIjEAAYASAAEgK2cvD_BwE&mrntrk=slid__pgrid_29008589832_pgeo_9033288_x__ptid_kwd-45697133742',
    'Hulu' : 'https://www.hulu.com/welcome'

}
photo_company ={
    'Netflix': 'https://cdn.vox-cdn.com/thumbor/QuS2QKQys3HhosKiV-2IuKhphbo=/39x0:3111x2048/1400x1050/filters:focal(39x0:3111x2048):format(png)/cdn.vox-cdn.com/uploads/chorus_image/image/49901753/netflixlogo.0.0.png',
    'Amazon' : 'https://logos-world.net/wp-content/uploads/2021/02/Amazon-Prime-Video-Logo-700x394.png',
    'Hulu' : 'https://assetshuluimcom-a.akamaihd.net/h3o/facebook_share_thumb_default_hulu.jpg'
}

default_companies = ['Amazon', 'Pandora', 'Hulu', 'Planet Fitness',"Sam's Club", 'YouTube', 'Masterclass','Disney+','P.volve', 'Netflix', "Annie's Creative Studio",'Philo', 'Scribd', 'Apple News+', 'Blinkist', 'Wondium', 'Kindle Unlimited', 'Epic!', 'Amazon Music Unlimited', 'Goddess Provisions Moon Wisdom']

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
            'photo_company': photo_company
            
        }
        return render(request, 'subscription.html', context)    
    return redirect('/')
    
def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(companies):
    # plt.switch_backend('AGG')
    # plt.figure(figsize=(10,5))
    # plt.title('subscription analysis')
    # plt.plot(x,y)
    # plt.xticks(rotaion=45)
    # plt.xlabel('date')
    # plt.ylabel('price')
    # plt.tight_layout()
    list_graph =[]
    for company_name in companies:
        company_date_price = companies[company_name]
        x = company_date_price.keys()
        y = company_date_price.values()
        plt.switch_backend('AGG')
        plt.figure(figsize=(10,5))
        plt.title(company_name)
        plt.plot(x,y)
        plt.xlabel('Dates')
        plt.ylabel('Prices')
        graph=get_graph()
        list_graph.append(graph)
    return(list_graph)

def stats(request):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])
        all_subscriptions = Subscription.objects.filter(user = logged_user)
        if len(all_subscriptions) < 1:
            context = {
                'all_subscriptions_count': len(all_subscriptions),
                'user' : logged_user,
            }
            return render(request, 'stats.html', context) 
        
        companies={}
        for subscription in all_subscriptions:
            company_name = subscription.company.company_name
            company_date_price = {}

            
            data_points = DataPoint.objects.filter(subscription= subscription).all()

            for data in data_points:
                date = data.created_at.date()
                price = float(data.monthly_rate)
                company_date_price[date] = price
            companies[company_name] = company_date_price
        
        list_graph = get_plot(companies)
        context = {
            'all_subscriptions_count': len(all_subscriptions),
            'user' : logged_user,
            'list_graph':list_graph
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
                messages.error(request, "Successfully updated profile")
        return redirect("/user_account")
    return redirect("/")


def add_subscription(request):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])
        all_companies = Company.objects.filter(entered_by_admin=True)
        context = {
            'logged_user': logged_user,
            'all_companies': all_companies,
        }
        return render(request, "add_subscription.html", context)
    return redirect("/")  


def process_add_subscription(request):
    if 'user_id' in request.session:
        if request.method == "POST":
            # errors handling
            # errors = Subscription.objects.basic_validator(request.POST)
            # if len(errors) > 0:
            #     for error in errors.values():
            #         messages.error(request, error)
            #         return redirect("/add_subscription")
            # else:
            logged_user = User.objects.get(id=request.session['user_id'])
            st_date = request.POST['start_date']
            sub_duration = request.POST['duration']

            # figure out time displacement
            # options ("Bi-annually", "Yearly", "Monthly", "Lifetime")
            if sub_duration == "Bi-annually":
                time_change = 2
            elif sub_duration == "Yearly":
                time_change = 1
            # elif sub_duration == "Monthly":
                # figure out time shift in days given the month
            # elif sub_duration == "Lifetime":

            s_date = st_date.split("-")

            if sub_duration == "Bi-annually" or sub_duration == "Yearly":
                add_time = int(s_date[0])+time_change
                s_date[0] = str(add_time)
                renew_date = "-".join(s_date)
                date_plus_time = datetime.strptime(renew_date, '%Y-%m-%d')    
            # elif sub_duration == "Monthly":
            #     add_time = int(s_date[1])+time_change
            #     # Need Logic to handle month spillover
            #     s_date[1] = str(add_time)
            #     renew_date = "-".join(s_date)
            #     date_plus_time = datetime.datetime.strptime(renew_date, '%Y-%m-%d')
            # else:
            #     date_plus_time = None

            # gets or creates company to be subscribed to 
            # if request.POST['company_id'] == "-1":
            if request.POST['company_name'] not in default_companies:
                this_company = Company.objects.create(
                    company_name = request.POST['company_name']
                )
            else:
                this_company = Company.objects.get(id= request.POST['company_id'])

            # creates new subscription
            ###
            new_subscription = Subscription.objects.create(
                user = logged_user,
                company = this_company,
                account = request.POST['account'],
                level = request.POST['level'],
                monthly_rate = Decimal(request.POST['monthly_rate']),
                start_date = st_date,
                renew_by_date = date_plus_time,
                duration = sub_duration,
            )
            # sets initial datapoint for the subscription
            DataPoint.objects.create(
                subscription = new_subscription,
                monthly_rate = Decimal(request.POST['monthly_rate']),
            )
            return redirect(f"/edit_subscription/{ new_subscription.id }")
        return redirect("/add_subscription")
    return redirect("/")  

def edit_subscription(request, subscription_id):
    if 'user_id' in request.session:
        logged_user = User.objects.get(id=request.session['user_id'])
        subscription_to_edit = Subscription.objects.get(id=subscription_id)
        if subscription_to_edit.user == logged_user:  
            all_companies = Company.objects.filter(entered_by_admin=True)   
            context = {
                'logged_user': logged_user,
                'subscription_to_edit': subscription_to_edit,
                'all_companies': all_companies,
            }
            return render(request, "editSubscription.html", context)
        return redirect("/subscriptions/sd/1")
    return redirect("/")


def process_edit_subscription(request, subscription_id):
    if 'user_id' in request.session:
        if request.method == "POST":
            # errors = Subscription.objects.basic_validator(request.POST)
            # if len(errors) > 0:
            #     for error in errors.values():
            #         messages.error(request, error)
            # else:
            logged_user = User.objects.get(id=request.session['user_id'])
            subscription_to_edit = Subscription.objects.get(id=request.POST['subscription_id'])
            if subscription_to_edit.user == logged_user:    

                if request.POST['company_id'] == "-1":
                    if subscription_to_edit.company.entered_by_admin:
                        this_company = Company.objects.create(
                        company_name = request.POST['company_name']
                        )
                        subscription_to_edit.company = this_company
                    else:
                        if subscription_to_edit.company.company_name != request.POST['company_name']:
                            company_to_delete_id = subscription_to_edit.company.id
                            company_to_delete = Company.objects.get(id=company_to_delete_id)
                            this_company = Company.objects.create(
                                company_name = request.POST['company_name']
                            )
                            subscription_to_edit.company = this_company
                            company_to_delete.delete()
                else:
                    if subscription_to_edit.company.entered_by_admin:
                        this_company = Company.objects.get(id= request.POST['company_id'])
                        subscription_to_edit.company = this_company
                    else:
                        company_to_delete_id = subscription_to_edit.company.id
                        company_to_delete = Company.objects.get(id=company_to_delete_id)
                        this_company = Company.objects.get(id= request.POST['company_id'])
                        subscription_to_edit.company = this_company
                        company_to_delete.delete()






                subscription_to_edit.level = request.POST['level']




                if subscription_to_edit.monthly_rate != Decimal(request.POST['monthly_rate']):
                    price_change = subscription_to_edit.monthly_rate - Decimal(request.POST['monthly_rate'])
                    DataPoint.objects.create(
                        subscription = subscription_to_edit,
                        monthly_rate = Decimal(request.POST['monthly_rate']),
                        price_change = price_change,
                    )
                    subscription_to_edit.monthly_rate = Decimal(request.POST['monthly_rate'])



                st_date = request.POST['start_date']
                sub_duration = request.POST['duration']

                # figure out time displacement
                # options ("Bi-annually", "Yearly", "Monthly", "Lifetime")
                if sub_duration == "Bi-annually":
                    time_change = 2
                elif sub_duration == "Yearly":
                    time_change = 1
                # elif sub_duration == "Monthly":
                    # figure out time shift in days given the month
                # elif sub_duration == "Lifetime":

                s_date = st_date.split("-")

                if sub_duration == "Bi-annually" or sub_duration == "Yearly":
                    add_time = int(s_date[0])+time_change
                    s_date[0] = str(add_time)
                    renew_date = "-".join(s_date)
                    date_plus_time = datetime.strptime(renew_date, '%Y-%m-%d')    
                # elif sub_duration == "Monthly":
                #     add_time = int(s_date[1])+time_change
                #     # Need Logic to handle month spillover
                #     s_date[1] = str(add_time)
                #     renew_date = "-".join(s_date)
                #     date_plus_time = datetime.datetime.strptime(renew_date, '%Y-%m-%d')
                # else:
                #     date_plus_time = None



                subscription_to_edit.start_date = st_date
                subscription_to_edit.duration = sub_duration
                subscription_to_edit.renew_by_date = date_plus_time



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
                return redirect("/subscriptions/sd/1")
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




