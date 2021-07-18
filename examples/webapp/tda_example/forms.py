from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import TDAUser


class TDAUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = TDAUser
        fields = UserCreationForm.Meta.fields


class TDAUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = TDAUser
        fields = UserChangeForm.Meta.fields
