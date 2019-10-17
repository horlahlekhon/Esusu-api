from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class BasicAuthenticationBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username__iexact=username)
            if user.check_password(password):
                print("chhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhpassword:{}, validateion".format(password), user.check_password(password))
                return user
            else:
                return None
        except user_model.DoesNotExist:
            return None
