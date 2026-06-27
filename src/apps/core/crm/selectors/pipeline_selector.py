"""Read‑only queries for the Pipeline model."""

from typing import List, Dict, Optional
from ..models import Pipeline


class PipelineSelector:
    @staticmethod
    def list_all() -> List[Dict]:
        pipelines = Pipeline.objects.all()
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "stages": p.stages,
                "is_active": p.is_active,
            }
            for p in pipelines
        ]

    @staticmethod
    def get_detail(pipeline_id: str) -> Optional[Dict]:
        try:
            p = Pipeline.objects.get(pk=pipeline_id)
            return {
                "id": str(p.id),
                "name": p.name,
                "stages": p.stages,
                "is_active": p.is_active,
            }
        except Pipeline.DoesNotExist:
            return None
