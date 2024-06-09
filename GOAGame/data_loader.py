class DataLoader:
    def __init__(self, sheet, sheet_name, data_class):
        data = next((worksheet.get_all_records() for worksheet in sheet.worksheets() if worksheet.title == sheet_name), [])
        self.rows = {str(row["Id"]): data_class(row) for row in data}

    def get_row(self, id):
        return self.rows[id]

class GOACard:
    def __init__(self, row):
        self.id = str(row["Id"])
        self.power = row["Power"]