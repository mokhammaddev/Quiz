from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from account.serializers import MyProfileSerializer
from .models import Question, Category, Option, Quizz, Contact


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'title', 'is_true']


class OptionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['option']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'category', 'question', 'options', 'level']


class QuestionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'category', 'question']


class ResultSerializer(serializers.ModelSerializer):
    # questions = QuestionSerializer(read_only=True)
    # options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Quizz
        fields = ['id', 'account', 'category', 'questions', 'score']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'message']


