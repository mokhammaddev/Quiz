from django.db import models, IntegrityError
from django.db.models import Avg, Q, UniqueConstraint


class TimeStamp(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# Subjects
class Category(TimeStamp):
    title = models.CharField(max_length=218)

    # `created_date` already exists here because of `TimeStamp`

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'


# Questions
class Question(TimeStamp):
    # `created_date` already exists here because of `TimeStamp`
    LEVEL = (
        (0, 'Easy'),
        (1, 'Medium'),
        (2, 'Hard'),
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Category', db_index=True)
    question = models.CharField(max_length=218)
    level = models.IntegerField(choices=LEVEL)

    @classmethod
    def filter_new_questions(cls, account):
        old_questions = Quizz.objects.filter(account=account).values('questions')
        new_questions = cls.objects.exclude(id__in=old_questions)
        return new_questions

    def __str__(self):
        return self.question


# Answers
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question', db_index=True, related_name='option')
    title = models.CharField(max_length=218, verbose_name='answer')
    is_true = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['question'],
                condition=Q(is_true=True),
                name='unique_correct_option'
            )
        ]

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except:
            raise IntegrityError('Only one option can be marked as correct for a question.')


class Quizz(TimeStamp):  # by_student
    """ collections of questions """
    # `created_date` already exists here because of `TimeStamp`
    account = models.ForeignKey('account.Account', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)
    # result = models.DecimalField(decimal_places=2, max_digits=5)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.account} - {self.score} in {self.category}"

    @classmethod
    def calculate_average_result_category(cls, category):
        average_result = cls.objects.filter(category=category).aggregate(Avg('score'))['score__avg']
        return average_result

    @classmethod
    def calculate_average_result_account(cls, account):
        average_result = cls.objects.filter(account=account).aggregate(Avg('score'))['score__avg']
        return average_result


class Contact(models.Model):
    name = models.CharField(max_length=218)
    email = models.EmailField(unique=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.email}, {self.name}"
