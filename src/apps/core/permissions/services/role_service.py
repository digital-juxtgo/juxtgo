import logging
from ..models import Role

logger = logging.getLogger(__name__)


class RoleService:
    @classmethod
    def create_role(cls, name, display_name, description=""):
        role, created = Role.objects.get_or_create(
            name=name,
            defaults={"display_name": display_name, "description": description},
        )
        if created:
            logger.info("Role created: %s", role.name)
        else:
            logger.info("Role already exists: %s", role.name)
        return role

    @classmethod
    def update_role(cls, role_id: int, data: dict):
        role = Role.objects.get(pk=role_id)
        role.name = data.get("name", role.name)
        role.display_name = data.get("display_name", role.display_name)
        role.description = data.get("description", role.description)
        role.save()
        if "permissions" in data:
            role.group.permissions.set(data["permissions"])
        logger.info("Role updated: %s", role.name)

    @classmethod
    def delete_role(cls, role_id: int):
        role = Role.objects.get(pk=role_id)
        role.delete()
        logger.info("Role deleted: %s", role.name)
