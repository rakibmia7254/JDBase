import json
import os
import random
import string

def create_db(name):
    dbs = json.loads(open('configs/dbs.json', 'r').read())
    name = name.replace(' ', '_')
    name2 = name.lower()+"_"+''.join(random.choices(string.hexdigits, k=10))
    if name in [list(d.keys())[0] for d in dbs]:
        return {"error":"database already exists"}
    data = []
    file_path = os.path.join('databases', f'{name2}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file)
    with open('configs/dbs.json', 'w') as file:
        data = {name: file_path}
        dbs.append(data)
        json.dump(dbs, file)
    return {"name":name,"file_path":file_path}

def get_dbs():
    # Specify the folder containing the JSON files
    folder_path = 'databases'
    # Check if the folder exists
    if not os.path.exists(folder_path):
        return []
    # Get all file names in the folder
    filenames = os.listdir(folder_path)
    # Filter only JSON files
    json_filenames = [filename for filename in filenames if filename.endswith('.json')]
    return json_filenames

def get_dbs_names():
    dbs = json.loads(open('configs/dbs.json', 'r').read())
    return [list(d.keys())[0] for d in dbs]

def get_db_by_name(name):
    dbs = json.loads(open('configs/dbs.json', 'r').read())
    for db in dbs:
        if name in db:
            return db[name]
    return {"error":"Database not found"}

class Database:
    def __init__(self, db_name):
        file_path = get_db_by_name(db_name)
        self.file_path = file_path
        self.database = self.load_database()

    def create_record(self, record):
        record["id"] = len(self.database) + 1
        self.database.append(record)
        self.save_database()
        return {"message":"Record created","data":record}

    def read_records(self):
        return self.database
    
    def get_by(self, query):
        key = list(query.keys())[0]
        value = query[key]
        records = []
        for record in self.database:
            if key in record and record[key] == value:
                records.append(record)
        if records:
            return records
        return {"error":"Record not found"}
    
    def update_record_by_query(self, query, updated_record):
        for record in self.database:
            match = True
            for key, value in query.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                for key, value in updated_record.items():
                    record[key] = value
        self.save_database()
        return {"message":"Record updated","data":updated_record}
    
    def delete_by(self, query):
        for record in self.database:
            match = True
            for key, value in query.items():
                if key not in record or record[key] != value:
                    match = False
                    break
            if match:
                self.database.remove(record)
                self.save_database()
                return {"message": "Record deleted"}
        return {"error": "Record not found"}
    
    def save_database(self):
        with open(self.file_path, "w") as file:
            json.dump(self.database, file)

    def load_database(self):
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

#database = Database("db1")
#database.create_record({"name": "Rahi", "age": 22})
#database.create_record({"name": "Jane", "age": 30})
#query= {"age": 10,"name":"Hasib"}

#print(database.read_records())
#print(Database.get_by({"name": "Rakib Hossain","age": 22}))
#print(database.update_record_by_query({"name": "Rakib Hossain"},{"skill": "Python-Api"}))

#database.delete_record(1)

#print(database.read_records())