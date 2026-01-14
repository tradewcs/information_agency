from django.test import TestCase
from django.forms.widgets import CheckboxSelectMultiple

from core.models import Topik
from core.forms import TopikForm, NewsPaperForm


class TopikFormTests(TestCase):
    def test_valid_data(self):
        form = TopikForm(data={"name": "Health"})
        self.assertTrue(form.is_valid())
        topik = form.save()
        self.assertEqual(topik.name, "Health")

    def test_duplicate_name_invalid(self):
        Topik.objects.create(name="Health")
        form = TopikForm(data={"name": "Health"})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class NewsPaperFormTests(TestCase):
    def setUp(self):
        self.topic = Topik.objects.create(name="Sports")

    def test_widget_is_checkboxselectmultiple(self):
        form = NewsPaperForm()
        self.assertIsInstance(form.fields["topic"].widget, CheckboxSelectMultiple)

    def test_valid_data_and_save(self):
        form = NewsPaperForm(
            data={
                "title": "T",
                "content": "C",
                "topic": [self.topic.pk],
            }
        )
        self.assertTrue(form.is_valid())
        np = form.save()
        self.assertIn(self.topic, np.topic.all())
