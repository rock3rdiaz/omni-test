from rest_framework import serializers

from ecomerce.enums import ProductCategoryEnum


class ProductSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    name = serializers.CharField(max_length=30)
    description = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    category = serializers.IntegerField()
    price = serializers.IntegerField()
    units = serializers.IntegerField()

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("Product code is invalid")
        return value

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Product name is invalid")
        return value

    def validate_category(self, value):
        if int(value) not in ProductCategoryEnum.__members__.values():
            raise serializers.ValidationError(f'Category must be a valid value => {[i.value for i in ProductCategoryEnum.__members__.values()]}')
        return value

    def validate_price(self, value):
        if int(value) < 0:
            raise serializers.ValidationError('Product price is <= 0')
        return value

    def validate_units(self, value):
        if int(value) < 0:
            raise serializers.ValidationError('Units is <= 0')
        return value


class OrderSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    units = serializers.IntegerField()

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("Product code is invalid")
        return value

    def validate_units(self, value):
        if int(value) < 0:
            raise serializers.ValidationError('Units is <= 0')
        return value
