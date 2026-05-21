"""
Script para adicionar um novo usuário ao banco de dados SQLite do Horizon ATS.
Execute: python add_user.py
"""
import sqlite3
import bcrypt
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.sqlite")

username = "andersonspita87@gmail.com"
password = "0134679Ab@"

# Gera o hash da senha
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Verifica se o usuário já existe
cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
row = cursor.fetchone()

if row:
    cursor.execute(
        "UPDATE users SET hashed_password = ? WHERE username = ?",
        (hashed, username)
    )
    print(f"✅ Usuário '{username}' atualizado com nova senha.")
else:
    cursor.execute(
        "INSERT INTO users (username, hashed_password, email, telefone) VALUES (?, ?, ?, ?)",
        (username, hashed, username, "")
    )
    print(f"✅ Usuário '{username}' criado com sucesso!")

conn.commit()
conn.close()
print("✅ Operação concluída. Banco de dados atualizado.")
