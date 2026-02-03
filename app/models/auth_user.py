import logging
from typing import Dict, Optional
from app.config.database import connectdb

# Configurar Django minimamente (apenas para validação de senha)
import os
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='temp-key-for-password-validation',
        PASSWORD_HASHERS=[
            'django.contrib.auth.hashers.PBKDF2PasswordHasher',
            'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
            'django.contrib.auth.hashers.ScryptPasswordHasher',
        ],
    )

from django.contrib.auth.hashers import check_password

# Configurar logging
logger = logging.getLogger(__name__)

class AuthUserModal:
    def __init__(self, username: str, password: str):
        self.username = username.strip() if username else ""
        self.password = password if password else ""
        self.user_data = None
        self._authenticate_attempts = 0
        
    def authenticate(self) -> bool:
        """
        Autentica o usuário no banco de dados.
        
        Returns:
            bool: True se autenticado com sucesso, False caso contrário
        """
        # Validação básica
        if not self._is_valid_input():
            logger.warning(f"Tentativa de login com entrada inválida: {self.username}")
            return False
        
        try:
            conn = connectdb()
            if conn is None:
                logger.error("Falha ao conectar ao banco de dados")
                return False
                
            cursor = conn.cursor()
            
            # Query para buscar hash de senha (compatível com Django)
            query = """
                SELECT id, nome, email, senha_veterinario
                FROM veterinario 
                WHERE email = %s
            """
            cursor.execute(query, (self.username,))
            result = cursor.fetchone()
            
            if result:
                # result[3] contém o hash de senha armazenado (do Django)
                stored_hash = result[3]
                
                # Usar check_password do Django para validar (compatível com todos os hashers)
                if check_password(self.password, stored_hash):
                    # Armazenar dados do usuário
                    self.user_data = {
                        'id': result[0],
                        'name': result[1],
                        'email': result[2],
                    }
                    logger.info(f"Login bem-sucedido para: {self.username}")
                    return True
                else:
                    logger.warning(f"Falha de login - senha incorreta para: {self.username}")
                    return False
            else:
                logger.warning(f"Falha de login - usuário não encontrado: {self.username}")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante autenticação: {str(e)}")
            return False
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
    
    def get_user_data(self) -> Optional[Dict]:
        """
        Retorna dados do usuário autenticado.
        
        Returns:
            Dict com dados do usuário ou None se não autenticado
        """
        return self.user_data
    
    def _is_valid_input(self) -> bool:
        """Valida os dados de entrada."""
        if not self.username or not self.password:
            return False
        if len(self.username) < 3:
            return False
        if len(self.password) < 3:
            return False
        return True