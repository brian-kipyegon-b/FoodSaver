from django.shortcuts import render, redirect, get_object_or_404
from . models import FoodItem, Activity, Order, Order_item, Notification
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta


# Create your views here.
def landing(request):
    context = {}
    return render(request, 'main/landing.html', context)

@login_required
def add_food(request):
    if request.method == "POST":
        name = request.POST.get('name')
        original_price = request.POST.get('original_price')
        discounted_price = request.POST.get('discounted_price')
        expiry_date = request.POST.get('expiry_date')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')
        if not name or not expiry_date:
            messages.error(request, "Name and expiry date are required.")
            return redirect(add_food)

        food = FoodItem.objects.create(name=name, original_price=original_price, discounted_price=discounted_price, expiry_date=expiry_date, image=image, stock=stock, created_by=request.user)
        Activity.objects.create(user=request.user, action=f"Added {food.name} to your inventory.")
        messages.success(request, f"{food.name} added successfully")
        return redirect('donor_dashboard')
    
    return render(request, 'main/add_food.html')

@login_required
def donor_dashboard(request):
    fooditems = FoodItem.objects.all().order_by('-id')

    total_fooditems = FoodItem.objects.count()
    total_orders = Order.objects.count()

    activitys = Activity.objects.all()[:3]
    
    food_saved = FoodItem.objects.all().count()
    unread_count = request.user.notifications.filter(is_read=False, role="donor").count()
    context = {
        "fooditems": fooditems,
        "total_fooditems": total_fooditems,
        "total_orders": total_orders,
        'food_saved': food_saved,
        'activitys':activitys,
        'unread_count':unread_count,
    }

    return render(
        request,
        "main/donor_dashboard.html",
        context
    )

@login_required
def consumer_dashboard(request):
    items = FoodItem.objects.filter(created_by__userprofile__role='donor')
    today = timezone.now().date()

    available_items = items.filter(expiry_date__gte=today)

    soon_threshold = today + timedelta(days=3)
    expring_soon = items.filter(expiry_date__gte=today, expiry_date__lte=soon_threshold)
    fooditems = available_items.order_by('-id')
    total_fooditems = available_items.count()
    total_orders = Order.objects.count()
    orders = Order.objects.filter(user=request.user)
    total_savings = 0

    for order in orders:
        for item in order.items.all():
            savings = (item.fooditem.original_price - item.fooditem.discounted_price) * item.quantity
            total_savings += savings
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'main/consumer_dashboard.html', {"fooditems":fooditems, 'total_fooditems':total_fooditems, "total_orders":total_orders, 'total_savings':total_savings, "available_items":available_items, "expring_soon":expring_soon, "unread_count":unread_count})

@login_required
def add_order_item(request, fooditem_id):
    fooditem = get_object_or_404(FoodItem, id=fooditem_id)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                messages.error(request, "The quantity must be atleast 1")
                return redirect('add_order_item', fooditem_id=fooditem.id)
            
            order = Order.objects.create(user=request.user)
            
            Order_item.objects.create(
                fooditem = fooditem,
                quantity = quantity,
                order = order
            )

        except Exception as e:
            messages.error(request, f"Error creating order: {e}")
            return redirect("fooditem_detail", fooditem_id=fooditem.id)
    
    return render(request, 'main/add_order_item.html')

@login_required
def order(request, ):
    fooditem = get_object_or_404(FoodItem, id=fooditem.id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        if quantity < 1 or quantity > fooditem.quantity:
            messages.error(request, "You have entered invalid quantity.")
            return redirect('make_order',  fooditem_id=fooditem.id)
        
        total_price = fooditem.discounted_price * quantity 

        order = Order.objects.create(user=request.user, fooditem=fooditem, quantity=quantity, total_price=total_price)

        fooditem.quantity -= quantity
        fooditem.save()

        messages.success(request, "Your order was placed successfully.")
    return redirect('my_orders')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/orders.html', {"orders":orders})

@login_required
def cancel_order(request, order_id):
    # Get the order belonging to the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Restore stock for each item in the order
    for order_item in order.items.all():
        fooditem = order_item.fooditem
        fooditem.stock += order_item.quantity
        fooditem.save()
    # Option 1: Delete the order completely
    order.delete()
    messages.success(request, "Order cancelled and stock restored.")

    order.status = "cancelled"
    order.save()
    messages.success(request, "Order marked as cancelled and stock restored.")

    return redirect('my_orders')

@login_required
def my_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = []

    total_price = 0
    for item in order.items.all():
        subtotal = item.quantity * item.fooditem.discounted_price
        total_price += subtotal
        items.append({
            'fooditem': item.fooditem,
            'quantity': item.quantity,
            'price': item.fooditem.discounted_price,
            'subtotal': subtotal
        })

    context = {
        'order': order,
        'items': items,
        'total_price': total_price,
    }
    return render(request, 'main/my_order_detail.html', context)

@login_required
def view_cartitem(request):
    return render(request, 'main/viewitem.html')

@login_required
def view_item(request):
    return render(request, 'main/viewitem.html')

@login_required
def add_to_cart(request, fooditem_id):
    # Get the cart from session (or create a new one)
    cart = request.session.get('cart', {})
    # Make sure the food item exists
    fooditem = get_object_or_404(FoodItem, id=fooditem_id)
    # Convert ID to string (session keys must be strings)
    item_id = str(fooditem.id)
    # Add or increase quantity
    cart[item_id] = cart.get(item_id, 0) + 1
    # Save cart back to session
    request.session['cart'] = cart
    # Redirect to cart page
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for item_id, qty in cart.items():
        fooditem = get_object_or_404(FoodItem, id=item_id)
        subtotal = fooditem.discounted_price * qty
        total += subtotal
        items.append({
            'fooditem': fooditem,
            'quantity': qty,
            'subtotal': subtotal
        })

    context = {
        'items': items,
        'total': total
    }
    return render(request, 'main/cart.html', context)

@login_required
def decrease_quantity(request, fooditem_id):
    cart = request.session.get('cart', {})
    item_id = str(fooditem_id)

    if item_id in cart:
        if cart[item_id] > 1:
            cart[item_id] -= 1   # reduce by 1
        else:
            cart[item_id] = 1    #to prevent the item from being removed from the from the cart

    request.session['cart'] = cart
    return redirect('cart_view')

@login_required
def increase_quantity(request, fooditem_id):
    cart = request.session.get('cart', {})
    item_id = str(fooditem_id)

    fooditem = get_object_or_404(FoodItem, id=fooditem_id)
    # Current quantity in cart
    current_qty = cart.get(item_id, 0)
    #  Check stock before increasing
    if current_qty < fooditem.stock:
        cart[item_id] = current_qty + 1
    else:
        messages.error(request, f"Only {fooditem.stock} {fooditem.name} available in stock.")
    request.session['cart'] = cart
    return redirect('cart_view')

@login_required
def remove_from_cart(request, fooditem_id):
    cart = request.session.get('cart', {})
    item_id = str(fooditem_id)
    # Remove item completely if it exists
    if item_id in cart:
        del cart[item_id]
    # Save cart back to session
    request.session['cart'] = cart
    return redirect('cart_view')

@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('cart_view')
    # Create a new order for the logged-in user
    order = Order.objects.create(user=request.user)
    for item_id, qty in cart.items():
        fooditem = get_object_or_404(FoodItem, id=item_id)
        # Check stock before reducing
        if qty > fooditem.stock:
            messages.error(request,f"Not enough stock for {fooditem.name}. Available: {fooditem.stock}")
            return redirect('cart_view')
        # Reduce stock safely
        fooditem.stock -= qty
        fooditem.save()
        # Create order item
        Order_item.objects.create(order=order, fooditem=fooditem, quantity=qty)
    # Clear cart after successful checkout
    request.session['cart'] = {}
    # Create notifications
    Notification.objects.create(user=fooditem.created_by, role="donor", type="order", message=f"{request.user.username} ordered {qty} of {fooditem.name}. Remaining stock: {fooditem.stock}", is_read=False)
    Notification.objects.create(user=request.user, role="consumer", type="order", message=f"Order #{order.id} has been placed successfully!")
    messages.success(request, f"Order #{order.id} placed successfully!")
    return redirect('order_detail', order_id=order.id)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = []

    total_price = 0
    for item in order.items.all():
        subtotal = item.quantity * item.fooditem.discounted_price
        total_price += subtotal
        items.append({
            'fooditem': item.fooditem,
            'quantity': item.quantity,
            'price': item.fooditem.discounted_price,
            'subtotal': subtotal
        })

    context = {
        'order': order,
        'items': items,
        'total_price': total_price,
    }
    return render(request, 'main/order_detail.html', context)

@login_required
def expiring_soon_page(request, pk=None):
    today = timezone.now().date()
    soon_threshold = today + timedelta(days=3)

    # Get all expiring soon items
    expiring_soon = FoodItem.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=soon_threshold
    ).order_by('expiry_date')
    selected_item = None
    if pk:
        selected_item = get_object_or_404(FoodItem, pk=pk)

    return render(request, "main/expiry_alerts.html", {
        "expiring_soon": expiring_soon,
        "selected_item": selected_item,
    })

@login_required
def consumer_notifications(request):
    notes = request.user.notifications.filter(role="consumer").order_by('-created_at')
    unread_count = request.user.notifications.filter(is_read=False).count()
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'main/consumer_notifications', {"notes":notes, "unread_count":unread_count})

@login_required
def donor_notifications(request):
    notes = request.user.notifications.filter(role="donor").order_by('-created_at')
    unread_count = request.user.notifications.filter(is_read=False).count()
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'main/donor_notifications.html', {"notes":notes, "unread_count":unread_count})
