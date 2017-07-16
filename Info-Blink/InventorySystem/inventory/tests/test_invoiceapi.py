"""Invoice Api TestCases."""

from model_mommy import mommy
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User


from inventory.models import (
    Products,
    Customer,
    Agent,
)


class EstimatedInvoiceAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='admin',
            email='admin@gmail.com.com',
            password='123456',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.Customer = mommy.make(
            Customer,
            balance=0,
            credit_limit=500,
            max_discount=10)

        self.Agent = mommy.make(
            Agent,
            max_discount=7)

        self.Product = mommy.make(
            Products,
            name='Car',
            discount=10,
            unit_price=200,
            quantity_in_stock=10
        )

        self.Product = mommy.make(
            Products,
            discount=10,
            unit_price=100,
            quantity_in_stock=6
        )

        self.data = {
            "invoice_number": "5",
            "customer": 1,
            "agent": 1,
            "invoice_due_date": "2017-02-05T00:00:00Z",
            "discount": 5,
            "type": "Credit",
            "product_data": {"1": 2, "2": 3}
        }

        self.client.login(username='admin', password='123456')

        self.cost = 598.5
        self.balance = - 598.5

    def test_calc_invoice_amount_and_remaining(self):
        url = '/sales/agentapi/invoices/'
        response = self.client.post(url, self.data, format='json')
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(float(response.data['amount']), self.cost)
        self.assertEquals(float(response.data['remaining']), self.cost)

    def test_customer_balance_update(self):
        url = '/sales/agentapi/invoices/'
        self.client.post(url, self.data, format='json')
        response = self.client.get('/sales/agentapi/customers/1/')
        self.assertEquals(float(response.data['balance']), self.balance)

    def test_discount_limit_of_customer(self):
        self.data['discount'] = 15
        url = '/sales/agentapi/invoices/'
        response = self.client.post(url, self.data, format='json')
        self.assertNotEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['non_field_errors'], [
                          "The discount is above the customer limit"])

    def test_discount_limit_of_agent(self):
        self.data['discount'] = 8
        url = '/sales/agentapi/invoices/'
        response = self.client.post(url, self.data, format='json')
        self.assertNotEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(response.data['non_field_errors'], [
                          "The discount is above the agent limit"])

    def test_product_update_after_invoice(self):
        url = '/sales/agentapi/invoices/'
        self.client.post(url, self.data, format='json')

        response = self.client.get('/sales/agentapi/products/1/')
        self.assertEquals(response.data['quantity_in_stock'], 8)

        response = self.client.get('/sales/agentapi/products/2/')
        self.assertEquals(response.data['quantity_in_stock'], 3)

    def test_products_in_stock_validation(self):
        self.data['product_data'] = {"1": 11, "2": 3}
        url = '/sales/agentapi/invoices/'

        response = self.client.post(url, self.data, format='json')
        self.assertEquals(response.data['non_field_errors'],
                          ["There isn't a sufficient Cars stock for this order"])
