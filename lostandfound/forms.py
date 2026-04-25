from django.contrib.auth.forms import UserCreationForm
from .models import User

class Userform(UserCreationForm):
    class Meta:
        model = User
        fields = ('name', 'username', 'email', 'password1', 'password2')

