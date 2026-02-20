import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    db_name = os.getenv("DB_NAME", "chatbot_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "") # Might be empty on local Mac
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    print(f"Attempting to connect to PostgreSQL with user '{db_user}' at {db_host}:{db_port}...")
    
    try:
        # First try connecting to the default 'postgres' database to see if server is up
        conn = psycopg2.connect(
            dbname="postgres",
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.autocommit = True
        print("✅ Successfully connected to PostgreSQL server!")
        
        # Check if our target database exists
        with conn.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database WHERE datname = %s;", (db_name,))
            if cur.fetchone():
                print(f"✅ Target database '{db_name}' already exists.")
            else:
                print(f"⚠️ Target database '{db_name}' does not exist. Creating it now...")
                cur.execute(f"CREATE DATABASE {db_name};")
                print(f"✅ Created target database '{db_name}'.")
                
        conn.close()
        
        print("\n🎉 PostgreSQL is fully working and ready for the chatbot!")
        print("You can now safely run: python main.py")
        
    except psycopg2.OperationalError as e:
        print("❌ Failed to connect to PostgreSQL.")
        print(f"Error details: {e}")
        print("\nTroubleshooting tips:")
        print("1. Is PostgreSQL running? Try running: brew services start postgresql")
        print("2. Is the password correct? Check your .env file.")

if __name__ == "__main__":
    test_connection()
