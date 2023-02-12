import os

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.list import ListView
from django.views import View

from payment.services import create_stripe_checkout_session

from .models import Item, Order


class ItemListView(ListView):
    model = Item
    template_name = 'item_list.html'
    context_object_name = 'items'


class BuyItem(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, id=kwargs['id'])
        session_id = create_stripe_checkout_session(item=item)
        return JsonResponse({"session_id": session_id})


class ItemDetailView(View):
    def get(self, request, *args, **kwargs):
        item = get_object_or_404(Item, id=kwargs['id'])
        stripe_key = os.getenv("STRIPE_PUBLIC_KEY")
        return render(request, 'item_detail.html', {'item': item, 'stripe_key' : stripe_key})

class CreateOrderView(View):
    def get(self, request):
        items = Item.objects.all()
        return render(request, 'create_order.html', {'items': items})

    def post(self, request):
        selected_items = request.POST.getlist('items')
        items = Item.objects.filter(id__in=selected_items)
        order = Order.objects.create()
        order.items.set(items)
        order.save()
        return redirect('payment:order_detail', order_id=order.id)

class OrderDetailView(View):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs['id'])
        stripe_key = os.getenv("STRIPE_PUBLIC_KEY")
        return render(request, 'order_detail.html', {'order': order, 'stripe_key': stripe_key})

class BuyOrder(View):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=kwargs['id'])
        session_id = create_stripe_checkout_session(order=order)
        return JsonResponse({"session_id": session_id})
