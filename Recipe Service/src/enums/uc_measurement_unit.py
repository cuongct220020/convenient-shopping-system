import enum

class UCMeasurementUnit(str, enum.Enum):
    G = "G"
    KG = "KG"
    ML = "ML"
    L = "L"
    TSP = "TSP"
    TBSP = "TBSP"
    CUP = "CUP"

    @property
    def unit_type(self) -> str:
        if self in {UCMeasurementUnit.G, UCMeasurementUnit.KG}:
            return "weight"
        else:
            return "volume"

    @property
    def multiplier(self) -> int:
        return {
            UCMeasurementUnit.G: 1,
            UCMeasurementUnit.KG: 1000,
            UCMeasurementUnit.ML: 1,
            UCMeasurementUnit.L: 1000,
            UCMeasurementUnit.TSP: 5,
            UCMeasurementUnit.TBSP: 15,
            UCMeasurementUnit.CUP: 240,
        }[self]