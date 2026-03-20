from datetime import datetime
from django.shortcuts import render
from rest_framework.views import APIView
from .seriallizers import LoginSerializer
class login(APIView):
    def post(self,request):

        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user =serializer.validated_data.get('user')
            user.last_login = datetime.now()
            user.save()







