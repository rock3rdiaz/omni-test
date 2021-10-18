from enum import IntEnum, unique


class ChoiceEnum(IntEnum):
    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


@unique
class ProductCategoryEnum(ChoiceEnum):
    """
    Some Product categories
    """
    FOOD = 0
    ELECTRONIC = 1
    CLOTHING = 2
    BOOKS = 3


@unique
class OrderStateEnum(ChoiceEnum):
    """
    Some Order states categories
    """
    OUTSTANDING = 0
    PAID = 1
    DELIVERED = 2


