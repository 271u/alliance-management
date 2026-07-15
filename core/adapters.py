from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class OIDCSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    OIDC is used only to authenticate and provision users.

    Application roles and permissions are managed locally through
    Django groups and must not be changed during OIDC login.
    """

    pass
