from django.urls import path
from main.views import landing, add_food, donor_dashboard, consumer_dashboard, my_orders, add_order_item, view_item, add_to_cart, cart_view, decrease_quantity, remove_from_cart, increase_quantity, place_order, order_detail, expiring_soon_page, my_order_detail, cancel_order, consumer_notifications, donor_notifications
from mpesa.views import ProceedToPayment
urlpatterns = [
    #LANDING URL
    path('', landing, name='landing'),

    #URLS TO DIRECT THE USERS TO DIFFERENT DASHBOARDS ACCORDING TO THEIR ROLES
    path('donor_dashboard/', donor_dashboard, name='donor_dashboard'),
    path('consumer_dashboard/', consumer_dashboard, name='consumer_dashboard'),

    #URL TO ADD FOOD ITEM TO THE SYSTEM BY THE DONORS
    path('add_food/', add_food, name='add_food'),

    #URLS FOR THE ORDER
    path('my_orders/', my_orders, name='my_orders'),
    path('add_order_item/<int:fooditem_id>/', add_order_item, name='add_order_item'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path("my_orders_details/<int:order_id>/", my_order_detail, name="my_order_detail"),
    path("my_orders/<int:order_id>/cancel/", cancel_order, name="cancel_order"),

    #URLS TO THE CART WHERE CUSTOMERS CAN TEMPORARILY ADD ITEMS BEFORE FINALLY MAKING THE FINAL DECISION
    path('viewitem/<int:item_id>/', view_item, name='view_item'),
    path('cart/add/<int:fooditem_id>/', add_to_cart, name='add_to_cart'),
    path('cart_view/', cart_view, name='cart_view'),

    #URLS  FOR THE OPERRATION THAT CAN BE DONE BY THE CUSTOMER AFTER ADDING THE ITEMS TO THE CART
    path('decrease_quantity/<int:fooditem_id>/', decrease_quantity, name='decrease_quantity'),
    path('increase_quantity/<int:fooditem_id>/', increase_quantity, name='increase_quantity'),
    path('remove_from_cart/<int:fooditem_id>/', remove_from_cart, name='remove_from_cart'),

    #URL FOR THE CHECKOUT WHERE THE CUSTOER 
    path('place_order/', place_order, name='place_order'),

    #URL FOR THE EXPIRING SOON PAGE
    path("expiring-soon/", expiring_soon_page, name="expiring_soon_page_all"),
    path("expiring-soon/<int:pk>/", expiring_soon_page, name="expiring_soon_page"),
    
    #NOTIFICATIONS
    path('consumer_notifications/', consumer_notifications, name='consumer_notifications'),
    path('donor_notifications/', donor_notifications, name='donor_notifications'),

    #PAYMENTS
    path('payment/<int:order_id>/', ProceedToPayment, name="proceed_to_payment"),
    

]