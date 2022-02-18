"""
    this file is part of ecommerce application in django framework
    this is the models file which define the database tabels of application
    and is not workable standalone
    only for demonstration puposes
"""

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


# each model corresponds to a table in database
# for banner area only 3 images are supported as can be seen in home_page in views.py
class BannerImage(models.Model):
    image = models.ImageField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.image}"


# customer registration model
class Customer(models.Model):
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.email}"


# product category model
class Category(models.Model):
    # we don't need id field as django gives us that by default
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    # just so the plural name of category model is appropriately in admin area
    # without this django will add just an 's' ie categorys which is stupid
    class Meta:
        verbose_name_plural = 'Categories'


# product model
# each product belong to a category
# as in category field the type is Foreignkey which means product is related to category
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    image = models.ImageField()
    # if you delete the category all products related to that will be deleted
    # here model.CASCADE just do that
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # this is used to print string representation of an model object
    # whenever we print product its name will be printed instead of some object
    def __str__(self):
        return self.name


# order model
# contain the action order
# this order can have many items just like a category can have many products
# it have also relation to customer as customer can place order only
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order_date = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)


# Order Item model
# represent a single item and its quantity
# related to product and order with foreignkey
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now=True)


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=200)
    country = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


# these are called signals in django
# can think of as javascript events
# here whenever an object is deleted from database post_delete signal is fired
# then we make sure to delete the image when image field is deleted
# as django will not delete the image but only the imagepath
# so this is to make sure the image is also deleted after its field is deleted

# https://stackoverflow.com/questions/16041232/django-delete-filefield
# Whenever ANY model is deleted, if it has a file field on it, delete the associated file too
@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    print(sender, instance)
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            instance_file_field = getattr(instance, field.name)
            delete_file_if_unused(sender, instance, field, instance_file_field)


# Delete the file if something else get uploaded in its place
@receiver(pre_save)
def delete_files_when_file_changed(sender, instance, **kwargs):
    # Don't run on initial save
    if not instance.pk:
        return
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            # its got a file field. Let's see if it changed
            try:
                instance_in_db = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                # We are probably in a transaction and the PK is just temporary
                # Don't worry about deleting attachments if they aren't actually saved yet.
                return
            instance_in_db_file_field = getattr(instance_in_db, field.name)
            instance_file_field = getattr(instance, field.name)
            if instance_in_db_file_field.name != instance_file_field.name:
                delete_file_if_unused(sender, instance, field, instance_in_db_file_field)


# Only delete the file if no other instances of that model are using it
def delete_file_if_unused(model, instance, field, instance_file_field):
    dynamic_field = {field.name: instance_file_field.name}
    print(dynamic_field)
    # https://stackoverflow.com/questions/310732/in-django-how-does-one-filter-a-queryset-with-dynamic-field-lookups
    other_refs_exist = model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist:
        instance_file_field.delete(False)

