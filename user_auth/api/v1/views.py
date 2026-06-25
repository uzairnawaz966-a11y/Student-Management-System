from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from user_auth.api.v1.serializers import JWTLoginSerializer, RegisterSerializer, CustomTokenRefreshSerializer, CheckEmailSerializer
from user_auth.services.auth_service import AuthService
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from organization.models import Membership


class RegisterUser(APIView):
    user_service = AuthService()

    def post(self, request):
        serialized_object = RegisterSerializer(data=request.data)

        if serialized_object.is_valid():
            response = self.user_service.create_account(serialized_object.validated_data)
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(serialized_object.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def activate_account(request, token):
    account_activation = AuthService()

    response, status_code = account_activation.activate_account(token=token)
    return Response(response, status=status_code)


class JWTLoginAPIView(APIView):
    auth_service = AuthService()

    def post(self, request):
        serializer = JWTLoginSerializer(data=request.data)

        if serializer.is_valid():

            response, status_code = self.auth_service.login_user(serializer.validated_data)
            return Response(response, status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendActivationLink(APIView):

    auth_service = AuthService()

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        response, status_code = self.auth_service.resend_activation_link(email)
        return Response(response, status=status_code)


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    auth_service = AuthService()

    def post(self, request):
        user = request.user
        password = request.data.get("password")
        new_password = request.data.get("new_password")

        if not password or not new_password:
            return Response(
                {"message": "Both existing password and new password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        response, status_code = self.auth_service.change_account_password(user, password, new_password)
        return Response(response, status=status_code)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class CheckEmailAPIView(APIView):
    """
    Accepts an email address and returns all organizations linked with that email through memberships
    This api is specific for only brand-new users who aren't invited from any organization
    """
    def post(self, request):
        serializer = CheckEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        memberships = Membership.objects.filter(user__email=email).select_related("organization")

        organizations = [
            {
                "id": membership.organization.id,
                "name": membership.organization.name,
                "role": membership.role
            }
            for membership in memberships
        ]

        if bool(organizations):
            return Response(
                {
                    "organization_exists": bool(organizations),
                    "Joined organizations": organizations
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                    "organization_exists": False,
                    "Joined organizations": []
            },
            status=status.HTTP_200_OK
        )