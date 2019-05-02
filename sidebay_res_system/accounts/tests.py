from django.test import TestCase, Client
import unittest
from selenium import webdriver
from django.urls import resolve
from res_system.accounts.views import login
from django.http import HttpRequest
import os
from django.conf import settings

class loginTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome(executable_path=r'C:\Users\senns\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\chromedriver_binary_73ver\chromedriver.exe')

    def tearDown(self):
        self.browser.quit()

    def test_root_urls_resolve_to_login_page_view(self):

        print(os.environ.get('DJANGO_SETTINGS_MODULE'))
        print(os.environ.get('D JANGO_SECRET_KEY'))

        for k, v in os.environ.items():
            print(k, v)
        found = resolve('/')
        print(found)
        self.assertEqual(found.func, login)

    def test_fill_ipout_form(self):
        self.browser.get('http://localhost:8000')

        print(self.browser.__str__())
        self.assertIn('Sidebay予約システム', self.browser.title)
        self.fail('Finish the Test!!')

if __name__ == '__main__':
    unittest.main(warnings='ignore')

