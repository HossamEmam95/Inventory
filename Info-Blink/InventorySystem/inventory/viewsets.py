from rest_framework import viewsets
from inventory.models import Customer,\
    Category, Products, Invoices, InvoiceDetail , Payments, PaymentDetail
from .serializers import CustomerSerializer, \
    CategorySerializer, ProductsSerializer, InvoiceSerializer,\
    InvoiceDetailsSerializer, PaymentSerializer, PaymentDetailSerialzer


class CustomerView(viewsets.ReadOnlyModelViewSet):
    queryset = Customer.objects
    serializer_class = CustomerSerializer


class CategoryView(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects
    serializer_class = CategorySerializer


class ProductsView(viewsets.ReadOnlyModelViewSet):
    queryset = Products.objects
    serializer_class = ProductsSerializer


class InvoicesView(viewsets.ModelViewSet):
    queryset = Invoices.objects
    serializer_class = InvoiceSerializer


class InvoiceDetailView(viewsets.ReadOnlyModelViewSet):
    queryset = InvoiceDetail.objects
    serializer_class = InvoiceDetailsSerializer


class PaymentView(viewsets.ModelViewSet):
    queryset = Payments.objects
    serializer_class = PaymentSerializer

class PaymentDetailsView(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentDetail.objects
    serializer_class = PaymentDetailSerialzer