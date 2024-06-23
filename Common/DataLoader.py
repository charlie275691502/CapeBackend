from enum import Enum


class DataLoader:
    def __init__(self, sheet, sheet_name, data_class):
        data = next((worksheet.get_all_records() for worksheet in sheet.worksheets() if worksheet.title == sheet_name), [])
        self.rows = {str(row["Id"]): data_class(row) for row in data}
        self.ids = [str(row["Id"]) for row in data]

    def get_row(self, id):
        return self.rows[id]

class PowerType(Enum):
    Empty = 0
    Wealth = 1
    Industry = 2
    SeaPower = 3
    Military = 4
    
class CardType(Enum):
    Power = 0
    ActionMask = 1
    ActionReform = 2
    ActionExpand = 3
    Strategy = 4
    
class GOACardTypePowerPair:
    def __init__(self, power_type: PowerType, power: int):
        self.power_type = power_type
        self.power = power
        
    def get_order(self):
        return self.power_type.value * 1000 + self.power
    
class GOACard:
    def __init__(self, row):
        self.id = str(row["Id"])
        self.power_type = PowerType[row["PowerType"]]
        self.power = row["Power"]
        self.card_type = CardType[row["CardType"]]
        
        self.requirements = []
        if PowerType[row["RequirementPowerType1"]] != PowerType.Empty :
            self.requirements.append(GOACardTypePowerPair(PowerType[row["RequirementPowerType1"]], row["RequirementPower1"]))
        if PowerType[row["RequirementPowerType2"]] != PowerType.Empty :
            self.requirements.append(GOACardTypePowerPair(PowerType[row["RequirementPowerType2"]], row["RequirementPower2"]))
        self.requirements.sort(key=lambda pair: pair.get_order())
        
    def is_action_card(self) -> bool:
        return self.card_type == CardType.ActionMask or self.card_type == CardType.ActionReform or self.card_type == CardType.ActionExpand
    
    def is_public_card(self) -> bool:
        return self.card_type == CardType.Power or self.is_action_card()
        
class Constant:
    def __init__(self, row):
        self.id = str(row["Id"])
        self.value = row["Value"]
        
class GOACharacter:
    def __init__(self, row):
        self.id = str(row["Id"])
        self.image_key = row["ImageKey"]
        self.name_key = row["NameKey"]
        self.skill_key = row["SkillKey"]
        self.skill_description_key = row["SkillDescriptionKey"]