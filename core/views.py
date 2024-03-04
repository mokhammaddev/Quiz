from operator import attrgetter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.utils import timezone
from account.models import Account
from account.serializers import AccountSerializer
from .models import Option, Category, Quizz, Question, Contact
from .serializers import (CategorySerializer, QuestionSerializer, ResultSerializer,
                          ContactSerializer, QuestionResultSerializer)


class CategoryListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/api/quizz/category
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class QuestionListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/api/quizz/category/{category_id}/questions/
    serializer_class = QuestionSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        qs = Question.objects.filter(category_id=category_id).order_by('?')[:5]
        return qs

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     category_id = self.kwargs.get('category_id')
    #     if qs:
    #         qs = qs.filter(category_id=category_id)
    #         return qs
    #     return HttpResponseNotFound('Not Found!')


class ResultListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/api/quizz/quizz-result

    queryset = Quizz.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = sorted(qs, key=attrgetter('score'), reverse=True)
        return qs


class ResultCreateAPIView(APIView):
    # http://127.0.0.1:8000/api/quizz/quizz-create

    # permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID of the category.'
                ),
                'questions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question_id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID of the question.'
                            ),
                            'answers_id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='ID of the answer.'
                            ),
                        }
                    )
                )
            },
            required=['category_id', 'questions'],
            example={
                "category_id": 1,
                "questions": [
                    {
                        "question_id": 1,
                        "option_id": 1
                    },
                    {
                        "question_id": 2,
                        "option_id": 1
                    },
                    {
                        "question_id": 3,
                        "option_id": 1
                    },
                    {
                        "question_id": 7,
                        "option_id": 1
                    }
                ]
            }
        )
    )
    def post(self, request):
        count = 0
        statistic = []
        account = self.request.user
        category_id = self.request.data.get('category_id')
        questions = self.request.data.get('questions')  # potion_ids also included
        print(questions)
        unique_question_ids = set()
        unique_option_ids = set()
        unique_questions = []

        for item in questions:
            question_id = item['question_id']
            option_id = item['option_id']

            if question_id in unique_question_ids:
                return Response({"message": "unique question_id required. Don't input duplicates!"})
            if option_id in unique_option_ids:
                return Response({"message": "unique option_id required. Don't input duplicates!"})
            if Option.objects.filter(id=option_id, question_id__in=unique_question_ids).exists():
                return Response({"message": "Option ID belongs to another question!"})

            unique_question_ids.add(question_id)
            unique_option_ids.add(option_id)
            unique_questions.append(item)

        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response("Category not found")
        score = Quizz.objects.create(account_id=account.id, category_id=category_id)

        j = 0
        for i in unique_questions:
            question_id = int(i.get('question_id'))
            option_id = int(i.get('option_id'))
            try:
                question = Question.objects.get(id=question_id)
                option = Option.objects.get(id=option_id)
            except Exception as e:
                raise ValidationError(e.args)
            statistic.append({
                "Question": QuestionResultSerializer(question).data,
                "Option": option.id
            })

            final_option = Question.objects.filter(option__is_true=True, category_id=category_id, id=question_id,
                                                   option=option)
            if final_option:
                count += 100 // len(unique_questions)
                statistic[j]["Student's option"] = "Correct"
            else:
                statistic[j]["Student's option"] = "Incorrect"

            score.questions.add(question)
            j += 1

        if 99 <= count < 100:
            count = 100
        score.score = count
        score.save()
        serialized_result = ResultSerializer(score).data
        response_data = {
            "score": serialized_result,
            "statistic": statistic
        }

        return Response(response_data)

    """
    Example for sending data:
    
    {
        "category_id": 1,
        "questions": [
            {
            "question_id": 1,
            "option_id": 1
            },
            {
            "question_id": 2,
            "option_id": 1
            },
            {
            "question_id": 3,
            "option_id": 1
            },
            {
            "question_id": 7,
            "option_id": 1
            }
        ]
    }

    """


# class ResultByTime(APIView):
#     permission_classes = [permissions.IsAdminUser]
#
#     @staticmethod
#     def get(request):
#         time_period = request.GET.get('time_period', 'day')
#
#         if time_period == 'day':
#             trunc_func = TruncDay('created_date')
#         elif time_period == 'week':
#             trunc_func = TruncWeek('created_date')
#         elif time_period == 'month':
#             trunc_func = TruncMonth('created_date')
#         else:
#             return Response("Invalid time_period parameter", status=status.HTTP_400_BAD_REQUEST)
#
#         results = Quizz.objects.annotate(
#             result_count=Count('id'),
#             average_score=Avg('score'),
#             truncated_date=trunc_func,
#         ).values('truncated_date', 'result_count', 'average_score')
#
#         return Response(results, status=status.HTTP_200_OK)


class AverageStatisticsListByCategory(APIView):
    # http://127.0.0.1:8000/api/quizz/result-by-category/

    def get(self, request):
        categories = Category.objects.all()
        category_results = []
        for category in categories:
            average_by_category = Quizz.calculate_average_result_category(category)
            if average_by_category is not None:
                rounded_average = round(average_by_category, 2)
                category_results.append({'title': category.title, 'average_result': rounded_average})
            else:
                category_results.append({'title': category.title, 'average_result': average_by_category})
        return Response(category_results)


class AverageStatisticsListByAccount(APIView):
    # http://127.0.0.1:8000/api/quizz/result-by-account

    def get(self, request):
        accounts = Account.objects.all()
        account_results = []
        for account in accounts:
            average_by_account = Quizz.calculate_average_result_account(account)
            serialized_account = AccountSerializer(account).data
            if average_by_account is not None:
                rounded_average = round(average_by_account, 2)
                account_results.append({"account": serialized_account, "average_by_account": rounded_average})
            else:
                account_results.append({"account": serialized_account, "average_by_account": average_by_account})

            return Response(account_results)


class TimeStatisticListAPIView(APIView):
    #  http://127.0.0.1:8000/api/quizz/result-by-time/?start_date=2023-05-29&end_date=2023-05-30
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'message': 'start_date and end_date parameters are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return Response({'message': 'start_date and end_date must be in the format YYYY-MM-DD'}, status=400)

        category_stats = Quizz.objects.filter(created_date__range=(start_date, end_date)).values_list('category')\
            .annotate(attempts=models.Count('id'), total_result=models.Avg('score'))\
            .values('category__title', 'account__username', 'attempts', 'total_result')

        statistics = []

        for category in category_stats:
            category_info = {
                'category': category['category__title'],
                'account': category["account__username"],
                'attempts': category['attempts'],
                'total_result': category['total_result']
            }
            statistics.append(category_info)

        return Response(statistics)

# class DayStatisticsListAPIview(generics.ListAPIView):
#     queryset = Quizz.objects.all()
#     serializer_class = ResultSerializer
#
#     def get_queryset(self):
#         qs = Quizz.objects.annotate(day=TruncDay('created_date')).filter(day=timezone.now().date()).annotate(
#             total_results=Count('id'))
#         return qs
#
#
# class WeekStatisticsListAPIView(generics.ListAPIView):
#     queryset = Quizz.objects.all()
#     serializer_class = ResultSerializer
#
#     def get_queryset(self):
#         now = timezone.now().date()
#         past_week = now - timedelta(days=7)
#         qs = Quizz.objects.filter(created_date__range=[past_week, now]).annotate(total_results=Count('id'))
#         return qs
#
#
# class MonthStatisticsListAPIView(generics.ListAPIView):
#     queryset = Quizz.objects.all()
#     serializer_class = ResultSerializer
#
#     def get_queryset(self):
#         now = timezone.now().date()
#         past_month = now - timedelta(days=30)
#         qs = Quizz.objects.filter(created_date__range=[past_month, now]).annotate(total_results=Count('id'))
#         return qs


class ContactListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
