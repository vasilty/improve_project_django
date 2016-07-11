from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from operator import attrgetter
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone

from . import models
from . import forms


def menu_list(request):
    today = timezone.now().date()
    menus = models.Menu.objects.prefetch_related('items').filter(
        expiration_date__gte=today).order_by('expiration_date')
    return render(request, 'menu/list_all_current_menus.html', {
        'menus': menus})


def menu_detail(request, pk):
    menu = models.Menu.objects.get(pk=pk)
    return render(request, 'menu/menu_detail.html', {'menu': menu})


def item_detail(request, pk):
    try: 
        item = models.Item.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404
    return render(request, 'menu/detail_item.html', {'item': item})


def menu_create_edit(request, pk=0):
    try:
        menu = models.Menu.objects.get(pk=pk)
    except models.Menu.DoesNotExist:
        menu = None
    form = forms.MenuForm(instance=menu)

    if request.method == 'POST':
        form = forms.MenuForm(instance=menu, data=request.POST)
        if form.is_valid():
            if menu:
                for item in menu.items.all():
                    item.items.remove(menu)
                form.save()
            else:
                menu = form.save()
            for item in menu.items.all():
                item.items.add(menu)
            return HttpResponseRedirect(
                reverse('menu:detail', kwargs={'pk': menu.pk}))
    return render(request, 'menu/menu_edit.html', {'form': form})
