from django.db import models
from django.contrib.auth.models import AbstractUser,User,Group, Permission
# Create your models here.
from django.db import models
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=10000, null=True, blank=True)
    phoneNumber = models.CharField(max_length=100, null=True, blank=True)
    is_Sell= models.IntegerField(default=0)
    is_Admin = models.IntegerField(default=0)
    def __str__(self):
        return self.user.username
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    sale = models.IntegerField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(null= True, blank= True)
    sellerId = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    sizes = models.CharField(max_length=100000,null=True)
    sell = models.IntegerField(default=0,null=True)
    def __str__(self):
        return self.name
    def getSale(self):
        if self.sale:
            return self.price - self.price*self.sale//100
        return self.price
    def getSize(self):
        return self.sizes.split(",")
    
class Order(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.IntegerField(null=True)
    address = models.CharField(max_length=10000, null=True, blank=True)
    phoneNumber = models.CharField(max_length=100, null=True, blank=True)
    status = models.IntegerField(default=0)

    def __str__(self):
        return f"Order {self.id}"
    def getItem(self):
        cnt = 0
        order = Order.objects.get(account = self.account,status = 0)
        orderitems = OrderItem.objects.filter(order = order)
        for orderitem in orderitems:
            cnt+=orderitem.quantity
        return cnt
    def getTotal(self):
        total = 0
        order = Order.objects.get(account = self.account,status = 0)
        orderitems = OrderItem.objects.filter(order = order)
        for orderitem in orderitems:
            total+=orderitem.getPrice()
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null = True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField()
    total_price = models.IntegerField(null=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"OrderItem {self.id}"
    def getPrice(self):
        return self.price*self.quantity