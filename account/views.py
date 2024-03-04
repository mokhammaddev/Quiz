from rest_framework import generics, status
from rest_framework.response import Response
from core.permissions import IsOwnerOrReadOnly
from .models import Account
from .serializers import RegisterSerializer, LoginSerializer, MyProfileSerializer, AccountSerializer


class AccountListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/account/list

    serializer_class = AccountSerializer
    queryset = Account.objects.all()


class RegisterView(generics.GenericAPIView):
    # http://127.0.0.1:8000/api/account/register

    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'data': "Account successfully created"}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    # http://127.0.0.1:8000/account/login

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'tokens': serializer.data['tokens']}, status=status.HTTP_200_OK)


class AccountRUView(generics.RetrieveUpdateAPIView):
    # http://127.0.0.1:8000/account/retrieve-update/{pk}
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, *args, **kwargs):
        query = self.get_object()
        if query:
            serializer = self.serializer_class(query)
            return Response({"success": True, 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "message": "query does not exist!"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "message": "credentials is invalid!"}, status=status.HTTP_404_NOT_FOUND)


class MyProfileListAPIView(generics.ListAPIView):
    # http://127.0.0.1:8000/account/my_profile/{pk}
    queryset = Account.objects.all()
    serializer_class = MyProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
