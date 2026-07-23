from database.database import DatabaseManager

db = DatabaseManager()

print("Connected successfully!")

print(db.db.list_collection_names())
