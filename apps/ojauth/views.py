from datetime import datetime
from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from MYJWT.myjwt import get_token
from .seriallizers import LoginSerializer
from .seriallizers import UerSerializer
from rest_framework.permissions import IsAuthenticated
import MYJWT.myjwt
class LoginView(APIView):
    def post(self,request):

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user =serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()
            token=get_token(user)
            return Response({"token":token,"user":UerSerializer(user).data})
        else:
            detail= list(serializer.errors.values())[0][0]
            print(detail)
            return Response({"detail":detail,"errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        return Response({"detail":"ok"})





