from typing import List, Dict, Optional
from ..models import Role


class RoleSelector:
    @staticmethod
    def list_roles() -> List[Dict]:
        roles = Role.objects.all().order_by("name")
        return [
            {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "created_at": role.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for role in roles
        ]

    @staticmethod
    def get_role_detail(role_id: int) -> Optional[Dict]:
        try:
            role = Role.objects.get(pk=role_id)
            return {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "permissions": list(
                    role.group.permissions.values_list("id", flat=True)
                ),
                "created_at": role.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Role.DoesNotExist:
            return None
