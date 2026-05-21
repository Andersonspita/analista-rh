import sqlite3
import os
import logging
import bcrypt

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "database.sqlite")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def init_db():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT NOT NULL,
                email TEXT,
                telefone TEXT
            )
        """)
        
        # Check if empty, then seed
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            from dotenv import load_dotenv
            load_dotenv()
            default_user = os.getenv("API_USERNAME", "admin")
            default_pass = os.getenv("API_PASSWORD", "admin")
            hashed_pass = get_password_hash(default_pass)
            
            cursor.execute(
                "INSERT INTO users (username, hashed_password, email, telefone) VALUES (?, ?, ?, ?)",
                (default_user, hashed_pass, "admin@empresa.com", "(00) 00000-0000")
            )
            logger.info("Banco de dados SQLite inicializado com usuário padrão do .env.")
            
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
    finally:
        conn.close()
