from django.db import models

# Create your models here.
Status = [('Open', 'Open'), ('Closed', 'Closed'), ('Partial', 'Partial')]
Type = [('Cash', 'Cash'), ('Credit', 'Credit')]


class Customer(models.Model):
    name = models.CharField(max_length=70)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    credit_limit = models.IntegerField()
    grace_period = models.IntegerField()
    balance = models.IntegerField()
    max_discount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return self.name


class Agent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=70)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20)
    max_discount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return self.name


class Category(models.Model):
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.type


class Products(models.Model):
    barcode = models.CharField(max_length=200)
    product_code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category)
    quantity_in_stock = models.IntegerField()
    quantity_on_hold = models.IntegerField()
    expire_date = models.DateTimeField()
    unit_price = models.DecimalField(max_digits=9, decimal_places=2)
    vendor = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return self.name


class Invoices(models.Model):
    invoice_number = models.CharField(max_length=100, primary_key=True)
    customer = models.ForeignKey(Customer)
    agent = models.ForeignKey(Agent)
    date = models.DateTimeField(auto_now_add=True)
    invoice_due_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    discount = models.IntegerField()
    status = models.CharField(max_length=100, choices=Status)
    type = models.CharField(max_length=100, choices=Type)
    remaining = models.DecimalField(max_digits=9, decimal_places=2)

    def __str__(self):
        return self.invoice_number

class Payments(models.Model):
    payment_number = models.CharField(max_length=100, primary_key=True, default='1')
    customer = models.ForeignKey(Customer)
    agent = models.ForeignKey(Agent)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_number



class InvoiceDetail(models.Model):
    invoice = models.ForeignKey(Invoices)
    product = models.ForeignKey(Products)
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity_sold = models.DecimalField(max_digits=9, decimal_places=3)


class PaymentDetail(models.Model):
    payment = models.ForeignKey(Payments)
    invoice = models.ForeignKey(Invoices)
