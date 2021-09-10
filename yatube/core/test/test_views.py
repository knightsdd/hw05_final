from django.test import Client, TestCase


class TemplateErrorsViewTest(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.guest_client = Client()

    def test_404_template(self):
        template_name = 'core/404.html'
        unexist_page = '/unexist_page/'
        response = self.guest_client.get(unexist_page)
        self.assertTemplateUsed(response, template_name=template_name)
