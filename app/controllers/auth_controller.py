from typing import Dict, Optional, Tuple
from app.models.auth_user import AuthUserModal

class AuthController:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.auth_user = AuthUserModal(username, password)
        self.user_data = None
        
    def login(self) -> Tuple[bool, Dict[str, str]]:
        """
        Realiza o login e retorna status e mensagem de feedback.
        
        Returns:
            Tuple[bool, Dict]: (sucesso, {'status': str, 'message': str})
        """
        # Validação de entrada
        if not self._validate_input():
            return False, {
                'status': 'error',
                'message': 'Usuário e senha são obrigatórios'
            }
        
        try:
            # Tenta autenticar
            result = self.auth_user.authenticate()
            
            if result:
                self.user_data = self.auth_user.get_user_data()
                return True, {
                    'status': 'success',
                    'message': f'Bem-vindo, {self.user_data.get("name", "usuário")}'
                }
            else:
                return False, {
                    'status': 'error',
                    'message': 'Usuário ou senha inválidos'
                }
                
        except Exception as e:
            return False, {
                'status': 'error',
                'message': f'Erro na autenticação: {str(e)}'
            }
    
    def _validate_input(self) -> bool:
        """Valida campos de entrada."""
        if not self.username or not self.password:
            return False
        if len(self.username.strip()) == 0 or len(self.password.strip()) == 0:
            return False
        return True
    
    def get_user_data(self) -> Optional[Dict]:
        """Retorna dados do usuário autenticado."""
        return self.user_data
    
    def logout(self) -> None:
        """Limpa dados de sessão."""
        self.user_data = None