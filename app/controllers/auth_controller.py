import requests
from typing import Dict, Optional, Tuple

class AuthController:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.user_data = None
        self.base_url = "http://127.0.0.1:8000/"

    def login(self) -> Tuple[bool, Dict[str, str]]:
        if not self._validate_input():
            return False, {'status': 'error', 'message': 'Usuário e senha obrigatórios'}

        try:
            response = requests.post(
                f"{self.base_url}api/login/",
                json={'username': self.username, 'password': self.password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    self.access_token = data['access']
                    self.refresh_token = data['refresh']
                    self.user_data = data['user_data']
                    return True, {
                        'status': 'success',
                        'message': data['message']
                    }
                else:
                    return False, {'status': 'error', 'message': data['message']}
            else:
                return False, {'status': 'error', 'message': 'Erro na API'}
                
        except Exception as e:
            return False, {'status': 'error', 'message': f'Erro: {str(e)}'}

    def _validate_input(self) -> bool:
        return bool(self.username.strip() and self.password.strip())

    def get_user_data(self) -> Optional[Dict]:
        return self.user_data

    def logout(self) -> None:
        self.access_token = None
        self.refresh_token = None
        self.user_data = None

    def get_authorization_header(self) -> Dict[str, str]:
        """Retorna header para requests HTTP"""
        if self.access_token:
            return {'Authorization': f'Bearer {self.access_token}'}
        return {}

    def get_ws_token(self) -> str:
        """Retorna o token para usar no WebSocket (?token=...)"""
        return self.access_token or ""