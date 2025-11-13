import enum

class MeasurementUnit(enum.Enum):
    G = ("weight", 1)
    KG = ("weight", 1000)
    ML = ("volume", 1)
    L = ("volume", 1000)
    TSP = ("volume", 5)
    TBSP = ("volume", 15)
    CUP = ("volume", 240)

    def __init__(self, unit_type: str, factor: float):
        self.unit_type = unit_type
        self.factor = factor

    def to_base(self, amount: float) -> float:
        return amount * self.factor

    def convert_to(self, amount: float, target_unit: 'MeasurementUnit') -> float:
        if self.unit_type != target_unit.unit_type:
            raise ValueError(f"Cannot convert between different unit types: {self.unit_type} and {target_unit.unit_type}")
        base_amount = self.to_base(amount)
        return base_amount / target_unit.factor