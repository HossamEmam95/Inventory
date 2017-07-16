from django.conf.urls import url, include
from . import views, viewsets

from rest_framework.routers import DefaultRouter
from .views import ProductView, InvoicesView,\
    PaymentsView, CreateProduct, UpdateProduct,\
    ProductDetail, InvoiceDetailView, CreatePayment


router = DefaultRouter()
router.register(r'customers', viewsets.CustomerView)
router.register(r'categories', viewsets.CategoryView)
router.register(r'products', viewsets.ProductsView)
router.register(r'invoices', viewsets.InvoicesView,)
router.register(r'invoicedetail', viewsets.InvoiceDetailView)
router.register(r'payments', viewsets.PaymentView)
router.register(r'paymentdetail', viewsets.PaymentDetailsView)


urlpatterns = [

    url(r'^agentapi/', include(router.urls), name='invoices'),
    url(r'^$', ProductView.as_view(), name="products_page"),
    url(r'invoices', InvoicesView.as_view(), name="invoices_page"),
    url(r'payments', PaymentsView.as_view(), name="payments_page"),
    url(r'newproduct/$', CreateProduct.as_view(), name='new_product'),
    url(r'updateproduct/(?P<pk>[0-9]+)/$',
        UpdateProduct.as_view(), name='product_update'),
    url(r'products/(?P<pk>[0-9]+)/$',
        ProductDetail.as_view(), name='product_detail'),
    url(r'invoice/(?P<pk>[0-9]+)/$',
        InvoiceDetailView.as_view(), name='invoice_detail'),
    url(r'newinvoice/$', views.manage_invoices, name='new_invoice'),
    url(r'newpayment/$', CreatePayment.as_view(), name='new_payment'),
    url(r'transaction/(?P<pk>[0-9]+)/$',
        views.transaction, name='transaction'),


]
