from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# creates a user url and assigns it to CREATE_USER_URL
CREATE_USER_URL = reverse('user:create')
# creates a token url and assigns it to TOKEN_URL
TOKEN_URL = reverse('user:token')

# create a helper function
def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the users API (public) needs authentication"""
    def setUp(self):
        self.client =  APIClient()
        
    def test_create_valid_user_success(self):
        """test creating user with valid payload is successful"""
        payload = {
            'email':'test@fake.com',
            'password':'testpass',
            'name':'Test name'
        }
        resp = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**resp.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', resp.data)
        
    def test_user_exists(self):
        """Test creating a user that already exits fails"""
        payload = {
            'email':'test@fake.pm',
            'password':'password',
        }
        create_user(**payload)
        
        resp = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_password_too_short(self):
        """Test password is more than 5 characters"""
        payload = {
            'email':'test@fake.pm',
            'password':'pa',
        }
        create_user(**payload)
        
        resp = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists =  get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertTrue(user_exists)
        
    def test_create_token_for_user(self):
        """test that a token is created for the user"""
        payload = {
            'email':'test@fake.pm',
            'password':'password',
        }
        create_user(**payload)
        resp = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
    def test_create_token_invalid_credentials(self):
        """test that token is not created if invalid credentials are given"""
        create_user(email='test@fake.pm', password='password')
        payload = {
            'email':'test@fake.pm',
            'password':'fakepass',
        }
        resp = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_token_no_user(self):
        """Test token creation failure if no user exists"""
        payload = {
            'email':'test@fake.pm',
            'password':'password',
        }
        resp =self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST) 
        
    def test_create_token_missing_field(self):
        """Test that email and password are required to create token"""
        resp = self.client.post(TOKEN_URL, {'email':'one', 'password':''})
        self.assertNotIn('token', resp.data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)         
        
    