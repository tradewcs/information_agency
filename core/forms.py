from django import forms

from .models import Publisher, Topik, NewsPaper


class PublisherForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text="Leave blank to keep current password."
    )

    class Meta:
        model = Publisher
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "years_of_experience",
            "password",
        ]

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        if pwd:
            if len(pwd) < 8:
                raise forms.ValidationError("Password must be at least 8 characters.")
        return pwd


class TopikForm(forms.ModelForm):
    class Meta:
        model = Topik
        fields = ["name"]


class NewsPaperForm(forms.ModelForm):
    class Meta:
        model = NewsPaper
        fields = ["title", "content", "topic"]
        widgets = {"topic": forms.CheckboxSelectMultiple}


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = Publisher
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "years_of_experience",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            return email.lower()
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if not p1 or p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        if len(p2) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()
        return user
