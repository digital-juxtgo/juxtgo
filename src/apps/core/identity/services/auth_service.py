from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class AuthService:
    @classmethod
    def authenticate_user(cls, email: str, password: str):
        return authenticate(username=email.lower().strip(), password=password)

    @classmethod
    def generate_tokens(cls, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)

    @classmethod
    def blacklist_token(cls, refresh_token: str):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            return False