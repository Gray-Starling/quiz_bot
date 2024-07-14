import json

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        try:
            with open(self.file_path, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"File {self.file_path} not found")
            self.data = []

    def get_data(self):
        if self.data is None:
            self.load_data()
        return self.data

questions_loader = DataLoader('questions.json')
questions_loader.load_data()