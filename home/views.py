from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
import os
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        categories = Category.objects.all()
        products = Product.objects.all()
        paginator = Paginator(products, 3) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'order':order}
        return render(request, 'index.html',context)
    else:
        categories = Category.objects.all()
        products = Product.objects.all()
        paginator = Paginator(products, 3) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories}
        return render(request, 'index.html',context)
def category(request):
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        categoryId = request.GET['categoryId']
        category = Category.objects.get(id = categoryId)
        categories = Category.objects.all()
        products = Product.objects.filter(category = category)
        paginator = Paginator(products, 3) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'order':order}
        return render(request, 'category.html',context)
    else:
        categoryId = request.GET['categoryId']
        category = Category.objects.get(id = categoryId)
        categories = Category.objects.all()
        products = Product.objects.filter(category = category)
        paginator = Paginator(products, 3) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories}
        return render(request, 'category.html',context)

def detail(request):
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        categories = Category.objects.all()
        productId = request.GET['id']
        product = Product.objects.get(id = productId)
        hotProducts = Product.objects.order_by('-sell')[:4]
        context = {'product': product,'categories':categories,'order':order,'hotProducts':hotProducts}
        return render(request, 'detail.html',context)
    else:
        categories = Category.objects.all()
        productId = request.GET['id']
        product = Product.objects.get(id = productId)
        hotProducts = Product.objects.order_by('-sell')[:4]
        context = {'product': product,'categories':categories,'hotProducts':hotProducts}
        return render(request, 'detail.html',context)

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']

        if password == repassword:
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('register')
            elif User.objects.filter(username = username).exists():
                messages.info(request, 'Username Already Used')
                return redirect('register')
            else:
                user = User.objects.create_user(username = username, email=email, password=password)
                user.save();
                account = Account(user= user)
                account.save();
                return redirect('login')
        else:
            messages.info(request, 'repeatpass is wrong')
            return redirect('register')
    else:
        return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username = username, password = password)
        if user is None:
            messages.info(request, 'Wrong username or password')
            return redirect('login')
        else:
            auth.login(request, user)
            return redirect('index')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('index')

def profile(request):
    if request.user.is_authenticated:
        user = request.user.account
        if request.method == "POST":
            address = request.POST['address']
            phone = request.POST['phone']
            user.address = address
            user.phoneNumber = phone
            user.save()
            return redirect('index')
        context = {'user': user}
    return render(request, 'profile.html', context)

def account(request):
    if request.user.is_authenticated:
        if request.user.account.is_Admin:
            customers = Account.objects.all()
            sellers = Account.objects.filter(is_Sell= 1)
            admins = Account.objects.filter(is_Admin = 1)
            context = {'customers':customers,'sellers':sellers,'admins':admins}
            return render(request, 'account.html', context)
        return render(request,'error.html')
    return redirect('login')

def registerAdmin(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        address= request.POST['address']
        phone= request.POST['phone']
        password = request.POST['password']
        repassword = request.POST['repassword']

        if password == repassword:
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('registerAdmin')
            elif User.objects.filter(username = username).exists():
                messages.info(request, 'Username Already Used')
                return redirect('registerAdmin')
            else:
                user = User.objects.create_user(username = username, email=email, password=password)
                user.save();
                account = Account(user= user, address= address, phoneNumber = phone, is_Admin = 1, is_Sell = 0)
                account.save();
                return redirect('account')
        else:
            messages.info(request, 'repeatpass is wrong')
            return redirect('registerAdmin')
    else:
        return render(request, 'registerAdmin.html')

def product(request):
    if request.user.is_authenticated:
        if request.user.account.is_Sell:
            user = request.user.account
            categories = Category.objects.all()
            products = Product.objects.filter(sellerId = user)
            context = {'products':products,'categories':categories}
            for category in categories:
                if category.product_set.count()== 0:
                    category.delete()
            return render(request, 'product.html', context)
        return render(request,'error.html')
    return redirect('login')

def addProduct(request):
    if request.user.is_authenticated:
        user = request.user.account
        if request.method == "POST":
            name = request.POST['name']
            image_file = request.FILES['image']  # Lấy tệp tin ảnh từ request.FILES
            price = request.POST['price']
            sale = request.POST['sale']
            description = request.POST['description']
            category_id = request.POST['category']
            sizes = request.POST['sizes']
            if category_id != "new_category":
                category = Category.objects.get(id=category_id)
            else:
                new_category = request.POST['new_category']
                tmp = Category.objects.all()
                ok = 0
                for i in tmp:
                    if i.name == new_category:
                        category = Category.objects.get(name = new_category)
                        ok = 1
                        break
                if ok == 0:
                    category = Category.objects.create(name = new_category)
            # Tạo đường dẫn tới thư mục 'static/images'
            image_path = settings.MEDIA_ROOT
            # Lưu tệp ảnh vào thư mục 'static/images'
            file_path = default_storage.save(f'{image_path}/{image_file.name}', ContentFile(image_file.read()))
            # Lấy đường dẫn tương đối đến tệp ảnh đã lưu
            relative_path = default_storage.url(file_path)
            product = Product(name=name, image=relative_path, price=price, description=description, category=category, sellerId=user,sizes = sizes,sale = sale)
            product.save()
        return redirect('product')
    return redirect('login')

def deleteAccount(request):
    if request.user.is_authenticated:
        id = request.GET['id']
        user = User.objects.get(id = id)
        user.delete()
        return redirect('account')
    return redirect('login')


def deleteProduct(request):
    if request.user.is_authenticated:
        productId = request.GET['productId']
        product = Product.objects.get(id = productId)
        image_file_path = f'{settings.MEDIA_ROOT}/{product.image.name}'
        if default_storage.exists(image_file_path):
            default_storage.delete(image_file_path)
        product.delete()
        return redirect('product')
    return redirect('login')

def editProduct(request):
    if request.user.is_authenticated:
        productId = request.GET['productId']
        product = Product.objects.get(id = productId)
        user = request.user.account
        if request.method == "POST":
            name = request.POST['name']
            price = request.POST['price']
            sale = request.POST['sale']
            description = request.POST['description']
            category_id = request.POST['category']
            sizes = request.POST['sizes']
            if category_id != "new_category":
                category = Category.objects.get(id=category_id)
            else:
                new_category = request.POST['new_category']
                tmp = Category.objects.all()
                ok = 0
                for i in tmp:
                    if i.name == new_category:
                        category = Category.objects.get(name = new_category)
                        ok = 1
                        break
                if ok == 0:
                    category = Category.objects.create(name = new_category)
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # Tạo đường dẫn tới thư mục 'static/images'
                image_path = settings.MEDIA_ROOT
                image_file_path = f'{settings.MEDIA_ROOT}/{product.image.name}'
                if default_storage.exists(image_file_path):
                    default_storage.delete(image_file_path)
                # Lưu tệp ảnh vào thư mục 'static/images'
                file_path = default_storage.save(f'{image_path}/{image_file.name}', ContentFile(image_file.read()))
                # Lấy đường dẫn tương đối đến tệp ảnh đã lưu
                relative_path = default_storage.url(file_path)
                product.image = relative_path
            product.name = name
            product.price = price
            product.description = description
            product.category = category
            product.sellerId = user
            product.sizes = sizes
            product.sale = sale
            product.save()
            return redirect('product')
        categories = Category.objects.all()
        context = {'product':product,'categories':categories}
        return render(request,'editProduct.html',context)
    return redirect('login')


def cart(request):
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        orderitems = OrderItem.objects.filter(order= order)
        if request.method == "POST":
            address = request.POST['address']
            phone = request.POST['phone']
            order.address = address
            order.phoneNumber = phone
            order.total_amount = order.getTotal()
            order.status = 1
            order.save()
            for orderitem in orderitems:
                orderitem.total_price = orderitem.getPrice()
                orderitem.save()
            context = {'order':order,'orderitems': orderitems,'user': user}
            return render(request, 'receipt.html', context)
        context = {'order':order,'orderitems': orderitems,'user': user}
        return render(request, 'cart.html', context)
    return redirect('login')

def chooseSize(request):
    if request.user.is_authenticated:
        user = request.user.account
        orderitemid = request.GET['orderitemId']
        size = request.GET['size']
        order = Order.objects.get(account = user, status = 0)
        orderitem = OrderItem.objects.get(order = order,id = orderitemid)
        orderitem.size = size
        orderitem.save()
        return redirect('cart')
    return redirect('login')

def addToCart(request):
    if request.user.is_authenticated:
        productId = request.GET['productId']
        product = Product.objects.get(id = productId)
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        orderitem, created = OrderItem.objects.get_or_create(order= order, product = product, price = product.getSale())
        if not created:
            orderitem.quantity+=1
            orderitem.save()
        return redirect('cart')
    return redirect('login')

def deleteFromCart(request):
    if request.user.is_authenticated:
        user = request.user.account
        orderitemid = request.GET['orderitemId']
        order = Order.objects.get(account = user, status = 0)
        orderitem = OrderItem.objects.get(order = order,id = orderitemid)
        orderitem.delete()
        return redirect('cart')
    return redirect('login')

def yourOrder(request):
    if request.user.is_authenticated:
        user = request.user.account
        orders = Order.objects.filter(account = user).exclude(status=0).order_by('-id')
        context = {'orders':orders}
    return render(request,'yourOrder.html', context)


def cancelOrder(request):
    if request.user.is_authenticated:
        orderId = request.GET['orderId']
        order = Order.objects.get(id = orderId)
        order.status = -1
        order.save()
        return redirect('yourOrder')
    return redirect('login')

def completeOrder(request):
    if request.user.is_authenticated:
        orderId = request.GET['orderId']
        order = Order.objects.get(id = orderId)
        orderitems = OrderItem.objects.filter(order= order)
        for orderitem in orderitems:
            product = orderitem.product
            product.sell += orderitem.quantity
            product.save()
        order.status = 2
        order.save()
        return redirect('yourOrder')
    return redirect('login')

def customerOrder(request):
    if request.user.is_authenticated:
        user = request.user.account
        orders = Order.objects.filter(orderitem__product__sellerId=user).order_by('-id')
        context = {'orders':orders,'user':user}
        return render(request, 'customerOrder.html', context)
    return redirect('login')

def registerSeller(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']

        if password == repassword:
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('register')
            elif User.objects.filter(username = username).exists():
                messages.info(request, 'ShopName Already Used')
                return redirect('registerSeller')
            else:
                user = User.objects.create_user(username = username, email=email, password=password)
                user.save();
                account = Account(user= user,is_Sell = 1)
                account.save();
                return redirect('login')
        else:
            messages.info(request, 'repeatpass is wrong')
            return redirect('registerSeller')
    else:
        return render(request, 'registerSeller.html')


def myshop(request):
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        id = request.GET['id']
        account = Account.objects.get(id = id)
        products = Product.objects.filter(sellerId = account)
        categories = set()
        for product in products:
            categories.add(product.category)
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'order':order,'account':account}
        return render(request, 'myshop.html',context)
    else:
        id = request.GET['id']
        account = Account.objects.get(id = id)
        products = Product.objects.filter(sellerId = account)
        categories = set()
        for product in products:
            categories.add(product.category)
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'account':account}
        return render(request, 'myshop.html',context)
    
def categoryShop(request):
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        categoryId = request.GET['categoryId']
        category = Category.objects.get(id = categoryId)
        sellerId = request.GET.get('sellerId')
        
        account = Account.objects.get(id = sellerId)
        products = Product.objects.filter(sellerId= account)
        categories = set()
        for product in products:
            categories.add(product.category)
        products = Product.objects.filter(category = category,sellerId= account)
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'order':order,'account':account}
        return render(request, 'categoryShop.html',context)
    else:
        categoryId = request.GET['categoryId']
        category = Category.objects.get(id = categoryId)
        sellerId = request.GET.get('sellerId')
        
        account = Account.objects.get(id = sellerId)
        products = Product.objects.filter(sellerId= account)
        categories = set()
        for product in products:
            categories.add(product.category)
        products = Product.objects.filter(category = category,sellerId= account)
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'account':account}
        return render(request, 'categoryShop.html',context)

def detailShop(request):
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        sellerId = request.GET.get('sellerId')
        
        account = Account.objects.get(id = sellerId)
        products = Product.objects.filter(sellerId= account)
        categories = set()
        for product in products:
            categories.add(product.category)
        hotProducts = Product.objects.filter(sellerId=account).order_by('-sell')[:4]
        productId = request.GET['id']
        product = Product.objects.get(id = productId)
        context = {'product': product,'categories':categories,'order':order,'account':account, 'hotProducts':hotProducts}
        return render(request, 'detailShop.html',context)
    else:
        sellerId = request.GET.get('sellerId')
        
        account = Account.objects.get(id = sellerId)
        products = Product.objects.filter(sellerId= account)
        categories = set()
        for product in products:
            categories.add(product.category)
        hotProducts = Product.objects.filter(sellerId=account).order_by('-sell')[:4]
        productId = request.GET['id']
        product = Product.objects.get(id = productId)
        context = {'product': product,'categories':categories,'account':account,'hotProducts':hotProducts}
        return render(request, 'detailShop.html',context)
    
def search(request):
    info = request.GET['search']
    products = Product.objects.filter(name__contains = info)
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        categories = Category.objects.all()
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'order':order}
        return render(request, 'index.html',context)
    else:
        categories = Category.objects.all()
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories}
        return render(request, 'index.html',context)

def searchShop(request):
    info = request.GET['search']
    if request.user.is_authenticated:
        user = request.user.account
        order,created = Order.objects.get_or_create(account = user,status = 0)
        id = request.GET['id']
        account = Account.objects.get(id = id)
        products = Product.objects.filter(sellerId = account,name__contains = info)
        allProducts = Product.objects.filter(sellerId = account)
        categories = set()
        for product in allProducts:
            categories.add(product.category)
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'order':order,'account':account}
        return render(request, 'myshop.html',context)
    else:
        id = request.GET['id']
        account = Account.objects.get(id = id)
        products = Product.objects.filter(sellerId = account,name__contains = info)
        allProducts = Product.objects.filter(sellerId = account)
        categories = set()
        for product in allProducts:
            categories.add(product.category)
        paginator = Paginator(products, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj':page_obj,'categories':categories,'account':account}
        return render(request, 'myshop.html',context)
    
def increase(request):
    if request.user.is_authenticated:
        user = request.user.account
        orderitemid = request.GET['orderitemId']
        order = Order.objects.get(account = user, status = 0)
        orderitem = OrderItem.objects.get(order = order,id = orderitemid)
        orderitem.quantity+=1
        orderitem.save()
        return redirect('cart')
    return redirect('login')

def decrease(request):
    if request.user.is_authenticated:
        user = request.user.account
        orderitemid = request.GET['orderitemId']
        order = Order.objects.get(account = user, status = 0)
        orderitem = OrderItem.objects.get(order = order,id = orderitemid)
        if orderitem.quantity == 1:
            orderitem.delete()
        else:
            orderitem.quantity-=1
            orderitem.save()
        return redirect('cart')
    return redirect('login')