class AuthController:

    def __init__(self, view):
        self.view = view

    def login(self, email, senha):
        if not email or not senha:
            self.view.show_error("Preencha todos os campos")
            return

        # futuramente: chamada API / backend
        print("Login OK:", email)

    def register(self, data):
        print("Cadastro:", data)
