from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Role
from .selectors import RoleSelector
from .services import RoleService

User = get_user_model()


class RoleModelTests(TestCase):
    def test_role_creation_auto_group(self):
        role = Role.objects.create(name="editor", display_name="Editor")
        self.assertIsNotNone(role.group)
        self.assertEqual(role.group.name, "editor")

    def test_save_does_not_duplicate_group(self):
        r1 = Role.objects.create(name="admin", display_name="Admin")
        r2 = Role.objects.create(name="admin", display_name="Admin")
        self.assertEqual(r1.group, r2.group)


class RoleSelectorTests(TestCase):
    def setUp(self):
        Role.objects.create(name="admin", display_name="Admin")
        Role.objects.create(name="manager", display_name="Manager")

    def test_list_roles_returns_dicts(self):
        roles = RoleSelector.list_roles()
        self.assertEqual(len(roles), 2)
        self.assertIn("name", roles[0])
        self.assertIn("display_name", roles[0])


class RoleServiceTests(TestCase):
    def test_create_role(self):
        role = RoleService.create_role("tester", "Tester", "Test description")
        self.assertEqual(role.name, "tester")
        self.assertTrue(Role.objects.filter(name="tester").exists())

    def test_create_duplicate_does_not_raise(self):
        RoleService.create_role("dup", "Duplicate")
        RoleService.create_role("dup", "Duplicate")  # should not raise
        self.assertEqual(Role.objects.filter(name="dup").count(), 1)

    def test_delete_role(self):
        role = Role.objects.create(name="temp", display_name="Temp")
        RoleService.delete_role(role.id)
        self.assertFalse(Role.objects.filter(name="temp").exists())
