from decimal import Decimal
from rest_framework import serializers
from inventory.models import Customer, Agent, Category, \
    Products, Invoices, InvoiceDetail, Payments, PaymentDetail


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('name', 'phone', 'email', 'credit_limit',
                  'grace_period', 'balance', 'max_discount')


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = ('name', 'email', 'phone', 'max_discount',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('type',)


class ProductsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Products
        fields = ('id', 'barcode', 'product_code', 'name', 'description',
                  'category', 'quantity_in_stock', 'quantity_on_hold',
                  'expire_date', 'vendor', 'manufacturer', 'discount')


class InvoiceDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvoiceDetail
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    product_data = serializers.DictField(write_only=True)

    class Meta:
        model = Invoices
        fields = ('id', 'invoice_number', 'customer', 'agent',
                  'date', 'invoice_due_date', 'amount', 'discount',
                          'status', 'type', 'remaining', 'product_data')

    def validate(self, data):
        customer = Customer.objects.get(id=data['customer'].id)
        agent = Agent.objects.get(id=data['agent'].id)
        product_data = data['product_data']
        invoice = super(InvoiceSerializer, self).validate(data)

        if invoice['discount'] > customer.max_discount:
            raise serializers.ValidationError(
                "The discount is above the customer limit")

        if invoice['discount'] > agent.max_discount:
            raise serializers.ValidationError(
                "The discount is above the agent limit")

        for key, value in product_data.items():
            product = Products.objects.get(id=key)
            if value > product.quantity_in_stock:
                raise serializers.ValidationError(
                    "There isn't a sufficient %ss stock for this order" % (product.name))

        return data

    def create(self, validated_data):
        product_data = validated_data.pop('product_data')
        invoice = super(InvoiceSerializer, self).create(validated_data)
        amount = 0
        for key, value in product_data.items():
            product = Products.objects.get(id=key)
            invoice_detail = InvoiceDetail.objects.create(
                invoice=invoice,
                product=product,
                product_description=product.description,
                product_price=product.unit_price,
                quantity_sold=value)
            invoice_detail.save()

            product.quantity_in_stock -= value
            product.save()

            amount += Decimal(invoice_detail.product_price) *\
                Decimal(invoice_detail.quantity_sold) * \
                (1 - (product.discount / 100))

        amount *= Decimal(1 - (invoice.discount / 100))
        invoice.amount = amount
        invoice.remaining = amount
        invoice.save()

        customer = validated_data.pop('customer')
        customer.balance -= invoice.amount
        customer.save()
        return invoice


class PaymentSerializer(serializers.ModelSerializer):
    data = serializers.DateTimeField(read_only=True)
    remaining = serializers.DecimalField(max_digits=9, decimal_places=2,
                                         read_only=True)
    used = serializers.BooleanField(read_only=True)

    class Meta:
        model = Payments
        fields = ('payment_number', 'customer', 'agent', 'data',
                  'amount', 'remaining', 'used')

    def create(self, validated_data):
        money = Decimal(validated_data['amount'])
        payment = super(PaymentSerializer, self).create(validated_data)
        customer = validated_data['customer']
        invoices = Invoices.objects.filter(customer=customer)

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
        return payment


class PaymentDetailSerialzer(serializers.ModelSerializer):

    class Meta:
        model = PaymentDetail
        fields =  ('payment', 'invoice', 'amount')
