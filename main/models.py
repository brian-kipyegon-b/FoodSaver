from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# Create your models here.
class FoodItem(models.Model):
    name = models.CharField(max_length=200)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.00)])
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.00)])
    stock = models.PositiveIntegerField()
    expiry_date = models.DateField()
    image = models.ImageField(upload_to="FoodItems/", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_orders")  # customer
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donor_orders")    # donor
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Order #{self.id} for donor {self.donor.username}"


class Order_item(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    fooditem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.fooditem.name}"
    

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True) 

    def __str__(self):
        return f"{self.user.username} - {self.action}"
    
class Notification(models.Model):
    TYPE_CHOICES = [
        ("order", "Order"),
        ("delivery", "Delivery"),
        ("payment", "Payment"),
        ("general", "General"),
    ]
    ROLE_CHOICES = [
        ("consumer", "Consumer"),
        ("donor", "Donor"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.user.username} - {self.message[:30]}"