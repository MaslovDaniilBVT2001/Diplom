import asyncpg
import asyncio

db_lock = asyncio.Lock()

async def connect_to_db():
    conn = await asyncpg.connect(user="mystudent", password="myparol02", database="mydatabase", host="188.225.58.30")
    return conn

async def close_connection(conn):
    await conn.close()

async def create_user_table(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            username VARCHAR(100),
            password VARCHAR(100),
            email VARCHAR(100),
            role VARCHAR(20)
        )
    """)

async def register_user(conn, first_name, last_name, username, password, email, role):
    async with db_lock:
        try:
            await conn.execute("""
                INSERT INTO users (first_name, last_name, username, password, email, role)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, first_name, last_name, username, password, email, role)
        except asyncpg.UniqueViolationError as e:
            raise ValueError("Пользователь с таким именем уже существует") from e

async def authenticate_user(conn, username, password):
    async with db_lock:
        user = await conn.fetchrow("SELECT * FROM users WHERE username = $1 AND password = $2", username, password)
        return user is not None

async def check_existing_user(conn, username, email):
    async with db_lock:
        query = "SELECT * FROM users WHERE username = $1 OR email = $2"
        row = await conn.fetchrow(query, username, email)
        return row is not None

async def get_db():
    conn = await connect_to_db()
    await asyncio.sleep(20)  # Ожидаем 20 секунд
    await close_connection(conn)
    return conn
