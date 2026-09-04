from django.urls import path

from .views import BankListView, MortgageApplyView, MortgageCalcView

urlpatterns = [
    path("banks", BankListView.as_view(), name="banks"),
    path("mortgage/calc", MortgageCalcView.as_view(), name="mortgage-calc"),
    path("mortgage/apply", MortgageApplyView.as_view(), name="mortgage-apply"),
]
