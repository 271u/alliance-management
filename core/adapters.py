# core/adapters.py

from django.conf import settings
from django.http import HttpResponseForbidden

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class OIDCGroupSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Maps OIDC groups to Django access.

    Desired behavior:

    OIDC group              Django effect
    ------------------------------------------------
    271u-management         can login
    271u-superuser          can login + staff + superuser
    other users             no access
    """

    def _get_claim_value(self, data: dict, claim_name: str):
        """
        Supports simple claims like:
            groups

        And nested claims like:
            realm_access.roles
        """
        value = data

        for part in claim_name.split("."):
            if not isinstance(value, dict):
                return None

            value = value.get(part)

            if value is None:
                return None

        return value

    def _normalize_groups(self, raw_groups) -> set[str]:
        if raw_groups is None:
            return set()

        if isinstance(raw_groups, str):
            raw_groups = [raw_groups]

        return {
            str(group).strip().lstrip("/")
            for group in raw_groups
            if str(group).strip()
        }

    def _get_oidc_groups(self, sociallogin) -> set[str]:
        extra_data = sociallogin.account.extra_data or {}
        claim_name = getattr(settings, "OIDC_GROUPS_CLAIM", "groups")

        possible_sources = [
            extra_data,
            extra_data.get("userinfo", {}),
            extra_data.get("id_token", {}),
        ]

        for source in possible_sources:
            raw_groups = self._get_claim_value(source, claim_name)
            groups = self._normalize_groups(raw_groups)

            if groups:
                return groups

        return set()

    def _sync_django_flags(self, user, oidc_groups: set[str]) -> None:
        superuser_groups = getattr(settings, "OIDC_SUPERUSER_GROUPS", set())

        is_superuser = bool(oidc_groups & superuser_groups)

        user.is_staff = is_superuser
        user.is_superuser = is_superuser
        user.is_active = True

    def pre_social_login(self, request, sociallogin):
        oidc_groups = self._get_oidc_groups(sociallogin)

        user_groups = getattr(settings, "OIDC_USER_GROUPS", set())
        superuser_groups = getattr(settings, "OIDC_SUPERUSER_GROUPS", set())

        allowed_groups = user_groups | superuser_groups

        print("OIDC extra_data:", sociallogin.account.extra_data)
        print("OIDC groups:", oidc_groups)
        print("Allowed groups:", allowed_groups)

        if not oidc_groups & allowed_groups:
            raise ImmediateHttpResponse(
                HttpResponseForbidden(
                    "Access denied. Your OIDC account is not in an allowed group."
                )
            )

        self._sync_django_flags(sociallogin.user, oidc_groups)

        if sociallogin.user.pk:
            sociallogin.user.save(
                update_fields=[
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ]
            )
