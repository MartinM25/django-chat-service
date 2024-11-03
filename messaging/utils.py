import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

def decode_jwt(token):
    try:
        # Decode the token using the SECRET_KEY and ALGORITHM from settings
        decoded = jwt.decode(token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        return decoded
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")
