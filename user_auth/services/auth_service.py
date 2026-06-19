import logging
from django.db import transaction
from user_auth.models import AccountActivationToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from organization.models import Membership
from user_auth.clients.email_client import EmailClient
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from user_auth.models import (
    Owner,
    Admin,
    Instructor,
    Student
)

User = get_user_model()

class AuthService:

    def activate_account(self, token):
        activation_token = get_object_or_404(AccountActivationToken, token=token)

        if activation_token.is_expired:
            return {
                "message": "Expired links cannot be used to activate account"
            }, 400

        with transaction.atomic():
            user = activation_token.user
            user.is_active = True
            user.save()

            activation_token.mark_as_used()

            return {
                "message": "Account activated successfully. You can now login"
            }, 200
    

    def login_user(self, validated_data):
        user = validated_data['user']
        organization_id = validated_data["organization_id"]

        membership = Membership.objects.filter(
            user=user,
            organization_id=organization_id,
            is_active=True
        ).first()

        if not membership:
            return {"message": "Invalid organization"}, 400

        refresh = RefreshToken.for_user(user)

        refresh["organization_id"] = membership.organization_id
        refresh["role"] = membership.role

        return {
                "message": "Login Successful",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                },
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            }, 200


    def create_profile(self, membership):
        if membership.is_owner:
            profile, _ = Owner.objects.get_or_create(membership=membership)
        elif membership.is_admin:
            profile, _ = Admin.objects.get_or_create(membership=membership)
        elif membership.is_instructor:
            profile, _ = Instructor.objects.get_or_create(membership=membership)
        elif membership.is_student:
            profile, _ = Student.objects.get_or_create(membership=membership)
        else:
            raise ValueError("Invalid role")
        return profile


    def create_membership(self, user, organization_id, role):
        membership = Membership.objects.create(
            user=user,
            organization_id=organization_id,
            role=role,
            is_active=False
        )

        self.create_profile(membership)
        return membership


    def create_account(self, validated_data):
        """
        Creates an Inactive user account in the database
        Automatically generates a one time activation link which expires after 24 hours
        Calls the email client to send links to users' gmails
        """

        validated_data.pop('password_confirmation', None)

        organization_id = validated_data.pop("organization_id", None)
        role = validated_data.pop("role", None)

        with transaction.atomic():

            user = User.objects.create_user(
                **validated_data,
                is_active=False
            )

            if organization_id is not None and role is not None:
                self.create_membership(
                    user=user,
                    organization_id=organization_id,
                    role=role
                )

            expiry_date = timezone.now() + timedelta(hours=24)
            activation_token = AccountActivationToken.objects.create(
                user=user,
                expiration_date=expiry_date,
            )

        activation_link = f"{settings.ORGANIZATION_BASE_URL}api/activate-user/{activation_token.token}/"

        email_client = EmailClient()
        try:
            email = user.email
            email_client.send_verification_email(email, activation_link)
        except Exception as e:
            logging.error(f"Account created but Failed to send activation link to {email}, Exception cause: {str(e)}")
            return {"message": "Account created but Failed to send activation link"}, 201

        return {
                "message": "User Registered Successfully, Check your Gmail for Account Activation link",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
            }


    def resend_activation_link(self, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {"message": "User Does not exist"}, 404

        if user.is_active:
            return {"message": "Account already activated"}, 400

        expiry_date = timezone.now() + timedelta(hours=24)

        token_object, created = AccountActivationToken.objects.get_or_create(
            user=user,
            defaults={
                "expiration_date": expiry_date
            }
        )

        if not created and token_object.is_expired:
            token_object.delete()
            token_object = AccountActivationToken.objects.create(
            user=user,
            expiration_date=expiry_date
        )

        activation_link = f"{settings.ORGANIZATION_BASE_URL}api/activate-user/{token_object.token}"

        email_client = EmailClient()

        try:
            email_client.send_verification_email(email, activation_link)
        except Exception as e:
            logging.error(f"Failed to resend activation link to {email}, Exception cause: {str(e)}")
            return {"message": "User created but failed to send activation link"}, 201
        
        return {"message": "Activation Link sent successfully. Check your email"}, 200


    def change_account_password(self, user, password, new_password):
        if not user.check_password(password):
            return {"message": "Invalid current password"}, 400
        
        user.set_password(new_password)
        user.save()

        return {"message": "Password Changed successfully"}, 200