# messaging_app/chats/auth.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[self.user_id_field]
            return User.objects.get(**{self.user_id_field: user_id})
        except User.DoesNotExist:
            return None