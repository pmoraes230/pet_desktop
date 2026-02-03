from app.models.auth_user import AuthUserModal

class AuthController:
    def __init__(self, username: str, password: str):
        self.auth_user = AuthUserModal(username, password)
        
    def login(self) -> bool:
        return self.auth_user.authenticate()