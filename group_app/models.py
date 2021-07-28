from django.db import models
import re
import bcrypt
from decimal import Decimal


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
MONEY_REGEX = re.compile('|'.join([
    r'^\$?(\d*(\.\d\d?)?|\d+)$',
    ]))


class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        email = postData['email']
        if len(postData['first-name']) <2:
            errors["first_name"]="First name should be at least 2 characters"
        if len(postData['last-name']) <2:
            errors["last_name"]="Last name should be at least 2 characters"
        if not EMAIL_REGEX.match(postData['email']):             
            errors['email'] = ("Invalid email address!")
        if len(User.objects.filter(email=email)) >= 1:
            errors["email"]="Email is already in use"
        if len(postData['password']) < 8:
            errors["password"]="Password must be at least 8 characters"
        if postData['password'] != postData['confirm-password']:
            errors["password"]="Passwords do not match"
        return errors
        
    def login_validator(self, postData):
        errors = {}
        # email = postData['email']
        existing_user = User.objects.filter(email=postData['email'])
        if len(postData['email']) == 0:
            errors['email'] = "Must enter an email"
        elif len(existing_user) == 0: 
            errors['email'] = "Email is not registered"
        elif len(postData['password']) < 8:
            errors['password'] = "Must enter a password 8 characters or longer"
        elif bcrypt.checkpw(postData['password'].encode(), existing_user[0].password.encode()) != True:
            errors['password'] = "Email and password do not match"
        return errors

    def edit_profile_validator(self, postData):
        errors = {}

        if len(postData['first_name']) < 2 or not NAME_REGEX.match(postData['first_name']):
            errors['first_name'] = "Please enter a valid first name"
        if len(postData['last_name']) < 2 or not NAME_REGEX.match(postData['last_name']):
            errors['last_name'] = "Please enter a valid last name"
        if len(postData['email']) < 2 or not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Please enter a valid email"
        user = self.get(id=postData['user_id'])
        if user.email != postData['email']:
            email_in_db = self.filter(email = postData['email'])
            if email_in_db:
                errors['email'] = "This email is already registered to another user"
        return errors


class SubscriptionManager(models.Manager): #validates subscription data
    def basic_validator(self, postData):
        errors = {}

        # if len(postData['company']) <2:
        #     errors["company"]="Company should be at least 2 characters."
        if len(postData['level']) <2:
            errors["level"]="Subscription level should be at least 2 characters."
        if len(postData['monthly_rate']) < 1:
            errors["monthly_rate"]="Must enter a monthly rate"
        if not MONEY_REGEX.match(postData['monthly_rate']):             
            errors['monthly_rate'] = "Invalid monetary value!"
        if len(postData['start_date']) < 1:
            errors["start_date"]="Must select a start date."
        if len(postData['duration']) < 1:
            errors["duration"]="Must select a duration."
        if len(postData['start_date']) < 1:
            errors["start_date"]="Must select a valid start date." 
        return errors
        

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add = True)
    objects = UserManager()


class Company(models.Model): #one-to-many with photos, subscriptions
    company_name = models.CharField(max_length=255)
    entered_by_admin = models.BooleanField(default=False)
    url = models.TextField(null=True, blank=True)#made text field in case urls are very long
    # to call in templates use:
    # <img src="{% static 'img/'|add:company.img_src %}" alt="{{ company.img_alt }}">
    image_src = models.TextField(default="no_img_available.jpg", null=True, blank=True)#made text field in case img urls are very long
    image_alt = models.CharField(default="no image available",max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add = True)

class Subscription(models.Model): #company's / user's subscriptions
    user = models.ForeignKey(
        User, 
        related_name = "subscriptions", 
        on_delete = models.CASCADE
    )
    company = models.ForeignKey(
        Company, 
        related_name = "company_subscriptions", 
        on_delete = models.CASCADE
    )
    account = models.CharField(max_length = 255) #for different accounts from same company
    # company = models.CharField(max_length = 255)#hulu, amazon prime, etc
    level = models.CharField(max_length = 255) # for premium, basic, first tier etc
    monthly_rate = models.DecimalField(decimal_places=2, max_digits=5)
    start_date = models.DateField()#can be selected from a clickable calender to deal with formatting
    renew_by_date = models.DateField(null=True, blank=True)
    # due_date = models.CharField(max_length = 10)#made charfield so that can designate just one day of month - the "9th" of every month etc.
    duration = models.CharField(max_length = 255) #can select from dropdown? auto-renew, 12-month, etc
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add = True)
    objects = SubscriptionManager()#use to validate subscription data

class DataPoint(models.Model):  #connect to subscription (can show one, or all)
    subscription = models.ForeignKey(
        Subscription,
        related_name = "subscription_datapoints",
        on_delete=models.CASCADE,
    )
    monthly_rate = models.DecimalField(decimal_places=2, max_digits=5)
    price_change = models.DecimalField(default = 0.00, decimal_places=2, max_digits=5)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add = True)



