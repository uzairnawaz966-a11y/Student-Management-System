from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from rest_framework_simplejwt.tokens import RefreshToken
from organization.models import Membership, OrganizationJoinLink
from user_auth.models import SocialOnboardingToken
from user_auth.services.auth_service import AuthService
from organization.services.organization_service import OrganizationService

User = get_user_model()


class GoogleAuthService:

    @staticmethod
    def google_login(credential, invite_token=None):

        try:
            google_user = id_token.verify_oauth2_token(
                credential,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
            )

        except Exception as e:
            print("=" * 50)
            print(e)
            print("=" * 50)
            return {
                "message": "Invalid Google Token"
            }, 400

        email = google_user["email"]

        first_name = google_user.get("given_name", "")
        last_name = google_user.get("family_name", "")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            },
        )

        if invite_token:

            try:
                join_link = OrganizationJoinLink.objects.get(
                    token=invite_token
                )
            except OrganizationJoinLink.DoesNotExist:
                return {
                    "message": "Invalid invite link"
                }, 404

            if not join_link.is_valid:
                return {
                    "message": "Invite link expired"
                }, 400

            if email not in join_link.allowed_emails:
                return {
                    "message": "Email is not authorized for this invite"
                }, 403

            membership = AuthService().accept_invite(
                join_link=join_link,
                user=user,
            )

            refresh = RefreshToken.for_user(user)

            refresh["organization_id"] = membership.organization_id
            refresh["role"] = membership.role

            return {
                "message": "Joined organization successfully",

                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },

                "organization": {
                    "id": membership.organization.id,
                    "name": membership.organization.name,
                },

                "role": membership.role,
            }, 200

        memberships = Membership.objects.filter(
            user=user,
            is_active=True,
        ).select_related("organization")

        organizations = [
            {
                "id": membership.organization.id,
                "name": membership.organization.name,
                "role": membership.role,
            }
            for membership in memberships
        ]

        if organizations:

            return {
                "message": "Google Login Successful",

                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },

                "organizations": organizations,

                "next_step": "select_organization",
            }, 200

        onboarding_token, _ = SocialOnboardingToken.objects.update_or_create(
            user=user,
            defaults={
                "expires_at": timezone.now() + timedelta(minutes=15)
            }
        )

        return {
            "message": "Google Login Successful",

            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },

            "next_step": "create_organization",

            "onboarding_token": str(onboarding_token.token),

        }, 200
    

    @staticmethod
    def create_organization(validated_data):

        onboarding_token = validated_data["onboarding_token"]

        try:
            token = SocialOnboardingToken.objects.select_related("user").get(
                token=onboarding_token
            )
        except SocialOnboardingToken.DoesNotExist:
            return {
                "message": "Invalid onboarding token"
            }, 404

        if token.is_expired:
            token.delete()

            return {
                "message": "Onboarding token expired"
            }, 400

        user = token.user

        organization_data = {
            "name": validated_data["name"],
            "description": validated_data["description"],
        }

        organization, membership = OrganizationService.create_organization(
            user=user,
            validated_data=organization_data,
        )

        AuthService().create_profile(membership)

        token.delete()

        refresh = RefreshToken.for_user(user)

        refresh["organization_id"] = membership.organization_id
        refresh["role"] = membership.role

        return {
            "message": "Organization created successfully",

            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },

            "organization": {
                "id": organization.id,
                "name": organization.name,
            },

            "membership": {
                "role": membership.role,
            },

            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }

        }, 201