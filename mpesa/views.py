from django.shortcuts import render, get_object_or_404
from django_daraja.mpesa.core import MpesaClient
from django.http import HttpResponse
from django.contrib import messages
from main.models import Order

# Create your views here.
def ProceedToPayment(request, order_id):
    cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    order = get_object_or_404(Order, id=order_id)
    response = ""
    amount = sum(item.fooditem.discounted_price * item.quantity for item in order.items.all())
    account_reference = 'STUDENTS_WELFARE'
    transaction_desc = 'Making donation to a student'
    callback_url = 'https://api.darajambili.com/express-payment'
    if request.method == 'POST':        
        #  extracting th user inputs
        phone_number = request.POST.get("phonenumber")      
        response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
        if response:
            messages.success(request,f"Sucess {response}")
        else:
            messages.success(request,"Error!")
    else:
        response = "Oops something went wrong" 
    context = {"response":response}
    return render(request, 'main/payments.html', context)
