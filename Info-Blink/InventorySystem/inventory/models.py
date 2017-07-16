"""Inventory System DataBase Models."""
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
Status = [('Open', 'Open'), ('Closed', 'Closed'), ('Partial', 'Partial')]
Type = [('Cash', 'Cash'), ('Credit', 'Credit')]


class Customer(models.Model):
    """Customer Creation Class."""

    user = models.OneToOneField(
        User,
        related_name='customer',
        on_delete=models.CASCADE,
        null=True)
    name = models.CharField(max_length=70)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    credit_limit = models.IntegerField()
    grace_period = models.IntegerField()
    balance = models.DecimalField(max_digits=9, decimal_places=2)
    max_discount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        """The readable name of this class."""
        return self.name


class Agent(models.Model):
    """Agent creation Class."""

    user = models.OneToOneField(
        User,
        related_name='agent',
        on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=70)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20)
    max_discount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        """The readable name of this class."""
        return self.name


class Category(models.Model):
    """Category Creation Class."""

    type = models.CharField(max_length=100)

    def __str__(self):
        """The readable name of this class."""
        return self.type


class Products(models.Model):
    """Product Creation Class."""

    barcode = models.CharField(max_length=200)
    product_code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category)
    quantity_in_stock = models.IntegerField()
    quantity_on_hold = models.IntegerField()
    expire_date = models.DateField()
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    vendor = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        """The readable name of this class."""
        return str(self.name + " " + str(self.unit_price)) + "$"


class Invoices(models.Model):
    """The Invoice Creation Class."""

    invoice_number = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer)
    agent = models.ForeignKey(Agent)
    date = models.DateTimeField(auto_now_add=True)
    invoice_due_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    discount = models.IntegerField()
    status = models.CharField(max_length=100, choices=Status, default='Open')
    type = models.CharField(max_length=100, choices=Type)
    remaining = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    products = models.ManyToManyField('Products', through='InvoiceDetail')

    def __str__(self):
        """The readable name of this class."""
        return self.invoice_number


class InvoiceDetail(models.Model):
    """
    the Invoice Detail class the the model that merge the many to many relation
    between the Invoice and the Product .. a detail is formed for every product
    """

    invoice = models.ForeignKey(Invoices, related_name='parent_invoice')
    product = models.ForeignKey(Products, related_name='parent_product')
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_sold = models.IntegerField()


class Payments(models.Model):
    """The payment Creation class."""

    payment_number = models.CharField(max_length=100, default='1')
    customer = models.ForeignKey(Customer)
    agent = models.ForeignKey(Agent)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    remaining = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        """The readable name of this class."""
        return self.payment_number


class PaymentDetail(models.Model):
    '''
    the Payment Detail class the the model that merge the many to many relation
    between the Invoice and the Payment .. a detail is formed for every payment
    '''
    payment = models.ForeignKey(Payments)
    invoice = models.ForeignKey(Invoices)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
