from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer 

TAGS_URL = reverse('recipe:tag-list') 

class PublicTagsApiTests(TestCase):
    """Test the publicly available tags api"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        resp = self.client.get(TAGS_URL)
        
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateTagsApiTests(TestCase):
    """Test the authorized tags api"""
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@fake.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        
    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        
        self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        
        resp = self.client.get(TAGS_URL)
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)
        
    def test_tags_limited_to_usesr(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'testest@fake.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        
        resp = self.client.get(TAGS_URL)
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], tag.name) 
        