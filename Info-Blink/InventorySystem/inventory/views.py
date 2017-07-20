from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.shortcuts import render
from .models import Products, Invoices,\
    Payments, Customer, PaymentDetail
from .forms import UpdateProductForm, InvoiceForm, DetailFormset, \
    CashPaymentForm
from django.core.urlresolvers import reverse_lazy, reverse


class ProductView(View):
    products = Products.objects.order_by('name')
    context = {'products': products}

    def get(self, request):
        return render(request, 'inventory/products_page.html', self.context)


class ProductDetail(DetailView):
    model = Products
    template_name = "inventory/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        return context


class CreateProduct(CreateView):
    template_name = "inventory/new_product.html"
    success_url = reverse_lazy('inventory:products_page')
    model = Products
    fields = ('barcode', 'product_code', 'name', 'description', 'category',
              'quantity_in_stock', 'quantity_on_hold',
              'expire_date', 'unit_price',
              'vendor', 'manufacturer', 'discount')


class UpdateProduct(UpdateView):
    form_class = UpdateProductForm
    template_name = "inventory/update_product.html"
    success_url = reverse_lazy('inventory:products_page')
    model = Products


class InvoicesView(View):
    invoices = Invoices.objects.order_by('date')
    context = {'invoices': invoices}

    def get(self, request):
        return render(request, 'inventory/invoices.html', self.context)


class InvoiceDetailView(DetailView):
    model = Invoices
    template_name = 'inventory/invoice_detail.html'


def create_invoice(request):
    '''
    This function is used to crate the invoices, it create the form then the
    fomsets, calcutlate the amount and check if this amount is bigger than the
    credit    limit after the invoice ceation it update the customer balance
    and the product in stock.'''

    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, request.FILES)
        detail_formset = DetailFormset(request.POST, request.FILES)

        if invoice_form.is_valid() and detail_formset.is_valid():
            amount = 0
            invoice = invoice_form.save(commit=False)
            for form in detail_formset:
                detail = form.save(commit=False)
                product = Products.objects.get(id=detail.product_id)
                amount += Decimal(product.unit_price * detail.quantity_sold)\
                          * (1 - (product.discount / 100))
            amount *= Decimal((1 - (invoice.discount / 100)))

            if invoice_form.valid_amount(invoice, amount):
                invoice.amount = amount
                invoice.remaining = amount
                invoice = invoice_form.save()

                for form in detail_formset:
                    detail = form.save(commit=False)
                    detail.invoice = invoice
                    product = Products.objects.get(id=detail.product_id)
                    detail.product_price = product.unit_price
                    detail.product_description = product.description
                    amount += (Decimal(detail.product_price) * detail.quantity_sold) * \
                              (1 - (product.discount / 100))
                    form.save()

                    product.quantity_in_stock -= detail.quantity_sold
                    product.save()

                # updating Customer Balance
                customer = Customer.objects.get(id=invoice.customer_id)
                current_invoice = Invoices.objects.get(id=invoice.id)
                customer.balance -= current_invoice.amount
                customer.save()
                if invoice.type == 'Credit':
                    return HttpResponseRedirect(reverse('inventory:invoices_page'))
                else:
                    return HttpResponseRedirect(reverse('inventory:cash_payment', args=(invoice.id,)))

    else:
        invoice_form = InvoiceForm()
        detail_formset = DetailFormset()

    return render(request, 'inventory/new_invoice.html',
                  {'invoice_form': invoice_form,
                   'detail_form': detail_formset})


class PaymentsView(View):
    payments = Payments.objects.order_by('date')
    context = {'payments': payments}

    def get(self, request):
        return render(request, 'inventory/payments.html', self.context)


class CreateCreditPayment(CreateView):
    """ Payment creation takes place here then
    send the id to transation function"""

    template_name = "inventory/new_payment.html"
    success_url = reverse_lazy('inventory:payments_page')
    model = Payments
    fields = ('payment_number', 'customer', 'agent', 'amount')

    def get_success_url(self):
        return reverse('inventory:transaction', args=(self.object.id,))


def transaction(request, pk):
    """
    after payment creation the payment id is sent here where it get all the
    customer invoices and loop on them. pay the partial and open invoices
    by date then return the remainig of the payment if found and
    update the customer balance and the invoices status
    """

    payment = Payments.objects.get(id=pk)
    customer = Customer.objects.get(id=payment.customer_id)
    invoices = Invoices.objects.filter(customer=payment.customer_id)
    money = payment.amount
    if not payment.used:
        for invoice in invoices:
            if money == 0:
                break
            if invoice.status == "Closed":
                continue
            if money >= invoice.remaining:
                money -= invoice.remaining
                payment_detail = PaymentDetail.objects.create(
                    payment=payment,
                    invoice=invoice,
                    amount=invoice.remaining
                )
                payment_detail.save()
                customer.balance += invoice.remaining
                customer.save()

                invoice.remaining = 0
                invoice.status = "Closed"
                invoice.save()

                payment.used = True
                payment.save()

            else:
                invoice.remaining -= money
                payment_detail = PaymentDetail.objects.create(
                    payment=payment,
                    invoice=invoice,
                    amount=money
                )
                payment_detail.save()

                customer.balance += money
                customer.save()

                invoice.status = "Partial"
                invoice.save()

                money = 0

                payment.used = True
                payment.save()

        payment.remaining += money
        payment.save()

    payment_details = PaymentDetail.objects.filter(payment=payment)
    context = {'payment': payment,
               'payment_details': payment_details, 'customer': customer}

    return render(request, 'inventory/transaction_status.html', context=context)


def cash_payment(request, pk):
    invoice = Invoices.objects.get(id=pk)

    if request.method == 'POST':
        payment_form = CashPaymentForm(invoice=invoice, data=request.POST)

        if payment_form.is_valid():
            customer = Customer.objects.get(id=invoice.customer_id)
            payment = payment_form.save(commit=False)

            payment.customer = customer
            payment.agent = invoice.agent
            payment.save()

            payment_detail = PaymentDetail.objects.create(
                payment=payment,
                invoice=invoice,
                amount=invoice.remaining
            )
            payment_detail.save()
            customer.balance += invoice.remaining
            customer.save()
            payment.remaining = payment.amount - invoice.remaining
            payment.save()
            invoice.remaining = 0
            invoice.status = "Closed"
            invoice.save()

            return HttpResponseRedirect(reverse(
                'inventory:cash_transaction',
                args=(payment_detail.id,)))

    else:
        payment_form = CashPaymentForm(invoice=invoice)

    return render(request, 'inventory/cash_payment.html',
                  {'payment_form': payment_form})


def cash_transaction(request, pk):
    print('here1')
    payment_detail = PaymentDetail.objects.filter(id=pk)
    payment = Payments.objects.get(id=payment_detail[0].payment_id)
    customer = Customer.objects.get(id=payment.customer_id)

    context = {'payment': payment,
               'payment_details': payment_detail, 'customer': customer}

    return render(request, 'inventory/transaction_status.html',
                  context=context)

