from django import forms

from .models import Topik, NewsPaper


class TopikForm(forms.ModelForm):
    class Meta:
        model = Topik
        fields = ["name"]


class NewsPaperForm(forms.ModelForm):
    class Meta:
        model = NewsPaper
        fields = ["title", "content", "topic"]
        widgets = {"topic": forms.CheckboxSelectMultiple}
