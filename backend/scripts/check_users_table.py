import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.database_service import db_service

def check():
    print("Checking if 'users' table exists...")
    if not db_service.client:
        print("Supabase client is not initialized.")
        return
    try:
        response = db_service.client.table("users").select("*").limit(1).execute()
        print("Success! 'users' table exists. Data:", response.data)
    except Exception as e:
        print("Error checking 'users' table:", e)

if __name__ == "__main__":
    check()
