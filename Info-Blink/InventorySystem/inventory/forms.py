from decimal import Decimal
from django.http import HttpResponse

from django import forms
from .models import Products, Invoices, InvoiceDetail, Customer, Agent, Payments
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory, inlineformset_factory


class UpdateProductForm(forms.ModelForm):

    class Meta:
        model = Products
        fields = ('description', 'category',
                  'quantity_in_stock', 'expire_date', 'unit_price',
                  'vendor', 'manufacturer', 'discount')


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoices
        exclude = ['amount', 'remaining', 'products', 'status']


    def valid_amount(self, invoice,  amount):
        customer = invoice.customer

        if amount > customer.credit_limit:
            msg = 'The invoice Amount is above %s credit limit' %\
                  (customer.name,)
            self.add_error('customer', forms.ValidationError(msg))

        else:
            return True

    def clean(self):
        if any(self.errors):
            return

        invoice = super(InvoiceForm, self).clean()
        customer = invoice['customer']
        agent = invoice['agent']

        if invoice['discount'] > customer.max_discount:
            raise forms.ValidationError("the discount is above customer max discount limit")

        if invoice['discount'] > agent.max_discount:
            raise forms.ValidationError("the discount is above agent max discount limit")


class BaseDetailFormSet(forms.BaseInlineFormSet):

    def clean(self):
        super(BaseDetailFormSet, self).clean()
        if any(self.errors):
            return self.errors

        for form in self.forms:
            product = form.cleaned_data['product']
            if form.cleaned_data['quantity_sold'] > product.quantity_in_stock:
                raise forms.ValidationError('not enough products')


class CashPaymentForm(forms.ModelForm):
    class Meta:
        model = Payments
        fields = ('payment_number', 'amount')

    def __init__(self, invoice, *args, **kwargs):

        self.invoice = invoice
        super(CashPaymentForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(CashPaymentForm, self).clean()

        amount = self.cleaned_data['amount']
        if amount < self.invoice.amount:
            msg = 'The payment isn\'t enough to pay this invoice'
            raise forms.ValidationError(msg)

DetailFormset = inlineformset_factory(Invoices,
                                      InvoiceDetail,
                                      fields=('product', 'quantity_sold'),
                                      formset=BaseDetailFormSet,
                                      extra=1)

