from rest_framework import serializers
from .models import Professor, Module, Rating
from django.contrib.auth.models import User

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    professors = ProfessorSerializer(many=True)  # Nested serialization

    class Meta:
        model = Module
        fields = '__all__'

# Rating Serializer
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

# Register Serializer 
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Password not be readable
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)  # Hash password
        return user
