from model_mommy import mommy
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

from inventory.models import *


class PaymentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="admin",
            email="admin@gmail.com",
            password="password123")

        self.client = Client()

        self.Customer = mommy.make(
            Customer,
            _quantity=2,
            balance=-1200,
            credit_limit=5000,
            max_discount=10)

        self.Agent = mommy.make(
            Agent,
            max_discount=7)

        self.invoices = mommy.make(
            Invoices,
            customer=Customer.objects.get(id=1),
            amount=400,
            remaining=400,
            status="Open",
            _quantity=3
        )

        self.invoices = mommy.make(
            Invoices,
            customer=Customer.objects.get(id=2),
            amount=400,
            remaining=400,
            status="Open",
        )

        self.data = {
            "payment_number": 123,
            "customer": 1,
            "agent": 1,
            "amount": 600,
            "date": "2017-02-05T00:00:00Z",
        }

        self.client.login(username='admin', password='123456')

    def test_payment_creation(self):
        response = self.client.post('/sales/newpayment/', self.data)
        self.assertEquals(response.status_code, 302)
        payment = self.client.get('/sales/transaction/1/')
        self.assertEquals(payment.context['payment'].amount, 600)

    def test_payment_bigger_than_all_invoices(self):
        self.data['amount'] = 4000
        url = '/sales/newpayment/'
        self.client.post(url, self.data)
        payment = self.client.get('/sales/transaction/1/')

        for payment_detail in payment.context['payment_details']:
            self.assertEquals(payment_detail.invoice.status, 'Closed')
            self.assertEquals(payment_detail.invoice.remaining, 0.00)
        url = '/sales/transaction/1/'
        response = self.client.get(url)
        self.assertEquals(float(response.context['payment'].remaining), 2800.00)

    def test_payment_is_enongh_for_some_invoices(self):

        self.data['amount'] = 500
        url = '/sales/newpayment/'
        self.client.post(url, self.data)
        payment = self.client.get('/sales/transaction/1/')
        payment_details = payment.context['payment_details']

        self.assertEquals(payment_details.count(), 2)

        self.assertEquals(payment_details[0].invoice.status, 'Closed')
        self.assertEquals(payment_details[0].invoice.remaining, 0.00)

        self.assertEquals(payment_details[1].invoice.status, 'Partial')
        self.assertEquals(payment_details[1].invoice.remaining, 300.00)

    def test_large_payment_effect_on_customer_balance(self):
        self.data['amount'] = 5000
        url = '/sales/newpayment/'
        self.client.post(url, self.data)
        payment = self.client.get('/sales/transaction/1/')
        customer = payment.context['customer']

        self.assertEquals(customer.balance, 0.00)

    def test_small_payment_effect_on_customer_balance(self):
        self.data['amount'] = 500
        url = '/sales/newpayment/'
        self.client.post(url, self.data)
        payment = self.client.get('/sales/transaction/1/')
        customer = payment.context['customer']

        self.assertEquals(customer.balance, -700.00)
