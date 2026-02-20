import os
import uuid
import psycopg2
from psycopg2 import pool

# Database connection pool
pg_pool = None

def get_connection():
    global pg_pool
    if not pg_pool:
        db_name = os.getenv("DB_NAME", "chatbot_db")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")

        pg_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
    return pg_pool.getconn()

def release_connection(conn):
    if pg_pool:
        pg_pool.putconn(conn)

def init_db():
    """Initializes the required database tables if they do not exist."""
    print(" [SYSTEM] Initializing expected output format PostgreSQL Database...")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Conversations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    thread_id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Messages table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id VARCHAR(255) PRIMARY KEY,
                    thread_id VARCHAR(255) REFERENCES conversations(thread_id),
                    user_id VARCHAR(255) REFERENCES users(user_id),
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
    except Exception as e:
        print(f" [ERROR] Error initializing database: {e}")
        conn.rollback()
    finally:
        release_connection(conn)

def get_or_create_user(user_id):
    """Ensures the user exists in the database."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE user_id = %s;", (user_id,))
            if not cur.fetchone():
                cur.execute("INSERT INTO users (user_id) VALUES (%s);", (user_id,))
                conn.commit()
    except Exception as e:
        print(f" [ERROR] Error in get_or_create_user: {e}")
        conn.rollback()
    finally:
        release_connection(conn)

def get_or_create_conversation(user_id, thread_id):
    """Ensures a conversation exists for the given user, returning the thread_id."""
    # Ensure user exists first
    get_or_create_user(user_id)
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT thread_id FROM conversations WHERE thread_id = %s;", (thread_id,))
            if not cur.fetchone():
                cur.execute("INSERT INTO conversations (thread_id, user_id) VALUES (%s, %s);", (thread_id, user_id))
                conn.commit()
    except Exception as e:
        print(f" [ERROR] Error in get_or_create_conversation: {e}")
        conn.rollback()
    finally:
        release_connection(conn)
        
    return thread_id

def load_recent_messages(user_id, thread_id="default_thread", limit=10):
    """Loads recent messages for a user from PostgreSQL."""
    conn = get_connection()
    messages = []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT role, content FROM messages 
                WHERE user_id = %s AND thread_id = %s
                ORDER BY timestamp ASC
                LIMIT %s;
            """, (user_id, thread_id, limit))
            
            rows = cur.fetchall()
            for role, content in rows:
                messages.append({"role": role, "content": content})
    except Exception as e:
        print(f" [ERROR] Error loading messages: {e}")
    finally:
        release_connection(conn)
    return messages

def save_message(user_id, role, content, thread_id="default_thread", message_id=None):
    """Saves a message to PostgreSQL."""
    if not message_id:
        message_id = str(uuid.uuid4())
        
    get_or_create_conversation(user_id, thread_id)
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages (message_id, thread_id, user_id, role, content)
                VALUES (%s, %s, %s, %s, %s);
            """, (message_id, thread_id, user_id, role, content))
        conn.commit()
    except Exception as e:
        print(f" [ERROR] Error saving message: {e}")
        conn.rollback()
    finally:
        release_connection(conn)
        
    return message_id
