from rest_framework import serializers

from .models import Bank, MortgageApplication


class BankSerializer(serializers.ModelSerializer):
    rate = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    minDown = serializers.IntegerField(source="min_down_pct")
    maxTerm = serializers.IntegerField(source="max_term_years")

    class Meta:
        model = Bank
        fields = ["id", "name", "rate", "minDown", "maxTerm", "note"]


class MortgageCalcSerializer(serializers.Serializer):
    price = serializers.FloatField(min_value=0)
    downPct = serializers.FloatField(min_value=0, max_value=100)
    years = serializers.IntegerField(min_value=1, max_value=30)
    rate = serializers.FloatField(min_value=0, max_value=100)


class MortgageApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MortgageApplication
        fields = ["id", "listing", "bank", "price_usd", "down_pct", "years", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]
