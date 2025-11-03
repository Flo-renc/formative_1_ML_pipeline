from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb+srv://team_user:user12345@cluster0.akwkdkn.mongodb.net/heart_disease_db?retryWrites=true&w=majority")
    return client["heart_disease_db"]
