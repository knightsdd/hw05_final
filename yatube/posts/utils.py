from django.core.paginator import Paginator


def make_paginator(objects, request, per_page):
    paginator = Paginator(objects, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
