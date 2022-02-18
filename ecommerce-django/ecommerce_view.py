from django.shortcuts import render, redirect, reverse
from django.utils.html import escape, strip_tags
from django.http import HttpResponse
import json
from .helper import str_convert_single_quotes
from .models import Product, Customer, Order, OrderItem, ShippingAddress, Category, BannerImage
from .forms import CustomerRegistrationForm, CustomerLoginForm


# start page
def home_page(request):
    # get the latest 3 images as limit is [:3]
    bannerImages = BannerImage.objects.all().order_by('-date_added')[:3]
    categories = Category.objects.all()
    category_list_with_product_set = []
    for category in categories:
        category_product_set = category.product_set.get_queryset()
        category_list_with_product_set.append(category_product_set)
    # context variable is used throughout views.py to pass dynamic data to html templates
    context = {
        'categories': categories,
        'images': bannerImages
    }
    return render(request, 'artstore/homepage.html', context)


# store page
def store(request):
    # limit to 100 products
    products = Product.objects.all()[0:100]
    context = {'products': products}
    return render(request, 'artstore/store.html', context)


# product search page
def search_product(request):
    query = request.GET.get('q')
    if query:
        query = escape(strip_tags(query))
        result = Product.objects.filter(name__contains=query)
        if result:
            context = {'products': result, 'query': query}
            return render(request, 'artstore/search.html', context)
        else:
            context = {'producsts': result, 'query': query}
            return render(request, 'artstore/search.html', context)


# cart page
def cart(request):
    context = {}
    return render(request, 'artstore/cart.html', context)


# orders page
def orders(request):
    # get the logged in user from session
    session_customer = request.session.get('customer')
    if session_customer:
        orders_q = Order.objects.filter(customer__pk=session_customer[0])
        if orders_q:
            order_item_list = []
            for order in orders_q:
                # order item
                # get all the items contain in this this order ie. orders_q
                # form order model we can get all the items in orderitem table thanks for foreignkey relationships
                oi = order.orderitem_set.get_queryset()
                # as the name imply order_item_list contains all orderItems of all order
                # for this logged in user
                order_item_list.append(oi)
            context = {'orders': order_item_list}
            return render(request, 'artstore/orders.html', context)
        else:
            context = {}
            return render(request, 'artstore/orders.html', context)
    else:
        return redirect(reverse('artstore:login'))


# checkout page
def checkout(request):
    context = {}
    return render(request, 'artstore/checkout.html', context)


# process checkout page
def process_checkout(request):
    # get request is not allowed
    if request.method == "GET":
        return redirect(reverse('artstore:homepage'))
    if request.method == 'POST':
        # if user is not logged in
        if not request.session.get('customer'):
            context = {
                'msg': 'please login to complete checkout',
                'redirect': request.build_absolute_uri(reverse('artstore:login'))
            }
            return render(request, 'artstore/message.html', context)
        # get cart as string form checkout page
        cartString = request.POST.get('cart')
        # convert the cart string to actual python list
        cart = json.loads(str_convert_single_quotes(cartString))

        # if cart is empty
        if len(cart) < 1:
            context = {
                'msg': 'your cart can not be empty..!',
                'redirect': request.build_absolute_uri(reverse('artstore:store'))
            }
            return render(request, 'artstore/message.html', context)

        # get shipping info form field
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')

        # add order to order table
        # get customer who is making the order
        # this is customer list with customerID and email we need id here
        session_customer = request.session.get('customer')
        customer = Customer.objects.get(pk=session_customer[0])
        # if we get a customer from db for session customer
        if customer:
            # create order here
            order = Order(customer=customer)
            order.save()
            # get the order just created above
            latest_order = Order.objects.latest('id')
            # loop through the whole cart
            for item in cart:
                # get product to put in order item table/model
                product = Product.objects.get(pk=item.get('id'))
                if product:
                    # insert each item/product with quantity to order item table/model
                    orderItem = OrderItem(product=product, order=latest_order, quantity=item.get('quantity'))
                    orderItem.save()
                    # pass
            # insert shipping detail
            shipping = ShippingAddress(customer=customer, order=latest_order, address=address, city=city, state=state, zipcode=zipcode, country=country)
            shipping.save()
            context = {
                'msg': 'your order is successfully processed..!',
                'redirect': request.build_absolute_uri(reverse('artstore:store')),
                'action': 'clearCart'
            }
            return render(request, 'artstore/message.html', context)
    else:
        return HttpResponse('404 Not Found..')


def user_registration(request):
    # go to store if user is logged in
    if request.session.get('customer'):
        # reverse is used to get the actual url for the view "store"
        # we can do so because we have app_name variable in urls.py
        return redirect(reverse('artstore:store'))
    if request.method == 'GET':
        form = CustomerRegistrationForm()
        context = {'form': form}
        return render(request, 'artstore/register.html', context)
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            # check if this email already exist
            q = Customer.objects.filter(email=clean_data['email_field'])
            if q:
                form.add_error('email_field', 'Email already exists')
            else:
                customer = Customer(email=clean_data['email_field'],
                                    password=clean_data['password_field'])
                customer.save()
                context = {
                    'msg': 'you are now registered',
                    'redirect': request.build_absolute_uri(reverse('artstore:login'))
                }
                return render(request, 'artstore/message.html', context)
        context = {'form': form}
        return render(request, 'artstore/register.html', context)


def user_login(request):
    # go to store if user is logged in
    if request.session.get('customer'):
        return redirect(reverse('artstore:store'))
    if request.method == 'GET':
        form = CustomerLoginForm()
        context = {'form': form}
        return render(request, 'artstore/login.html', context)
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            # check for user in database
            customer = Customer.objects.filter(email=clean_data['email_field']).first()
            if customer is not None:
                if customer.email == clean_data['email_field'] and \
                        customer.password == clean_data['password_field']:
                    # customer credentials is ok
                    # add customer to session
                    request.session['customer'] = [customer.id, customer.email]
                    request.session.set_expiry(0)
                    return redirect(reverse('artstore:store'))
                else:
                    form.add_error('email_field', 'invalid user name or password')
            else:
                form.add_error('email_field', 'invalid user name or password')
        context = {'form': form}
        return render(request, 'artstore/login.html', context)


def user_logout(request):
    if request.method == "POST":
        try:
            del request.session['customer']
            request.session.flush()
            return redirect(reverse('artstore:login'))
        except KeyError:
            return redirect(reverse('artstore:store'))
    if request.method == "GET":
        return HttpResponse('404 not found..')




