from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from apps.core.shared.views.base import BaseListView, BaseCreateView, BaseUpdateView
from ..selectors import PipelineSelector
from ..services import PipelineService


class PipelineListView(BaseListView):
    template_name = "crm/pipeline/list.html"
    context_object_name = "pipelines"
    page_title = "Sales Pipelines"
    add_url = reverse_lazy("core:crm:pipeline_create")

    def get_data(self, request):
        return PipelineSelector.list_all()


class PipelineCreateView(BaseCreateView):
    template_name = "crm/pipeline/form.html"
    success_url = reverse_lazy("core:crm:pipeline_list")
    page_title = "Create Pipeline"
    back_url = reverse_lazy("core:crm:pipeline_list")

    def save_object(self, request):
        name = request.POST.get("name", "")
        stages_str = request.POST.get("stages", "")
        stages = [s.strip() for s in stages_str.split(",") if s.strip()]
        if not name:
            raise ValueError("Pipeline name is required.")
        PipelineService.create({"name": name, "stages": stages})


class PipelineUpdateView(BaseUpdateView):
    model = "crm.Pipeline"
    template_name = "crm/pipeline/form.html"
    success_url = reverse_lazy("core:crm:pipeline_list")
    page_title = "Edit Pipeline"
    back_url = reverse_lazy("core:crm:pipeline_list")

    def update_object(self, request, obj):
        data = {
            "name": request.POST.get("name", ""),
            "stages": [
                s.strip()
                for s in request.POST.get("stages", "").split(",")
                if s.strip()
            ],
        }
        PipelineService.update(str(obj.pk), data)


class PipelineDeleteView(View):
    template_name = "crm/confirm_delete.html"
    success_url = reverse_lazy("core:crm:pipeline_list")

    def get(self, request, pk):
        pipeline = PipelineSelector.get_detail(pk)
        if not pipeline:
            messages.error(request, "Pipeline not found.")
            return redirect(self.success_url)
        return render(
            request,
            self.template_name,
            {"object": pipeline, "back_url": self.success_url},
        )

    def post(self, request, pk):
        try:
            PipelineService.delete(pk)
            messages.success(request, "Pipeline deleted.")
        except Exception as e:
            messages.error(request, str(e))
        return redirect(self.success_url)
