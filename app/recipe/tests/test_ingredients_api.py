from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicInredientsApiTests(TestCase):
    """Suite of tests for public access to the ingredient api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test unauthorized access denied to this api"""

        resp = self.client.get(INGREDIENTS_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Suite of tests for private access to the ingredient api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@fake.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieval of ingredients list"""
        Ingredient.objects.create(user=self.user, name='Flour')
        Ingredient.objects.create(user=self.user, name='Salt')

        resp = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test ingredients retrieved specific to the user are retrieved"""
        user2 = get_user_model().objects.create_user(
            'test2@fake.com',
            'password2'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Garlic')

        resp = self.client.get(INGREDIENTS_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""
        payload = {'name': 'Cabbage'}
        self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'name': ''}
        resp = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Apples'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Cinnamon'
        )
        recipe = Recipe.objects.create(
            title='Apple Pie',
            time_minutes=5.00,
            price=2.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        resp = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, resp.data)
        self.assertNotIn(serializer2.data, resp.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Eggs'
        )
        Ingredient.objects.create(user=self.user, name='Jalapenos')
        recipe1 = Recipe.objects.create(
            title='Breakfast Burrito',
            time_minutes=20.00,
            price=5.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Huevos Rancheros',
            time_minutes=7.00,
            price=3.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        resp = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(resp.data), 1)
