from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.forms import modelform_factory

User = get_user_model()


def style_form(form):
    """Barcha maydonlarga dashboard CSS klasslarini beradi."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs["class"] = "check"
        elif isinstance(widget, forms.ClearableFileInput):
            widget.attrs["class"] = "file"
        else:
            widget.attrs["class"] = "input"
        if isinstance(widget, forms.DateInput):
            widget.input_type = "date"
            widget.format = "%Y-%m-%d"
    return form


def make_form(model, fields, *args, **kwargs):
    return style_form(modelform_factory(model, fields=fields)(*args, **kwargs))


class AdminCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=10)
    role = forms.ChoiceField(choices=[(r, l) for r, l in User.Role.choices if 1 <= r <= 4])

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = int(self.cleaned_data["role"])
        if commit:
            user.save()
        return user


class RankForm(forms.Form):
    role = forms.TypedChoiceField(coerce=int, choices=[(r, l) for r, l in User.Role.choices if r <= 4])
