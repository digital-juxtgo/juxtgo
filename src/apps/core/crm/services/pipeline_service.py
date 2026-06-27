"""Write operations for Pipeline."""

import logging
from ..models import Pipeline

logger = logging.getLogger(__name__)


class PipelineService:
    @staticmethod
    def create(data: dict) -> Pipeline:
        pipeline = Pipeline.objects.create(**data)
        logger.info("Pipeline created: %s", pipeline.name)
        return pipeline

    @staticmethod
    def update(pipeline_id: str, data: dict) -> Pipeline:
        pipeline = Pipeline.objects.get(pk=pipeline_id)
        for field, value in data.items():
            setattr(pipeline, field, value)
        pipeline.save()
        logger.info("Pipeline updated: %s", pipeline.name)
        return pipeline

    @staticmethod
    def delete(pipeline_id: str) -> None:
        pipeline = Pipeline.objects.get(pk=pipeline_id)
        pipeline.delete()
        logger.info("Pipeline deleted: %s", pipeline.name)
