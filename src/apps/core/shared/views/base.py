"""
Reusable base view classes for JuxtGo OS.

These views enforce the strict architecture rules:
- Views never import models directly (use string model references where needed).
- List views call selectors to return plain dicts, not ORM objects.
- Create/Update views delegate to services and never touch models.
"""

from collections import defaultdict
from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View


class ResolvableModelMixin:
    """
    Mixin that allows model to be specified as a string 'app_label.ModelName'
    instead of an actual model class.  Views that require a model class can
    use self.get_model_class().
    """

    model = None  # Can be a model class or a string like 'identity.User'

    def get_model_class(self):
        if isinstance(self.model, str):
            return django_apps.get_model(self.model)
        return self.model


class BaseListView(LoginRequiredMixin, View):
    """
    Read‑only list view.
    Subclasses must override `get_data(self, request)` and return a **list of dicts**.
    Pagination is applied automatically if paginate_by is set.
    """

    template_name = None
    paginate_by = 20
    page_title = "List"
    add_url = None
    back_url = None
    context_object_name = "data_list"

    def get(self, request):
        data = self.get_data(request)  # list of dicts
        page_obj = None

        if self.paginate_by:
            paginator = Paginator(data, self.paginate_by)
            page_num = request.GET.get("page", 1)
            try:
                page_obj = paginator.page(page_num)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

        context = {
            self.context_object_name: page_obj if page_obj else data,
            "page_title": self.page_title,
            "add_url": self.add_url,
            "back_url": self.back_url,
            "is_paginated": page_obj is not None,
            "page_obj": page_obj,
        }
        self.add_extra_context(request, context)
        return render(request, self.template_name, context)

    def get_data(self, request):
        """Override to return a list of dicts from a selector."""
        raise NotImplementedError("Subclasses must implement get_data()")

    def add_extra_context(self, request, context):
        """Hook to inject additional data into the template context."""
        pass


class BaseCreateView(LoginRequiredMixin, View):
    template_name = None
    success_url = None
    success_message = "Created successfully."
    back_url = None

    def get(self, request):
        context = {
            "form": defaultdict(str),
            "errors": defaultdict(str),
            "back_url": self.back_url,
        }
        self.add_extra_context(request, context)
        return render(request, self.template_name, context)

    def post(self, request):
        try:
            self.save_object(request)
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        except ValidationError as e:
            errors = e.args[0] if e.args else {}
            context = {
                "form": request.POST,
                "errors": errors,
                "back_url": self.back_url,
            }
            self.add_extra_context(request, context)
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f"Error: {e}")
            context = {
                "form": request.POST,
                "errors": defaultdict(str),
                "back_url": self.back_url,
            }
            self.add_extra_context(request, context)
            return render(request, self.template_name, context)

    def save_object(self, request):
        raise NotImplementedError("Subclass must implement save_object()")

    def add_extra_context(self, request, context):
        pass


class BaseUpdateView(LoginRequiredMixin, ResolvableModelMixin, View):
    """
    Update view.
    `model` can be a model class or a string 'app_label.ModelName'.
    `pk_url_kwarg` is 'pk' by default.
    """

    template_name = None
    success_url = None
    success_message = "Updated successfully."
    back_url = None
    pk_url_kwarg = "pk"

    def get(self, request, **kwargs):
        pk = kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(self.get_model_class(), pk=pk)
        profile = getattr(obj, "profile", None)
        context = {
            "object": obj,
            "profile": profile,
            "form": defaultdict(str),
            "errors": defaultdict(str),
            "back_url": self.back_url,
        }
        self.add_extra_context(request, context)
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        pk = kwargs.get(self.pk_url_kwarg)
        obj = get_object_or_404(self.get_model_class(), pk=pk)
        profile = getattr(obj, "profile", None)
        try:
            self.update_object(request, obj)
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        except ValidationError as e:
            errors = e.args[0] if e.args else {}
            context = {
                "object": obj,
                "profile": profile,
                "form": request.POST,
                "errors": errors,
                "back_url": self.back_url,
            }
            self.add_extra_context(request, context)
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, f"Error: {e}")
            context = {
                "object": obj,
                "profile": profile,
                "form": request.POST,
                "errors": defaultdict(str),
                "back_url": self.back_url,
            }
            self.add_extra_context(request, context)
            return render(request, self.template_name, context)

    def update_object(self, request, obj):
        raise NotImplementedError("Subclass must implement update_object()")

    def add_extra_context(self, request, context):
        """Hook for subclasses to add extra template context."""
        pass
