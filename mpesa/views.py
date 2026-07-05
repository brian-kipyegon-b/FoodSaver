from django.shortcuts import render, get_object_or_404, redirect
from django_daraja.mpesa.core import MpesaClient
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import Order

# Create your views here.
@login_required
def ProceedToPayment(request, order_id):
    cl = MpesaClient()
    order = get_object_or_404(Order, id=order_id, user=request.user)

    amount = int(sum(item.fooditem.discounted_price * item.quantity for item in order.items.all()))
    account_reference = 'FoodSaver'
    transaction_desc = 'Pay for your ordered items in FoodSaver'
    callback_url = 'https://yourdomain.com/mpesa/callback/'

    if request.method == 'POST':
        phone_number = request.POST.get("phone_number", "").strip()
        if not phone_number:
            messages.error(request, "Please enter your phone number.")
        elif not phone_number.isdigit():
            messages.error(request, "Enter a valid Safaricom number in format 2547XXXXXXXX.")
        else:
            try:
                response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
                if response:
                    messages.success(request, "Payment initiated. Enter your M-Pesa PIN to complete.")
                    return redirect('my_order_detail', order_id=order.id)
                else:
                    messages.error(request, "Error while initiating payment.")
            except Exception as e:
                messages.error(request, f"Payment failed: {e}")
    return render(request, 'main/payments.html', {"order": order, "total_price": amount})

