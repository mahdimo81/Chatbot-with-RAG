from django.db import transaction
from django.http import QueryDict
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer


from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

class UserCreateAPIView(APIView):

    def post(self, request):
        try:
            # Check for empty request body
            if not request.data:
                return Response(
                    {"detail": "The request body is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate request data format
            if not isinstance(request.data, QueryDict) or not isinstance(
                request.data, dict
            ):
                return Response(
                    {
                        "detail": "Invalid request format. Request body must be a (multipart/form-data) or json of field: data pairs."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convert QueryDict to dict if needed
            if isinstance(request.data, QueryDict):
                user_data = request.data.dict()  # Convert to regular dict
            else:
                user_data = request.data  # Keep as dict

            try:
                with transaction.atomic():  # Start db transaction
                    # Create user
                    user_serializer = CustomUserSerializer(data=user_data)
                    user_serializer.is_valid(raise_exception=True)
                    user = user_serializer.save()

                # Return success response
                return Response(
                    {
                        "message": "User has been registered successfully.",
                        "user": user_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except ValidationError as e:  # Handle validation errors
                return Response(
                    {"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer  # Use the custom serializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can log out

    def post(self, request):  # Handle logout request
        try:
            if not request.data:
                return Response(
                    {"detail": "The request body is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                refresh_token = request.data[
                    "refresh_token"
                ]  # Get refresh token from request
                token = RefreshToken(refresh_token)  # Create token object
                token.blacklist()  # Blacklist the refresh token

                # Update user token_invalidated
                user = request.user
                user.token_invalidated = True  # Invalidate authentication token
                user.save()  # Save changes to the database

                return Response(
                    {
                        "message": "Refresh token has been blacklisted. Delete access token from front-end app."
                    },
                    status=status.HTTP_205_RESET_CONTENT,
                )
            
            except Exception as e:  # Handle possible errors
                return Response(
                    {"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST
                )  # Return bad request response
            
        except Exception as e:

            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class UserUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Requires authentication

    def put(self, request, user_id=None, *args, **kwargs):  # Handle PUT requests
        try:
            # Validate request body exists
            if not request.data:
                return Response(
                    {"detail": "The request body is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate request format
            if not isinstance(request.data, QueryDict) or not isinstance(
                request.data, dict
            ):
                return Response(
                    {
                        "detail": "Invalid request format. The request body must be a (multipart/form-data) or json of field: data pairs."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convert QueryDict to dict if needed
            if isinstance(request.data, QueryDict):
                user_data = request.data.dict()
            else:
                user_data = request.data

            user = request.user  # Get current user

            # Remove unchanged fields from update data
            if "username" in user_data and user_data["username"] == user.username:
                del user_data["username"]

            # Initialize serializers for validation
            user_serializer = CustomUserSerializer(user, data=user_data, partial=True)
            user_valid = user_serializer.is_valid()  # Validate user data

            if user_valid:

                # Save updates
                user_serializer.save()

                return Response(  # Return success response
                    {
                        "message": "User information has been updated successfully.",
                        "user": user_serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:  # Return validation errors if any
                errors = {
                    "detail": user_serializer.errors,
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:

            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
