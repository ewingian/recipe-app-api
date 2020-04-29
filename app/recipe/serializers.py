from rest_framework import serializers

from core.models import Tag
from core.models import Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""
    
    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)
        
class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""
    
    class Meta:
        model = Ingredient
        fields = ('name', 'user')
        read_only_fields = ('id',)