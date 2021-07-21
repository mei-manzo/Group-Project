from django.urls import path     
from . import views
urlpatterns = [
    path('', views.index),
    # path('success', views.success),
    path('check_registration', views.check_registration),
    path('check_login', views.check_login),
    path('logout', views.logout),
    path('subscriptions', views.subscriptions),
    path('subscriptions/stats', views.stats),



    path('user_account', views.user_account),
    path('process_edit_user', views.process_edit_user),


    path('add_subscription', views.add_subscription),
    path('process_add_subscription', views.process_add_subscription),
    path('edit_subscription/<int:subscription_id>', views.edit_subscription),
    path('process_edit_subscription', views.process_edit_subscription),

]