from decimal import Decimal
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.shortcuts import render
from .models import Products, Invoices,\
    InvoiceDetail, Payments, Customer, PaymentDetail
from .forms import UpdateProductForm, NewInvoiceForm
from django.core.urlresolvers import reverse_lazy, reverse
from django.forms import modelformset_factory, inlineformset_factory

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


def manage_invoices(request):
    # creating FormSets
    InvoiceFormSet = modelformset_factory(Invoices, exclude=[
        'amount', 'remaining', 'products',
        'status'])
    DetailFromSet = inlineformset_factory(Invoices,
                                          InvoiceDetail,
                                          exclude=['product_price',
                                                   'product_description'],
                                          form=NewInvoiceForm, extra=1)

    # saving the Invoice with it's Products
    if request.method == 'POST':
        invoice_formset = InvoiceFormSet(request.POST, request.FILES,
                                         queryset=Invoices.objects)
        detail_formset = DetailFromSet(request.POST, request.FILES)
        if invoice_formset.is_valid() and detail_formset.is_valid():
            amount = 0
            invoice = invoice_formset.save()
            # loop on the products formsets and assigning
            # the price and description for Products table then caclualte the
            # amount
            for form in detail_formset:
                detail = form.save(commit=False)
                detail.invoice = invoice[0]
                product = Products.objects.get(id=detail.product_id)
                detail.product_price = product.unit_price
                detail.product_description = product.description
                amount += float(detail.product_price * detail.quantity_sold)
                amount *= float(amount * (1 - (product.discount / 100)))
                form.save()
            amount *= Decimal((1 - (invoice[0].discount / 100)))
            invoice[0].amount = amount
            invoice[0].remaining = amount
            invoice_formset.save()

            # updating Customer Balance And Invoice Remaining
            customer = Customer.objects.get(id=invoice[0].customer_id)
            current_invoice = Invoices.objects.get(id=invoice[0].id)
            customer.balance -= current_invoice.amount

            # checking the cridit limit
            if (customer.credit_limit + customer.balance) < 0:
                current_invoice.delete()
                return HttpResponse("Ur invoice exceeds ur credit limit")
            # checking customer max discount
            elif customer.max_discount < current_invoice.discount:
                current_invoice.delete()
                return HttpResponse('u the invoice discount exceed the'
                                    ' allowed cusomter discount')
            # checking agent max discount
            elif current_invoice.agent.max_discount < current_invoice.discount:
                current_invoice.delete()
                return HttpResponse('u the invoice discount exceed '
                                    'the allowed agent discount')
            else:
                customer.save()

    else:
        invoice_formset = InvoiceFormSet(
            queryset=Invoices.objects.filter(invoice_number=0))
        detail_formset = DetailFromSet(
            queryset=InvoiceDetail.objects.filter(invoice=0))

    return render(request, 'inventory/new_invoice.html',
                  {'invoice_form': invoice_formset,
                   'detail_form': detail_formset})


class PaymentsView(View):
    payments = Payments.objects.order_by('date')
    context = {'payments': payments}

    def get(self, request):
        return render(request, 'inventory/payments.html', self.context)


class CreatePayment(CreateView):
    template_name = "inventory/new_payment.html"
    success_url = reverse_lazy('inventory:payments_page')
    model = Payments
    fields = ('payment_number', 'customer', 'agent', 'amount')

    def get_success_url(self):
        return reverse('inventory:transaction', args=(self.object.id,))


def transaction(request, pk):
    payment = Payments.objects.get(id=pk)
    customer = Customer.objects.get(id=payment.customer_id)
    invoices = Invoices.objects.filter(customer=payment.customer_id)
    money = payment.amount
    flag = 0
    if not payment.used:
        for invoice in invoices:
            if money == 0:
                break
            print(invoice.status)
            if invoice.status == 'Closed':
                continue
            if money >= invoice.remaining:
                money -= invoice.remaining
                detail = PaymentDetail(
                    payment=payment,
                    invoice=invoice,
                    amount=invoice.remaining)
                detail.save()
                if flag == 0:
                    customer.balance += invoice.remaining
                    # customer.balance += money
                customer.save()
                invoice.remaining = 0
                invoice.status = 'Closed'
                invoice.save()
                payment.used = True
                payment.save()
                flag = 1
            else:
                invoice.remaining -= money
                detail = PaymentDetail(
                    payment=payment, invoice=invoice, amount=money)
                detail.save()
                print(customer.balance)
                if flag == 0:
                    customer.balance += money
                print(customer.balance)
                customer.save()
                money = 0
                invoice.status = 'Partial'
                invoice.save()
                payment.used = True
                payment.save()

        payment.remaining += money
        payment.save()
    # if payment.used == False:
    #     customer.balance += money
    #     customer.save()
    #     payment.used = True
    #     payment.save()

    payment_details = PaymentDetail.objects.filter(payment=payment)
    context = {'payment': payment,
               'payment_details': payment_details, 'customer': customer}

    return render(request, 'inventory/transaction_status.html', context=context)


# if customer.balance >= current_invoice.amount:
    #     current_invoice.remaining = 0
    #     customer.balance -= current_invoice.amount
    #     current_invoice.status = 'Closed'
    #     customer.save()
    #     current_invoice.save()
    # else:
    #     if customer.balance <= 0:
    #         current_invoice.status = 'Open'
    #         current_invoice.remaining = current_invoice.amount
    #     else:
    #         current_invoice.remaining = current_invoice.amount - customer.balance
    #         current_invoice.status = 'Partial'
    #     customer.balance -= current_invoice.amount
    #     customer.save()
    #     current_invoice.save()
