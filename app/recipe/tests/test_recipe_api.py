from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from core.models import Tag
from core.models import Ingredient

from recipe.serializers import RecipeSerializer
from recipe.serializers import RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

# /api/recipe/recipes
# /api/recipe/recipes/<id>


def detail_url(recipe_id):
    """Need to create
    url that can take argument.
    Will return detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main Course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """ Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required"""
        resp = self.client.get(RECIPES_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated access to recipe api"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'fake@fake.com',
            'fake'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        resp = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for specified user"""
        user2 = get_user_model().objects.create_user(
            'fake2@fake.com',
            'fake2'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        resp = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data, serializer.data)

    def test_viewing_recipe_detail(self):
        """Test viewing a sample recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        resp = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(resp.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a basic recipe"""
        payload = {
            'title': 'Vegan Chocolate Cheesecake',
            'time_minutes': 55,
            'price': 10.00,
        }
        resp = self.client.post(RECIPES_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Carmel Chocolate Mousse',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 75,
            'price': 20.00
        }
        resp = self.client.post(RECIPES_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name="Sherry")
        ingredient2 = sample_ingredient(user=self.user, name="Yellow Onion")
        ingredient3 = sample_ingredient(user=self.user, name="Jalepeno")
        payload = {
            'title': 'Onion Jalepeno Jam',
            'ingredients': [ingredient1.id, ingredient2.id, ingredient3.id],
            'time_minutes': 60,
            'price': 35.00
        }
        resp = self.client.post(RECIPES_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 3)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        self.assertIn(ingredient3, ingredients)

    def test_create_recipe_with_tags_and_ingredients(self):
        """Test creating a recipe with all available attributes"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dinner')
        ingredient1 = sample_ingredient(user=self.user, name="Beyond Braut")
        ingredient2 = sample_ingredient(user=self.user, name="Leeks")
        ingredient3 = sample_ingredient(user=self.user, name="Garlic")
        payload = {
            'title': 'Braut Tartare',
            'tags': [tag1.id, tag2.id],
            'ingredients': [ingredient1.id, ingredient2.id, ingredient3.id],
            'time_minutes': 30,
            'price': 15.00
        }
        resp = self.client.post(RECIPES_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=resp.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 3)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        self.assertIn(ingredient3, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        # patch is used to update the fields in the payload
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {
            'title': 'My Curry',
            'tags': [new_tag.id],
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        # put will replace an object we are updating with a full object
        # that is provided in the request
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Carbonara',
            'time_minutes': 5,
            'price': 1.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)
