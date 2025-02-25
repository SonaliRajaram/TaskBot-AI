import unittest
from flask_testing import TestCase
from main import app, extract_name, is_valid_email, extract_email, is_valid_phone, extract_phone, correct_service_name, correct_intent

class Testapp(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_extract_name(self):
        self.assertEqual(extract_name("My name is John Doe"), "John Doe")
        self.assertEqual(extract_name("I am Jane Doe"), "Jane Doe")
        self.assertEqual(extract_name("Hello, my name is Alice"), "Alice")
        self.assertEqual(extract_name("No name here"), "No name here")

    def test_is_valid_email(self):
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertFalse(is_valid_email("invalid-email"))
        self.assertFalse(is_valid_email("test@.com"))

    def test_extract_email(self):
        self.assertEqual(extract_email("My email is test@example.com"), "test@example.com")
        self.assertEqual(extract_email("Contact me at user@doapp.com"), "user@doapp.com")
        self.assertIsNone(extract_email("No email here"))

    def test_is_valid_phone(self):
        self.assertTrue(is_valid_phone("1234567890"))
        self.assertFalse(is_valid_phone("12345"))
        self.assertFalse(is_valid_phone("12345678901"))

    def test_extract_phone(self):
        self.assertEqual(extract_phone("My phone number is 1234567890"), "1234567890")
        self.assertEqual(extract_phone("Call me at 0987654321"), "0987654321")
        self.assertIsNone(extract_phone("No phone number here"))

    def test_correct_intent(self):
        self.assertEqual(correct_intent("I need a service"), "service")
        self.assertEqual(correct_intent("I want to cancel"), "cancel")
        self.assertEqual(correct_intent("What are your working hours?"), "working_hours")
        self.assertIsNone(correct_intent("unknown intent"))

    def test_chat_endpoint(self):
        response = self.client.post('/chat', json={"session_id": "test_session", "message": "hi"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello! How can I assist you today?", response.json['response'])

        response = self.client.post('/chat', json={"session_id": "test_session", "message": "I need a service"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("We offer the following services", response.json['response'])

if __name__ == '__main__':
    unittest.main()