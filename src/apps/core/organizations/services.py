import logging
from django.db import transaction
from apps.core.permissions.models import Role
from apps.core.shared.utils import generate_unique_slug
from .models import Organization, OrganizationMembership, OrganizationInvitation

logger = logging.getLogger(__name__)


class OrganizationService:
    @staticmethod
    def create_organization(name: str, creator_user) -> Organization:
        slug = generate_unique_slug(Organization, name)
        with transaction.atomic():
            org = Organization.objects.create(name=name, slug=slug)
            owner_role, _ = Role.objects.get_or_create(
                name="owner",
                defaults={"display_name": "Owner"},
            )
            OrganizationMembership.objects.create(
                user=creator_user,
                organization=org,
                role=owner_role,
            )
        logger.info("Organisation %s created by %s", name, creator_user.email)
        return org

    @staticmethod
    def update_organization(org_id: str, name: str) -> Organization:
        org = Organization.objects.get(pk=org_id)
        org.name = name
        org.slug = generate_unique_slug(Organization, name, instance=org)
        org.save()
        logger.info("Organisation %s updated", org.name)
        return org

    @staticmethod
    def delete_organization(org_id: str) -> None:
        org = Organization.objects.get(pk=org_id)
        org.delete()
        logger.info("Organisation %s deleted", org.name)

    @staticmethod
    def invite_user(org_id: str, email: str, invited_by) -> OrganizationInvitation:
        org = Organization.objects.get(pk=org_id)
        invitation = OrganizationInvitation.objects.create(
            organization=org,
            email=email,
            invited_by=invited_by,
        )
        logger.info("Invitation sent to %s for organisation %s", email, org.name)
        return invitation

    @staticmethod
    def accept_invitation(token: str, user) -> None:
        invitation = OrganizationInvitation.objects.get(token=token)
        if invitation.accepted:
            raise ValueError("Invitation already accepted")
        member_role, _ = Role.objects.get_or_create(
            name="member",
            defaults={"display_name": "Member"},
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=invitation.organization,
            role=member_role,
        )
        invitation.accepted = True
        invitation.save()
        logger.info(
            "User %s accepted invitation to %s",
            user.email,
            invitation.organization.name,
        )

    @staticmethod
    def switch_organization(user, org_id: str) -> Organization:
        org = Organization.objects.get(pk=org_id)
        if not OrganizationMembership.objects.filter(
            user=user, organization=org
        ).exists():
            raise ValueError("You are not a member of this organization.")
        return org
