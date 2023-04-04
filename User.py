
from pymongo import MongoClient

class User:
    def __init__(self, name, email, password,client):
        self.name = name
        self.email = email
        self.password = password
        self.client = client
        self.logged_in = False
        self.admin = False

    def __repr__(self):
        return f"{self.name} {self.email} {self.password}"

    def login(self):
        record = self.client.flask_db.users.find_one({'username': self.name})
        print(record)
        if record:
            self.logged_in = True
            if record['admin'] == "true":
                self.admin = True
            return True
        else:
            return False
    
    def logout(self):
        self.logged_in = False
        self.admin = False
    
    
    