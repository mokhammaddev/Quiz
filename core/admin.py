from django.contrib import admin
from .models import Question, Category, Option, Quizz


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_date']
    list_display_links = ['id', 'title']


class OptionInLineModel(admin.TabularInline):
    model = Option
    readonly_fields = ('id',)

    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'category', 'level']
    list_display_links = ['id', 'question', 'category']
    inlines = [OptionInLineModel]
    list_filter = ['category', 'level']


@admin.register(Quizz)
class QuizzAdmin(admin.ModelAdmin):
    list_display = ['id', 'score', 'category', 'account']
    list_display_links = ['id', 'score', 'category', 'account']


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_true', 'question']
    list_display_links = ['id', 'title']
    list_filter = ['is_true', 'question']



