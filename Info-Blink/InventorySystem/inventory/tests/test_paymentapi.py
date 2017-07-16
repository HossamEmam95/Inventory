"""The test cases for the payment API."""

from model_mommy import mommy
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User


from inventory.models import (
    Customer,
    Agent,
    Invoices,
)


class TestingPayments(APITestCase):
    """testing the payment creation and it's effects."""

    def setUp(self):
        self.user = User.objects.create(
            username="admin",
            email="admin@gmail.com",
            password="password123")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

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
        url = '/sales/agentapi/payments/'
        response = self.client.post(url, self.data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['customer'], 1)
        self.assertEquals(float(response.data['amount']), 600.00)

    def test_payment_effect_on_customer_balance(self):
        url = '/sales/agentapi/payments/'
        self.client.post(url, self.data, format='json')
        response = self.client.get('/sales/agentapi/customers/1/')
        self.assertEquals(float(response.data['balance']), -600.00)

    def test_payment_bigger_than_all_invoices(self):
        self.data['amount'] = 4000
        url = '/sales/agentapi/payments/'
        self.client.post(url, self.data, format='json')
        for i in range(1, 3):
            url = '/sales/agentapi/invoices/%s/' % (i + 1)
            response = self.client.get(url)
            self.assertEquals(response.data['status'], "Closed")
            self.assertEquals(float(response.data['remaining']), 0.00)

        url = '/sales/agentapi/payments/1/'
        response = self.client.get(url)
        self.assertEquals(float(response.data['remaining']), 2800.00)

    def test_payment_is_enongh_for_some_invoices(self):
        self.data['amount'] = 500
        url = '/sales/agentapi/payments/'
        self.client.post(url, self.data, format='json')

        response = self.client.get('/sales/agentapi/invoices/1/')
        self.assertEquals(response.data['status'], "Closed")
        self.assertEquals(float(response.data['remaining']), 0.00)

        response = self.client.get('/sales/agentapi/invoices/2/')
        self.assertEquals(response.data['status'], "Partial")
        self.assertEquals(float(response.data['remaining']), 300.00)

        response = self.client.get('/sales/agentapi/invoices/3/')
        self.assertEquals(response.data['status'], "Open")
        self.assertEquals(float(response.data['remaining']), 400.00)

        url = '/sales/agentapi/payments/1/'
        response = self.client.get(url)
        self.assertEquals(float(response.data['remaining']), 0.00)

    def test_payment_only_goes_for_assigned_customer_invoices(self):
        self.data['amount'] = 500000
        url = '/sales/agentapi/payments/'
        response = self.client.post(url, self.data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get('/sales/agentapi/invoices/4/')
        self.assertEquals(response.data['customer'], 2)
        self.assertEquals(response.data['status'], "Open")
        self.assertEquals(float(response.data['remaining']), 400.00)

    def test_payment_create_payment_detail(self):
        self.data['amount'] = 500
        url = '/sales/agentapi/payments/'
        self.client.post(url, self.data, format='json')

        response = self.client.get('/sales/agentapi/paymentdetail/1/')
        self.assertEquals(response.data['payment'], 1)
        self.assertEquals(response.data['invoice'], 1)
        self.assertEquals(float(response.data['amount']), 400.00)

        response = self.client.get('/sales/agentapi/paymentdetail/2/')
        self.assertEquals(response.data['payment'], 1)
        self.assertEquals(response.data['invoice'], 2)
        self.assertEquals(float(response.data['amount']), 100.00)

        response = self.client.get('/sales/agentapi/paymentdetail/3/')
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
