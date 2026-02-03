from app.config.database import connectdb

class AuthUserModal:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        
    def authenticate(self) -> bool:
        conn = connectdb()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM veterinario WHERE EMAIL = %s AND senha_veterinario = %s"
        cursor.execute(query, (self.username, self.password))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] > 0