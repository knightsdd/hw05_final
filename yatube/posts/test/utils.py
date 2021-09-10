from http import HTTPStatus
from typing import Dict, List

from bs4 import BeautifulSoup


def check_urls_templates(self, client, names: Dict):
    for adress, template in names.items():
        with self.subTest(template=template):
            responce = client.get(adress)
            self.assertTemplateUsed(responce, template_name=template)


def check_urls_access(self, client, names: List[str]):
    for adress in names:
        with self.subTest(adress=adress):
            response = client.get(adress)
            self.assertEqual(response.status_code, HTTPStatus.OK)


def chek_unexisting_page(self, client):
    response = client.get('/unexisting_page/')
    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


def chek_paginator(
        self,
        client,
        expected_recs: int,
        adress: str,
        is_page2=False):

    page2 = ''
    if is_page2:
        page2 = '?page=2'

    response = client.get(adress + page2)
    self.assertEqual(len(response.context['page_obj']), expected_recs)


def find_post_by_text(text: str, sourse: str) -> bool:
    """If post's text in page return True."""

    soup = BeautifulSoup(sourse, 'html.parser')
    first_post = soup.main.p.p.text
    return text == first_post
