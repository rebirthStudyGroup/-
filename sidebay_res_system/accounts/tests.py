from django.test import TestCase
from selenium import webdriver
import unittest
from django.urls import resolve
from .views import login
from django.http import HttpRequest


class loginTest(unittest.TestCase):
    def setUp(self):
        self.blowser = webdriver.Chrome()

    def tearDown(self):
        self.blowser.quit()

    def root_urls_resolve_to_login_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, login)


    def fill_ipout_form(self):
        self.blowser.get('http://localhost:8000')

        self.assertIn('Sidebay予約システム', self.blowser.title)
        self.fail('Finish the Test!!')

if __name__ == '__main__':
    unittest.main(warnings='ignore')

