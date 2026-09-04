from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .calc import calc_mortgage
from .models import Bank, MortgageApplication
from .serializers import (
    BankSerializer,
    MortgageApplicationSerializer,
    MortgageCalcSerializer,
)


class BankListView(generics.ListAPIView):
    queryset = Bank.objects.filter(active=True)
    serializer_class = BankSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class MortgageCalcView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = MortgageCalcSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        return Response(calc_mortgage(price=d["price"], down_pct=d["downPct"], years=d["years"], rate=d["rate"]))


class MortgageApplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MortgageApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(user=request.user)
        return Response(
            MortgageApplicationSerializer(application).data, status=status.HTTP_201_CREATED
        )
