import customtkinter as ctk
from datetime import datetime
import tkinter as tk

class ModuloProntuario:
    def __init__(self, content_frame, prontuario_controller):
        self.content = content_frame
        self.controller = prontuario_controller
        self.pets_map = {}
        self.placeholder = (
            "Descreva aqui os sintomas, temperatura, peso, conduta clínica "
            "e procedimentos realizados..."
        )

    def tela_prontuario(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=30)

        # HEADER
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))

        left_header = ctk.CTkFrame(header, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_header,
            text="Prontuário eletrônico",
            font=("Arial", 34, "bold")
        ).pack(anchor="w", pady=(0, 10))

        linha_paciente = ctk.CTkFrame(left_header, fg_color="transparent")
        linha_paciente.pack(anchor="w")

        ctk.CTkLabel(
            linha_paciente,
            text="PACIENTE:",
            font=("Arial", 12, "bold"),
            text_color="#64748B"
        ).pack(side="left", padx=(0, 8))

        self.combo_paciente = ctk.CTkOptionMenu(
            linha_paciente,
            values=["Carregando..."],
            command=self.on_pet_selecionado
        )
        self.combo_paciente.pack(side="left")

        self.btn_salvar = ctk.CTkButton(
            header,
            text="Salvar prontuário",
            fg_color="#A855F7",
            hover_color="#9333EA",
            font=("Arial", 14, "bold"),
            width=220,
            height=56,
            corner_radius=28,
            command=self.salvar_prontuario
        )
        self.btn_salvar.pack(side="right", anchor="n")

        # CORPO
        corpo = ctk.CTkFrame(container, fg_color="transparent")
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=1)
        # garantir que a única linha do corpo expanda para ocupar a altura disponível
        try:
            corpo.rowconfigure(0, weight=1)
        except Exception:
            pass

        # Editor (Evolução Clínica)
        editor_holder = ctk.CTkFrame(corpo, fg_color="transparent")
        editor_holder.grid(row=0, column=0, sticky="nsew", padx=(0, 25))
        # definir uma altura mínima para que o editor ocupe mais espaço vertical
        try:
            editor_holder.grid_propagate(False)
            editor_holder.configure(height=480)
        except Exception:
            pass

        topo_editor = ctk.CTkFrame(editor_holder, fg_color="transparent")
        topo_editor.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            topo_editor,
            text="\U0001F58A  Evolução Clínica",
            font=("Arial", 16, "bold"),
            text_color="#6B21A8"
        ).pack(side="left", anchor="w")

        ctk.CTkLabel(
            topo_editor,
            text="Pressione Salvar após as anotações",
            font=("Arial", 10),
            text_color="#94A3B8"
        ).pack(side="right", anchor="e")

        editor = ctk.CTkFrame(editor_holder, fg_color="transparent")
        editor.pack(fill="both", expand=True)

        self.txt = ctk.CTkTextbox(
            editor,
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0",
            fg_color="#FFFFFF",
            text_color="black",
            font=("Arial", 14),
            padx=20,
            pady=20
        )
        self.txt.pack(fill="both", expand=True)

        # placeholder handling
        self.txt.insert("1.0", self.placeholder)
        self.txt.configure(text_color="#94A3B8")
        self.txt.bind("<FocusIn>", self._on_txt_focus_in)
        self.txt.bind("<FocusOut>", self._on_txt_focus_out)

        # Histórico
        self.hist = ctk.CTkScrollableFrame(
            corpo,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=1,
            border_color="#E2E8F0",
            width=340,
            height=480
        )
        self.hist.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            self.hist,
            text="Histórico",
            font=("Arial", 18, "bold")
        ).pack(pady=(20, 10))

        # espaço para estado vazio (será preenchido por on_pet_selecionado)
        self.empty_state_frame = ctk.CTkFrame(self.hist, fg_color="transparent")
        self.empty_state_frame.pack(fill="both", expand=True)

        # container para os itens do histórico (será empilhado a partir do fundo)
        self.items_container = ctk.CTkFrame(self.hist, fg_color="transparent")
        self.items_container.pack(side="bottom", fill="both", expand=True, padx=6, pady=(6, 12))

        # Carregar pets
        self.carregar_pets()

    # =========================
    # FUNÇÕES
    # =========================

    def carregar_pets(self):
        pets = self.controller.listar_pets()

        nomes = []
        for pet in pets:
            pet_id = pet.get('id')
            nome = pet.get('NOME', 'Sem nome')
            nomes.append(nome)
            self.pets_map[nome] = pet_id

        if not nomes:
            nomes = ["Nenhum paciente"]

        # Melhor texto inicial
        values = ["Selecione um paciente..."] + nomes
        self.combo_paciente.configure(values=values)
        self.combo_paciente.set(values[0])

    def on_pet_selecionado(self, nome_pet):
        pet_id = self.pets_map.get(nome_pet)
        if not pet_id:
            return

        # limpar container de itens e esconder/mostrar estado vazio conforme necessário
        for w in self.items_container.winfo_children():
            w.destroy()

        historico = self.controller.historico(pet_id)

        if not historico:
            # mostrar estado vazio (reposiciona o empty_state_frame)
            for w in self.empty_state_frame.winfo_children():
                w.destroy()
            self.empty_state_frame.pack(fill="both", expand=True)
            wrapper = ctk.CTkFrame(self.empty_state_frame, fg_color="transparent")
            wrapper.place(relx=0.5, rely=0.5, anchor="center")

            circle = ctk.CTkFrame(wrapper, width=80, height=80, fg_color="#F8FAFC", corner_radius=40)
            circle.pack()
            # usar um label com emoji como ícone simples
            ctk.CTkLabel(circle, text="\U0001F5C3", font=("Arial", 28), text_color="#E6E6E6").place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(
                wrapper,
                text="Nenhum registro anterior encontrado para este pet.",
                text_color="#94A3B8",
                font=("Arial", 11),
                wraplength=220
            ).pack(pady=(12, 0))
            return

        # esconde o estado vazio quando houver registros
        try:
            self.empty_state_frame.pack_forget()
        except Exception:
            pass

        # preencher histórico (itens empilhados a partir do fundo)
        for registro in historico:
            data = registro.get('DATA_CONSULTA')
            texto = registro.get('OBSERVACOES') or ''
            
            # Converter string para datetime se necessário
            if isinstance(data, str):
                try:
                    from datetime import datetime
                    data = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                    data_str = data.strftime("%d %b %Y")
                except:
                    data_str = data
            else:
                data_str = data.strftime("%d %b %Y") if hasattr(data, 'strftime') else str(data)

            # tornar cada item maior para ocupar mais espaço vertical
            item = ctk.CTkFrame(self.items_container, fg_color="#F1F5F9", corner_radius=12, height=120)
            item.pack(side="bottom", fill="x", pady=12, padx=12)
            try:
                item.pack_propagate(False)
            except Exception:
                pass

            # hover effect
            def on_enter(e, w=item):
                try:
                    w.configure(fg_color="#ECEFF6")
                except Exception:
                    pass

            def on_leave(e, w=item):
                try:
                    w.configure(fg_color="#F1F5F9")
                except Exception:
                    pass

            item.bind("<Enter>", on_enter)
            item.bind("<Leave>", on_leave)

            # abrir prontuário completo ao clicar
            def _open(e, reg=registro):
                self.mostrar_prontuario(reg)

            item.bind("<Button-1>", _open)

            ctk.CTkLabel(item, text=data_str, font=("Arial", 14, "bold")).pack(anchor="w", padx=14, pady=(10,0))
            resumo_label = ctk.CTkLabel(item, text=(texto[:220] + ("..." if len(texto) > 220 else "")), font=("Arial", 12), wraplength=360, text_color="#334155")
            resumo_label.pack(anchor="w", padx=14, pady=(6, 10))
            resumo_label.bind("<Button-1>", _open)

    def salvar_prontuario(self):
        nome_pet = self.combo_paciente.get()
        pet_id = self.pets_map.get(nome_pet)

        if not pet_id:
            return
        texto = self.txt.get("1.0", "end").strip()
        if not texto or texto == self.placeholder:
            return

        self.controller.salvar(pet_id, texto)
        self.txt.delete("1.0", "end")
        # re-inserir placeholder
        self.txt.insert("1.0", self.placeholder)
        self.txt.configure(text_color="#94A3B8")
        self.on_pet_selecionado(nome_pet)

    def mostrar_prontuario(self, registro):
        parent = self.content.winfo_toplevel()
        topo = ctk.CTkToplevel(parent)
        topo.title("Prontuário")
        topo.geometry("600x480")
        topo.transient(parent)
        try:
            topo.grab_set()
        except Exception:
            pass

        data = registro.get('DATA_CONSULTA')
        obs = registro.get('OBSERVACOES') or ''
        if isinstance(data, str):
            try:
                data_dt = datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                data_str = data_dt.strftime("%d %b %Y %H:%M")
            except Exception:
                data_str = data
        else:
            data_str = data.strftime("%d %b %Y %H:%M") if hasattr(data, 'strftime') else str(data)

        head = ctk.CTkFrame(topo, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(head, text="Prontuário", font=("Arial", 18, "bold")).pack(side="left")
        ctk.CTkLabel(head, text=data_str, font=("Arial", 11), text_color="#64748B").pack(side="right")

        box = ctk.CTkTextbox(topo, corner_radius=10, border_width=1, border_color="#E2E8F0", padx=12, pady=12, font=("Arial", 12))
        box.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        box.insert("1.0", obs)
        try:
            box.configure(state="disabled")
        except Exception:
            pass

        ctk.CTkButton(topo, text="Fechar", width=120, command=topo.destroy).pack(pady=(0, 12))

    # placeholder handlers
    def _on_txt_focus_in(self, event):
        try:
            content = self.txt.get("1.0", "end").strip()
            if content == self.placeholder:
                self.txt.delete("1.0", "end")
                self.txt.configure(text_color="black")
        except Exception:
            pass

    def _on_txt_focus_out(self, event):
        try:
            content = self.txt.get("1.0", "end").strip()
            if not content:
                self.txt.insert("1.0", self.placeholder)
                self.txt.configure(text_color="#94A3B8")
        except Exception:
            pass
