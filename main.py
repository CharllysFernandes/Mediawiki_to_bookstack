import customtkinter as ctk
import threading
import os
import re
import unicodedata
from datetime import datetime
from src.mediawiki_client import MediaWikiClient
from src.logger import Logger
from src.config_manager import ConfigManager
from src.pages_cache import PagesCache
from src.image_downloader import MediaWikiImageDownloader

class MediaWikiApp:
    def __init__(self):
        self.client = None
        self.logger = Logger()
        self.config_manager = ConfigManager()
        self.pages_cache = PagesCache()
        self.is_connected = False
        
        # Janela de configurações
        self.config_window = None
        
        # Sistema de navegação
        self.current_view = None
        self.views = {}
        self.logged_in = False
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("MediaWiki to BookStack")
        self.root.geometry("900x700")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Container principal
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True)
        
        # Barra de navegação lateral
        self.nav_rail = ctk.CTkFrame(main_container, width=200, corner_radius=0)
        self.nav_rail.pack(side="left", fill="y")
        self.nav_rail.pack_propagate(False)
        
        # Logo/Título da aplicação
        app_title = ctk.CTkLabel(self.nav_rail, text="MediaWiki\nto BookStack", 
                                font=ctk.CTkFont(size=16, weight="bold"))
        app_title.pack(pady=(20, 30))
        
        # Botões de navegação
        self.nav_buttons = {}
        
        # Botão Login
        self.nav_buttons["login"] = ctk.CTkButton(
            self.nav_rail, 
            text="🔐 Login", 
            command=lambda: self.navigate_to("login"),
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.nav_buttons["login"].pack(pady=(0, 10), padx=20)
        
        # Botão Páginas
        self.nav_buttons["pages"] = ctk.CTkButton(
            self.nav_rail, 
            text="📄 Páginas", 
            command=lambda: self.navigate_to("pages"),
            width=160,
            height=40,
            font=ctk.CTkFont(size=14),
            state="disabled"  # Desabilitado até fazer login
        )
        self.nav_buttons["pages"].pack(pady=(0, 10), padx=20)
        
        # Botão Configurações
        self.nav_buttons["config"] = ctk.CTkButton(
            self.nav_rail, 
            text="⚙️ Configurações", 
            command=lambda: self.navigate_to("config"),
            width=160,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.nav_buttons["config"].pack(pady=(0, 10), padx=20)
        
        # Separador
        separator = ctk.CTkFrame(self.nav_rail, height=2)
        separator.pack(fill="x", padx=20, pady=20)
        
        # Status da conexão
        self.connection_status = ctk.CTkLabel(self.nav_rail, text="● Desconectado", 
                                             text_color="red", font=ctk.CTkFont(size=12))
        self.connection_status.pack(pady=(10, 0))
        
        # Área de conteúdo principal
        self.content_area = ctk.CTkFrame(main_container)
        self.content_area.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Inicializar variáveis para views
        self.page_checkboxes = []
        self.current_pages = []
        self.extracted_content = {}
        
        # Criar todas as views
        self.create_all_views()
        
        # Navegar para a view inicial
        self.navigate_to("login")
        
        # Carregar configurações automaticamente
        self.load_config(show_message=False)
    
    def create_all_views(self):
        """Cria todas as views da aplicação"""
        self.views = {}
        
        # View de Login
        self.views["login"] = self.create_login_view()
        
        # View de Páginas
        self.views["pages"] = self.create_pages_view()
        
        # View de Configurações
        self.views["config"] = self.create_config_view()
        
        # Ocultar todas as views inicialmente
        for view in self.views.values():
            view.pack_forget()
    
    def navigate_to(self, view_name):
        """Navega para uma view específica"""
        # Atualizar estado dos botões
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == view_name:
                btn.configure(state="disabled")
            else:
                # Verificar se deve estar habilitado
                if btn_name == "pages" and not self.logged_in:
                    btn.configure(state="disabled")
                else:
                    btn.configure(state="normal")
        
        # Ocultar view atual
        if hasattr(self, "current_view") and self.current_view:
            self.current_view.pack_forget()
        
        # Mostrar nova view
        if view_name in self.views:
            self.views[view_name].pack(fill="both", expand=True, padx=20, pady=20)
            self.current_view = self.views[view_name]
            
        # Atualizar título da view
        self.update_view_title(view_name)
    
    def update_view_title(self, view_name):
        """Atualiza o título da view atual"""
        titles = {
            "login": "🔐 Conexão MediaWiki",
            "pages": "",
            "config": "⚙️ Configurações Avançadas"
        }
        
        # Se já existe um título, removê-lo
        for widget in self.content_area.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and hasattr(widget, "_is_title"):
                widget.destroy()
                break
        
        # Criar novo título
        title = ctk.CTkLabel(self.content_area, text=titles.get(view_name, ""), 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title._is_title = True
        title.pack(pady=(20, 10), anchor="w")
    
    def create_login_view(self):
        """Cria a view de login"""
        login_view = ctk.CTkFrame(self.content_area)
        
        # Frame de configuração (login)
        config_frame = ctk.CTkFrame(login_view)
        config_frame.pack(fill="x", padx=20, pady=20)
        
        # URL da API
        ctk.CTkLabel(config_frame, text="URL da API MediaWiki:").pack(anchor="w", padx=10, pady=(10,0))
        self.url_entry = ctk.CTkEntry(config_frame, placeholder_text="https://wiki.example.com/api.php")
        self.url_entry.pack(fill="x", padx=10, pady=(5,10))
        
        # Usuário
        ctk.CTkLabel(config_frame, text="Usuário:").pack(anchor="w", padx=10, pady=(0,0))
        self.username_entry = ctk.CTkEntry(config_frame, placeholder_text="Digite seu usuário")
        self.username_entry.pack(fill="x", padx=10, pady=(5,10))
        
        # Senha
        ctk.CTkLabel(config_frame, text="Senha:").pack(anchor="w", padx=10, pady=(0,0))
        self.password_entry = ctk.CTkEntry(config_frame, placeholder_text="Digite sua senha", show="*")
        self.password_entry.pack(fill="x", padx=10, pady=(5,10))
        
        # Checkbox para salvar senha
        self.save_password_var = ctk.BooleanVar()
        self.save_password_checkbox = ctk.CTkCheckBox(config_frame, text="Salvar senha (não recomendado)", 
                                                     variable=self.save_password_var)
        self.save_password_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para verificação SSL
        self.verify_ssl_var = ctk.BooleanVar(value=False)
        self.verify_ssl_checkbox = ctk.CTkCheckBox(config_frame, text="Verificar certificado SSL", 
                                                  variable=self.verify_ssl_var)
        self.verify_ssl_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para bypass de restrições
        self.bypass_restrictions_var = ctk.BooleanVar(value=True)
        self.bypass_restrictions_checkbox = ctk.CTkCheckBox(config_frame, 
                                                           text="Contornar restrições de permissão", 
                                                           variable=self.bypass_restrictions_var)
        self.bypass_restrictions_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para modo bot
        self.bot_mode_var = ctk.BooleanVar(value=False)
        self.bot_mode_checkbox = ctk.CTkCheckBox(config_frame, 
                                                text="Usar modo bot (para contas com privilégios)", 
                                                variable=self.bot_mode_var)
        self.bot_mode_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para expansão de templates
        self.expand_templates_var = ctk.BooleanVar(value=True)
        self.expand_templates_checkbox = ctk.CTkCheckBox(config_frame, 
                                                        text="Expandir templates (conteúdo completo)", 
                                                        variable=self.expand_templates_var)
        self.expand_templates_checkbox.pack(anchor="w", padx=10, pady=(0,10))
        
        # Botões de login
        login_button_frame = ctk.CTkFrame(login_view)
        login_button_frame.pack(fill="x", padx=20, pady=10)
        
        self.connect_btn = ctk.CTkButton(login_button_frame, text="Conectar", command=self.connect_to_wiki)
        self.connect_btn.pack(side="left", padx=10, pady=10)
        
        self.save_btn = ctk.CTkButton(login_button_frame, text="Salvar Config", command=self.save_config)
        self.save_btn.pack(side="left", padx=10, pady=10)
        
        self.load_btn = ctk.CTkButton(login_button_frame, text="Carregar Config", command=self.load_config)
        self.load_btn.pack(side="left", padx=10, pady=10)
        
        # Botão Sair (só aparece quando conectado)
        self.logout_btn = ctk.CTkButton(login_button_frame, text="Sair", command=self.logout, 
                                       fg_color="red", hover_color="darkred", state="disabled")
        self.logout_btn.pack(side="right", padx=10, pady=10)
        
        # Status da conexão
        self.status_label = ctk.CTkLabel(login_view, text="Status: Desconectado", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)
        
        return login_view
    
    def create_pages_view(self):
        """Cria a view de páginas"""
        pages_view = ctk.CTkFrame(self.content_area)
        
        # Informações da conexão
        self.connection_info_label = ctk.CTkLabel(pages_view, text="", 
                                                 font=ctk.CTkFont(size=14, weight="bold"))
        self.connection_info_label.pack(pady=10)
        
        # Botões para usuário conectado
        connected_buttons_frame = ctk.CTkFrame(pages_view)
        connected_buttons_frame.pack(fill="x", padx=20, pady=10)
        
        self.list_prefixes_btn = ctk.CTkButton(connected_buttons_frame, text="Listar Prefixos", command=self.list_page_prefixes)
        self.list_prefixes_btn.pack(side="left", padx=10, pady=10)
        
        # Frame para botões de páginas
        pages_buttons_frame = ctk.CTkFrame(pages_view)
        pages_buttons_frame.pack(fill="x", padx=20, pady=5)
        
        self.load_cache_btn = ctk.CTkButton(pages_buttons_frame, text="Carregar Cache", command=self.load_pages_cache)
        self.load_cache_btn.pack(side="left", padx=10, pady=10)
        
        self.refresh_pages_btn = ctk.CTkButton(pages_buttons_frame, text="Atualizar da API", command=self.refresh_pages_from_api)
        self.refresh_pages_btn.pack(side="left", padx=10, pady=10)
        
        # Frame para ações de extração
        extraction_buttons_frame = ctk.CTkFrame(pages_view)
        extraction_buttons_frame.pack(fill="x", padx=20, pady=5)
        
        self.extract_pages_btn = ctk.CTkButton(extraction_buttons_frame, text="Extrair Pendentes", command=self.extract_pending_content)
        self.extract_pages_btn.pack(side="left", padx=10, pady=10)
        
        # Novo botão para extrair em Markdown
        self.extract_markdown_btn = ctk.CTkButton(extraction_buttons_frame, text="Extrair Markdown", 
                                                command=self.extract_markdown_content, 
                                                fg_color="#2B5797", hover_color="#1f4788")
        self.extract_markdown_btn.pack(side="left", padx=10, pady=10)
        
        # Novo botão para extrair como TXT
        self.extract_txt_btn = ctk.CTkButton(extraction_buttons_frame, text="Extrair TXT", 
                                           command=self.extract_txt_content, 
                                           fg_color="#2B7A2B", hover_color="#1f5f1f")
        self.extract_txt_btn.pack(side="left", padx=10, pady=10)
        
        # Novo botão para extrair TXT + Imagens
        self.extract_txt_images_btn = ctk.CTkButton(extraction_buttons_frame, text="Extrair TXT + Imagens", 
                                                  command=self.extract_txt_with_images, 
                                                  fg_color="#7A2B7A", hover_color="#5f1f5f")
        self.extract_txt_images_btn.pack(side="left", padx=10, pady=10)
        
        # Adicionar botão para salvar arquivos
        self.save_files_btn = ctk.CTkButton(extraction_buttons_frame, text="Salvar Wikitext", 
                                          command=self.save_extracted_files, state="disabled")
        self.save_files_btn.pack(side="left", padx=10, pady=10)
        
        # Lista de prefixos/páginas
        content_frame = ctk.CTkFrame(pages_view)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(content_frame, text="Conteúdo da Wiki:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        # Progress bar
        self.progress_label = ctk.CTkLabel(content_frame, text="")
        self.progress_label.pack(anchor="w", padx=10, pady=(5,0))
        
        self.progress_bar = ctk.CTkProgressBar(content_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(5,5))
        self.progress_bar.set(0)
        
        # Frame para seleção de páginas
        self.pages_selection_frame = ctk.CTkScrollableFrame(content_frame, height=200)
        self.pages_selection_frame.pack(fill="both", expand=True, padx=10, pady=(5,5))
        
        # Botões de seleção
        selection_buttons_frame = ctk.CTkFrame(content_frame)
        selection_buttons_frame.pack(fill="x", padx=10, pady=(0,5))
        
        self.select_all_btn = ctk.CTkButton(selection_buttons_frame, text="Selecionar Tudo", 
                                          command=self.select_all_pages, width=120)
        self.select_all_btn.pack(side="left", padx=(0,5))
        
        self.select_none_btn = ctk.CTkButton(selection_buttons_frame, text="Deselecionar Tudo", 
                                           command=self.deselect_all_pages, width=120)
        self.select_none_btn.pack(side="left", padx=(0,5))
        
        self.selected_count_label = ctk.CTkLabel(selection_buttons_frame, text="0 páginas selecionadas")
        self.selected_count_label.pack(side="right", padx=(5,0))
        
        # Textbox para visualização de resultados
        self.content_textbox = ctk.CTkTextbox(content_frame, height=100)
        self.content_textbox.pack(fill="x", padx=10, pady=(0,10))
        
        return pages_view
    
    def create_config_view(self):
        """Cria a view de configurações"""
        config_view = ctk.CTkFrame(self.content_area)
        
        # Botão para abrir configurações avançadas
        config_button_frame = ctk.CTkFrame(config_view)
        config_button_frame.pack(fill="x", padx=20, pady=20)
        
        self.config_advanced_btn = ctk.CTkButton(config_button_frame, text="Abrir Configurações Avançadas", 
                                               command=self.open_config_window, 
                                               font=ctk.CTkFont(size=16), height=40)
        self.config_advanced_btn.pack(pady=20)
        
        # Botão Testar Conexão (só aparece quando conectado)
        self.test_btn = ctk.CTkButton(config_button_frame, text="Testar Conexão", command=self.test_connection,
                                     state="disabled", font=ctk.CTkFont(size=14), height=35)
        self.test_btn.pack(pady=(0, 20))
        
        # Informações sobre configurações
        info_frame = ctk.CTkFrame(config_view)
        info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        info_text = """
        📋 Configurações Disponíveis:
        
        • Conexão: URLs, credenciais e configurações de SSL
        • Extração: Configurações de templates e parsing
        • Cache: Gerenciamento de cache de páginas
        • Interface: Personalização da interface do usuário
        
        Clique no botão acima para acessar todas as configurações avançadas.
        """
        
        info_label = ctk.CTkLabel(info_frame, text=info_text, 
                                 font=ctk.CTkFont(size=14), 
                                 justify="left")
        info_label.pack(pady=20, padx=20, anchor="w")
        
        return config_view
        
    def log_message(self, message):
        """Adiciona mensagem ao log interno"""
        self.logger.info(message)
        
    def update_status(self, status, color="white"):
        """Atualiza o status da aplicação"""
        self.status_label.configure(text=f"Status: {status}", text_color=color)
        
    def connect_to_wiki(self):
        """Conecta ao MediaWiki em thread separada"""
        url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not url or not username or not password:
            self.log_message("ERRO: Todos os campos são obrigatórios")
            self.update_status("Erro - Campos obrigatórios", "red")
            return
            
        self.connect_btn.configure(state="disabled")
        self.update_status("Conectando...", "yellow")
        
        # Executar em thread separada para não travar a UI
        threading.Thread(target=self._connect_worker, args=(url, username, password), daemon=True).start()
        
    def logout(self):
        """Desconecta e volta para a tela de login"""
        try:
            self.client = None
            self.logged_in = False
            
            self.log_message("Desconectado com sucesso!")
            
            # Otimização: Agrupar todas as atualizações da UI
            def update_ui_after_logout():
                self.update_status("Desconectado", "white")
                self.connection_status.configure(text="● Desconectado", text_color="red")
                self.nav_buttons["pages"].configure(state="disabled")
                self.test_btn.configure(state="disabled")
                self.logout_btn.configure(state="disabled")
                
                # Limpar informações de conexão
                if hasattr(self, 'connection_info_label'):
                    self.connection_info_label.configure(text="")
                
                # Navegar de volta para login
                self.navigate_to("login")
                
                # Limpar senha por segurança
                self.password_entry.delete(0, 'end')
            
            # Uma única operação da UI
            update_ui_after_logout()
            
        except Exception as e:
            self.log_message(f"ERRO ao desconectar: {str(e)}")

    def _connect_worker(self, url, username, password):
        """Worker thread para conexão"""
        try:
            self.log_message(f"Tentando conectar em: {url}")
            
            verify_ssl = self.verify_ssl_var.get()
            bypass_restrictions = self.bypass_restrictions_var.get()
            bot_mode = self.bot_mode_var.get()
            
            if not verify_ssl:
                self.log_message("AVISO: Verificação SSL desabilitada")
            
            if bypass_restrictions:
                self.log_message("INFO: Modo bypass de restrições ativado")
            
            if bot_mode:
                self.log_message("INFO: Modo bot ativado")
            
            self.client = MediaWikiClient(
                url, 
                username, 
                password, 
                verify_ssl=verify_ssl,
                timeout=30
            )
            
            # Configurar opções de bypass
            if hasattr(self.client, 'bypass_restrictions'):
                self.client.bypass_restrictions = bypass_restrictions
            if hasattr(self.client, 'bot_mode'):
                self.client.bot_mode = bot_mode
            
            if self.client.login():
                self.log_message("Conexão estabelecida com sucesso!")
                self.logged_in = True
                
                # Otimização: Agrupar atualizações da UI em uma única operação
                def update_ui_after_login():
                    self.update_status("Conectado", "green")
                    self.connection_status.configure(text="● Conectado", text_color="green")
                    self.nav_buttons["pages"].configure(state="normal")
                    self.test_btn.configure(state="normal")
                    self.logout_btn.configure(state="normal")
                    self.navigate_to("pages")
                    
                    # Atualizar informações de conexão na view de páginas
                    if hasattr(self, 'connection_info_label'):
                        site_info = self.client.get_site_info()
                        if site_info:
                            info_text = f"Conectado a: {site_info.get('sitename', 'Wiki')} | Usuário: {username}"
                            self.connection_info_label.configure(text=info_text)
                
                # Uma única chamada root.after ao invés de múltiplas
                self.root.after(0, update_ui_after_login)
                
            else:
                self.log_message("ERRO: Falha na autenticação")
                self.logged_in = False
                self.root.after(0, lambda: self.update_status("Erro de autenticação", "red"))
                self.root.after(0, lambda: self.connection_status.configure(text="● Falha na autenticação", text_color="red"))
                
        except Exception as e:
            self.log_message(f"ERRO: {str(e)}")
            self.logged_in = False
            self.root.after(0, lambda: self.update_status("Erro de conexão", "red"))
            self.root.after(0, lambda: self.connection_status.configure(text="● Erro de conexão", text_color="red"))
        finally:
            self.root.after(0, lambda: self.connect_btn.configure(state="normal"))
            
    def test_connection(self):
        """Testa a conexão fazendo uma consulta simples"""
        if not self.client:
            return
            
        self.test_btn.configure(state="disabled")
        threading.Thread(target=self._test_worker, daemon=True).start()
        
    def _test_worker(self):
        """Worker thread para teste de conexão"""
        try:
            self.log_message("Testando conexão - consultando informações do site...")
            site_info = self.client.get_site_info()
            
            if site_info:
                self.log_message(f"Teste bem-sucedido!")
                self.log_message(f"Nome do site: {site_info.get('sitename', 'N/A')}")
                self.log_message(f"Versão: {site_info.get('generator', 'N/A')}")
            else:
                self.log_message("ERRO: Não foi possível obter informações do site")
                
        except Exception as e:
            self.log_message(f"ERRO no teste: {str(e)}")
        finally:
            self.root.after(0, lambda: self.test_btn.configure(state="normal"))
    
    def save_config(self):
        """Salva as configurações atuais"""
        try:
            config_data = {
                'api_url': self.url_entry.get().strip(),
                'username': self.username_entry.get().strip(),
                'verify_ssl': self.verify_ssl_var.get(),
                'bypass_restrictions': self.bypass_restrictions_var.get(),
                'bot_mode': self.bot_mode_var.get(),
                'expand_templates': self.expand_templates_var.get()
            }
            
            # Salvar senha apenas se checkbox estiver marcado
            if self.save_password_var.get():
                config_data['password'] = self.password_entry.get().strip()
                self.log_message("AVISO: Senha salva em texto simples. Considere questões de segurança.")
            
            self.config_manager.save_config(config_data)
            self.log_message("Configurações salvas com sucesso!")
            
        except Exception as e:
            self.log_message(f"ERRO ao salvar configurações: {str(e)}")
    
    def load_config(self, show_message=True):
        """Carrega as configurações salvas (otimizado - assíncrono)"""
        if show_message:
            # Para carregamento com mensagem, executar em thread para não travar UI
            threading.Thread(target=self._load_config_worker, args=(show_message,), daemon=True).start()
        else:
            # Para carregamento silencioso (inicialização), executar diretamente
            self._load_config_worker(show_message)
    
    def _load_config_worker(self, show_message=True):
        """Worker thread para carregamento de configurações"""
        try:
            config_data = self.config_manager.load_config()
            
            def update_ui_with_config():
                if config_data:
                    self.url_entry.delete(0, 'end')
                    self.url_entry.insert(0, config_data.get('api_url', ''))
                    
                    self.username_entry.delete(0, 'end')
                    self.username_entry.insert(0, config_data.get('username', ''))
                    
                    # Carregar configuração SSL
                    self.verify_ssl_var.set(config_data.get('verify_ssl', False))
                    self.bypass_restrictions_var.set(config_data.get('bypass_restrictions', True))
                    self.bot_mode_var.set(config_data.get('bot_mode', False))
                    self.expand_templates_var.set(config_data.get('expand_templates', True))
                    
                    if 'password' in config_data:
                        self.password_entry.delete(0, 'end')
                        self.password_entry.insert(0, config_data.get('password', ''))
                        self.save_password_var.set(True)
                    
                    if show_message:
                        self.log_message("Configurações carregadas com sucesso!")
                        
                else:
                    if show_message:
                        self.log_message("Nenhuma configuração salva encontrada.")
            
            # Atualizar UI na thread principal
            if show_message:
                self.root.after(0, update_ui_with_config)
            else:
                # Para carregamento silencioso, executar diretamente
                update_ui_with_config()
                        
        except Exception as e:
            error_msg = f"ERRO ao carregar configurações: {str(e)}"
            if show_message:
                self.root.after(0, lambda: self.log_message(error_msg))
            else:
                self.log_message(error_msg)
    
    def list_page_prefixes(self):
        """Lista os prefixos de páginas da wiki"""
        if not self.client:
            return
            
        self.list_prefixes_btn.configure(state="disabled")
        self.update_status("Carregando prefixos...", "yellow")
        self.content_textbox.delete("1.0", "end")
        threading.Thread(target=self._list_prefixes_worker, daemon=True).start()
        
    def _list_prefixes_worker(self):
        """Worker thread para listar prefixos"""
        try:
            self.log_message("Obtendo lista de namespaces/prefixos...")
            
            # Usar o método correto do client
            prefixes = self.client.get_namespace_prefixes()
            
            if prefixes:
                # Exibir na interface
                result_text = "\n".join(prefixes)
                self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
                self.root.after(0, lambda: self.content_textbox.insert("1.0", result_text))
                self.root.after(0, lambda: self.update_status("Prefixos carregados", "green"))
                
                # Contar apenas os namespaces principais (não aliases)
                main_count = len([p for p in prefixes if not p.startswith('    ')])
                self.log_message(f"Encontrados {main_count} namespaces")
                
            else:
                error_msg = "Nenhum namespace encontrado na wiki."
                self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
                self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
                self.root.after(0, lambda: self.update_status("Nenhum prefixo encontrado", "orange"))
                self.log_message("AVISO: Nenhum namespace retornado pela API")
                
        except Exception as e:
            error_msg = f"ERRO ao listar prefixos: {str(e)}"
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
            self.root.after(0, lambda: self.update_status("Erro ao carregar prefixos", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.list_prefixes_btn.configure(state="normal"))
    
    def load_pages_cache(self):
        """Carrega páginas do cache local e exibe sistema de navegação simples"""
        try:
            if self.pages_cache.load_cache():
                stats = self.pages_cache.get_statistics()
                
                # Inicializar navegação simples
                if not hasattr(self, 'current_page'):
                    self.current_page = 0
                
                # Criar interface de navegação
                self._create_cached_page_checkboxes()
                
                # Mostrar estatísticas gerais
                stats_text = f"""=== PÁGINAS PENDENTES PARA EXTRAÇÃO ===
Total no cache: {stats['total_pages']:,} páginas
Páginas pendentes: {stats['pending_pages']:,} páginas
Páginas processadas: {stats['processed_pages']:,} páginas
Progresso geral: {stats['progress_percentage']:.1f}%
Última atualização: {stats['last_updated'] or 'Nunca'}

📑 Use a navegação acima para explorar as páginas pendentes
✅ Selecione as páginas desejadas e clique em "Extrair Pendentes"
📄 Mostrando 50 páginas por vez para melhor performance
"""
                
                self.content_textbox.delete("1.0", "end")
                self.content_textbox.insert("1.0", stats_text)
                
                status_msg = f"Cache carregado - {stats['pending_pages']:,} páginas pendentes disponíveis"
                self.update_status(status_msg, "green")
                self.log_message(f"Cache carregado com {stats['total_pages']} páginas | {stats['pending_pages']} pendentes | Navegação ativa")
                
            else:
                self.content_textbox.delete("1.0", "end")
                self.content_textbox.insert("1.0", "Nenhum cache encontrado. Use 'Atualizar da API' para criar o cache inicial.")
                self.update_status("Cache não encontrado", "orange")
                self.log_message("Nenhum cache de páginas encontrado")
                
        except Exception as e:
            error_msg = f"ERRO ao carregar cache: {str(e)}"
            self.content_textbox.delete("1.0", "end")
            self.content_textbox.insert("1.0", error_msg)
            self.update_status("Erro ao carregar cache", "red")
            self.log_message(error_msg)
    
    def refresh_pages_from_api(self):
        """Atualiza o cache com páginas da API"""
        if not self.client:
            return
            
        self.refresh_pages_btn.configure(state="disabled")
        self.update_status("Atualizando cache da API...", "yellow")
        threading.Thread(target=self._refresh_pages_worker, daemon=True).start()
    
    def _refresh_pages_worker(self):
        """Worker thread para atualizar cache da API"""
        try:
            self.log_message("Buscando páginas da API para atualizar cache...")
            
            def progress_callback(total, batch):
                self.root.after(0, lambda: self.progress_label.configure(text=f"API: {total} páginas carregadas"))
            
            # Buscar páginas da API
            api_pages = self.client.get_all_pages(callback=progress_callback)
            
            if api_pages:
                # Atualizar cache preservando status existente
                new_pages_count = self.pages_cache.update_pages_from_api(api_pages)
                
                # Remover páginas que não existem mais
                current_pageids = [page.get('pageid') for page in api_pages]
                self.pages_cache.remove_deleted_pages(current_pageids)
                
                # Salvar cache atualizado
                if self.pages_cache.save_cache():
                    stats = self.pages_cache.get_statistics()
                    
                    # Inicializar navegação simples se não existir
                    if not hasattr(self, 'current_page'):
                        self.current_page = 0
                    
                    result_text = f"""=== CACHE ATUALIZADO COM SUCESSO ===
Total de páginas: {stats['total_pages']:,}
Novas páginas adicionadas: {new_pages_count:,}
Páginas pendentes: {stats['pending_pages']:,}
Páginas processadas: {stats['processed_pages']:,}
Progresso geral: {stats['progress_percentage']:.1f}%

 Use a navegação acima para explorar as páginas pendentes
✅ Selecione as páginas desejadas e clique em "Extrair Pendentes"
📄 Mostrando 50 páginas por vez para melhor performance

Cache salvo em: config/pages_cache.json
"""
                    
                    self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
                    self.root.after(0, lambda: self.content_textbox.insert("1.0", result_text))
                    self.root.after(0, lambda: self.update_status(f"Cache atualizado: {stats['total_pages']:,} páginas", "green"))
                    self.root.after(0, lambda: self.progress_bar.set(1.0))
                    
                    # Atualizar checkboxes com sistema de navegação
                    self.root.after(0, self._create_cached_page_checkboxes)
                    
                    self.log_message(f"Cache atualizado: {stats['total_pages']} páginas ({new_pages_count} novas)")
                    
                else:
                    error_msg = "ERRO: Falha ao salvar cache atualizado"
                    self.root.after(0, lambda: self.update_status("Erro ao salvar cache", "red"))
                    self.log_message(error_msg)
                    
            else:
                error_msg = "ERRO: Nenhuma página retornada pela API"
                self.root.after(0, lambda: self.update_status("API não retornou páginas", "red"))
                self.log_message(error_msg)
                
        except Exception as e:
            error_msg = f"ERRO ao atualizar cache: {str(e)}"
            self.root.after(0, lambda: self.update_status("Erro na atualização", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.refresh_pages_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
    
    def _create_cached_page_checkboxes(self):
        """Cria checkboxes para páginas pendentes do cache com navegação simples"""
        # Limpar TODOS os widgets do frame de seleção (checkboxes + controles de navegação)
        for widget in self.pages_selection_frame.winfo_children():
            widget.destroy()
        self.page_checkboxes.clear()
        
        # Inicializar controles de paginação simples
        if not hasattr(self, 'current_page'):
            self.current_page = 0
        
        # Fixar em 50 páginas por página
        self.pages_per_page = 50
        
        # Obter páginas pendentes (sem filtros)
        all_pages = self._get_filtered_pages()
        
        # Calcular paginação
        total_pages = len(all_pages)
        total_page_count = max(1, (total_pages + self.pages_per_page - 1) // self.pages_per_page)
        
        # Ajustar página atual se necessário
        if self.current_page >= total_page_count:
            self.current_page = max(0, total_page_count - 1)
        
        # Obter páginas da página atual
        start_idx = self.current_page * self.pages_per_page
        end_idx = min(start_idx + self.pages_per_page, total_pages)
        display_pages = all_pages[start_idx:end_idx]
        
        # Criar controles de navegação
        self._create_pagination_controls(total_pages, total_page_count)
        
        # Separador
        separator = ctk.CTkFrame(self.pages_selection_frame, height=2)
        separator.pack(fill="x", padx=10, pady=5)
        
        # Informações da página atual
        if total_pages > 0:
            page_info = ctk.CTkLabel(
                self.pages_selection_frame,
                text=f"📄 Mostrando {len(display_pages)} de {total_pages} páginas pendentes | Página {self.current_page + 1} de {total_page_count}",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            page_info.pack(pady=(5, 10))
        
        # Otimização: criar widgets em lote
        self._batch_ui_update = True
        
        for i, page in enumerate(display_pages):
            title = page.get('title', 'Sem título')
            page_id = page.get('pageid', 'N/A')
            
            # Criar variável para o checkbox
            var = ctk.BooleanVar(value=False)  # Desmarcado por padrão
            
            # Frame simplificado
            page_frame = ctk.CTkFrame(self.pages_selection_frame)
            page_frame.pack(fill="x", padx=2, pady=1)
            
            # Status icon (sempre pendente já que filtramos apenas pendentes)
            status_icon = "⏳"
            status_text = "Pendente"
            
            # Checkbox com informações detalhadas
            checkbox_text = f"{status_icon} {title} (ID: {page_id}) - {status_text}"
            checkbox = ctk.CTkCheckBox(
                page_frame, 
                text=checkbox_text,
                variable=var,
                command=self._delayed_update_count
            )
            checkbox.pack(anchor="w", padx=5, pady=2)
            
            # Armazenar referências
            checkbox.page_data = page
            checkbox.var = var
            self.page_checkboxes.append(checkbox)
        
        # Reabilitar callbacks
        self._batch_ui_update = False
        
        # Se não há páginas para mostrar
        if total_pages == 0:
            no_pages_label = ctk.CTkLabel(
                self.pages_selection_frame,
                text="📭 Nenhuma página pendente encontrada no cache",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_pages_label.pack(pady=20)
        
        # Atualizar contador
        self.update_selected_count()
    
    def _get_filtered_pages(self):
        """Obtém todas as páginas pendentes (sem filtros)"""
        # Obter todas as páginas do cache
        all_pages = self.pages_cache.pages_data
        
        # Retornar apenas páginas pendentes (status 0)
        return [p for p in all_pages if p.get('status', 0) == 0]
    
    def _create_pagination_controls(self, total_pages, total_page_count):
        """Cria controles simples de navegação de páginas"""
        # Frame principal para controles de navegação
        controls_frame = ctk.CTkFrame(self.pages_selection_frame)
        controls_frame.pack(fill="x", padx=5, pady=10)
        
        # Título da navegação
        ctk.CTkLabel(controls_frame, text="📑 Navegação", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        # Frame para controles de paginação
        nav_frame = ctk.CTkFrame(controls_frame)
        nav_frame.pack(padx=10, pady=(0, 10))
        
        # Botão primeira página
        first_btn = ctk.CTkButton(nav_frame, text="⏮️ Primeira", command=self._go_to_first_page, width=80, height=30)
        first_btn.pack(side="left", padx=5, pady=10)
        
        # Botão página anterior
        prev_btn = ctk.CTkButton(nav_frame, text="◀️ Anterior", command=self._go_to_prev_page, width=80, height=30)
        prev_btn.pack(side="left", padx=2, pady=10)
        
        # Informação da página atual
        page_info_text = f"Página {self.current_page + 1} de {total_page_count}"
        page_info_label = ctk.CTkLabel(nav_frame, text=page_info_text, font=ctk.CTkFont(size=14, weight="bold"))
        page_info_label.pack(side="left", padx=20, pady=10)
        
        # Botão próxima página
        next_btn = ctk.CTkButton(nav_frame, text="Próxima ▶️", command=self._go_to_next_page, width=80, height=30)
        next_btn.pack(side="left", padx=2, pady=10)
        
        # Botão última página
        last_btn = ctk.CTkButton(nav_frame, text="Última ⏭️", command=self._go_to_last_page, width=80, height=30)
        last_btn.pack(side="left", padx=5, pady=10)
        
        # Estatísticas centralizadas
        stats_frame = ctk.CTkFrame(controls_frame)
        stats_frame.pack(padx=10, pady=(0, 10))
        
        stats = self.pages_cache.get_statistics()
        stats_text = f"📊 Total: {total_pages} páginas pendentes | Processadas: {stats.get('processed_pages', 0)} | Progresso: {stats.get('progress_percentage', 0):.1f}%"
        
        stats_label = ctk.CTkLabel(stats_frame, text=stats_text, font=ctk.CTkFont(size=12))
        stats_label.pack(padx=10, pady=5)
    
    def _delayed_update_count(self):
        """Callback otimizado que evita atualizações excessivas"""
        if hasattr(self, '_batch_ui_update') and self._batch_ui_update:
            return  # Skip durante batch update
            
        # Cancelar timer anterior se existir
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        
        # Agendar atualização com delay para evitar spam
        self._update_timer = self.root.after(100, self.update_selected_count)
    
    def _load_more_pages(self):
        """Método legado - redireciona para próxima página"""
        self._go_to_next_page()
    
    def _on_search_change(self, event):
        """Método removido - filtros desabilitados"""
        pass
    
    def _on_status_filter_change(self, selected_status):
        """Método removido - filtros desabilitados"""
        pass
    
    def _on_pages_per_page_change(self, selected_count):
        """Método removido - fixado em 50 páginas"""
        pass
    
    def _clear_filters(self):
        """Método removido - filtros desabilitados"""
        pass
    
    def _go_to_first_page(self):
        """Vai para a primeira página"""
        if self.current_page > 0:
            self.current_page = 0
            self._refresh_page_display()
    
    def _go_to_prev_page(self):
        """Vai para a página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self._refresh_page_display()
    
    def _go_to_next_page(self):
        """Vai para a próxima página"""
        all_pages = self._get_filtered_pages()
        total_page_count = max(1, (len(all_pages) + self.pages_per_page - 1) // self.pages_per_page)
        
        if self.current_page < total_page_count - 1:
            self.current_page += 1
            self._refresh_page_display()
    
    def _go_to_last_page(self):
        """Vai para a última página"""
        all_pages = self._get_filtered_pages()
        total_page_count = max(1, (len(all_pages) + self.pages_per_page - 1) // self.pages_per_page)
        
        if self.current_page < total_page_count - 1:
            self.current_page = total_page_count - 1
            self._refresh_page_display()
    
    def _go_to_specific_page(self, event=None):
        """Vai para uma página específica"""
        try:
            page_num = int(self.goto_page_var.get())
            all_pages = self._get_filtered_pages()
            total_page_count = max(1, (len(all_pages) + self.pages_per_page - 1) // self.pages_per_page)
            
            # Validar número da página (1-indexed para o usuário)
            if 1 <= page_num <= total_page_count:
                self.current_page = page_num - 1  # Converter para 0-indexed
                self.goto_page_var.set("")  # Limpar campo
                self._refresh_page_display()
            else:
                self.log_message(f"Página inválida: {page_num}. Use um número entre 1 e {total_page_count}")
                
        except ValueError:
            if self.goto_page_var.get().strip():  # Só mostrar erro se há texto
                self.log_message("Digite um número de página válido")
    
    def _refresh_page_display(self):
        """Atualiza a exibição das páginas"""
        self._create_cached_page_checkboxes()
        
        # Log simples
        all_pages = self._get_filtered_pages()
        self.log_message(f"Navegação: Página {self.current_page + 1} | Total: {len(all_pages)} páginas pendentes")
    
    def extract_pending_content(self):
        """Extrai conteúdo apenas das páginas pendentes selecionadas"""
        if not self.client or not self.page_checkboxes:
            self.log_message("ERRO: Carregue as páginas primeiro")
            self.update_status("Carregue as páginas primeiro", "red")
            return
        
        selected_pages = self.get_selected_pages()
        if not selected_pages:
            self.log_message("ERRO: Nenhuma página selecionada")
            self.update_status("Nenhuma página selecionada", "red")
            return
            
        self.extract_pages_btn.configure(state="disabled")
        self.update_status("Extraindo páginas pendentes...", "yellow")
        self.content_textbox.delete("1.0", "end")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._extract_pending_worker, args=(selected_pages,), daemon=True).start()
    
    def _extract_pending_worker(self, selected_pages):
        """Worker thread para extrair conteúdo de páginas pendentes com atualização de status"""
        try:
            page_titles = [page['title'] for page in selected_pages]
            page_ids = [page['pageid'] for page in selected_pages]
            total_pages = len(page_titles)
            processed = 0
            
            self.log_message(f"Iniciando extração de {total_pages} páginas pendentes selecionadas...")
            
            def progress_callback(current_total, batch_size):
                nonlocal processed
                processed = current_total
                progress = processed / total_pages if total_pages > 0 else 0
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.progress_label.configure(text=f"Extraindo: {processed}/{total_pages}"))
            
            # Extrair conteúdo
            expand_templates = self.expand_templates_var.get()
            contents = self.client.get_page_content_batch(
                page_titles, 
                callback=progress_callback, 
                format_type='wikitext',
                expand_templates=expand_templates
            )
            
            # Processar resultados e atualizar status no cache
            successful = 0
            failed = 0
            processed_ids = []
            failed_details = []
            
            for i, (title, content) in enumerate(contents.items()):
                page_id = page_ids[i] if i < len(page_ids) else None
                
                if isinstance(content, dict) and content.get('wikitext'):
                    # Sucesso
                    successful += 1
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 1)  # Marcar como processada
                        processed_ids.append(page_id)
                else:
                    # Falha
                    failed += 1
                    error_msg = content if isinstance(content, str) else "Erro desconhecido"
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 0, error_msg)  # Manter pendente com erro
                    failed_details.append(f"❌ {title}: {error_msg}")
            
            # Salvar cache atualizado
            self.pages_cache.save_cache()
            
            # Preparar relatório
            stats = self.pages_cache.get_statistics()
            
            summary = [
                f"=== EXTRAÇÃO DE PÁGINAS PENDENTES ===",
                f"Páginas selecionadas: {total_pages}",
                f"Extraídas com sucesso: {successful}",
                f"Falharam: {failed}",
                f"",
                f"=== PROGRESSO GERAL ===",
                f"Total no cache: {stats['total_pages']:,}",
                f"Processadas: {stats['processed_pages']:,}",
                f"Pendentes: {stats['pending_pages']:,}",
                f"Progresso: {stats['progress_percentage']:.1f}%",
                ""
            ]
            
            # Adicionar detalhes de falhas se houver
            if failed_details:
                summary.append("=== PÁGINAS COM ERRO ===")
                summary.extend(failed_details[:10])  # Mostrar até 10 erros
                if len(failed_details) > 10:
                    summary.append(f"... e mais {len(failed_details) - 10} erros")
                summary.append("")
            
            if successful > 0:
                summary.append("✅ Páginas processadas foram marcadas como concluídas no cache")
            
            result_text = "\n".join(summary)
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", result_text))
            
            # Status final
            status_msg = f"Extraídas: {successful}/{total_pages} | Cache: {stats['progress_percentage']:.1f}%"
            status_color = "green" if failed == 0 else "orange"
            self.root.after(0, lambda: self.update_status(status_msg, status_color))
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            
            # Log
            self.log_message(f"Extração completa: {successful}/{total_pages} páginas. Progresso geral: {stats['progress_percentage']:.1f}%")
            
            # Armazenar conteúdo para salvar arquivos
            self.extracted_content = contents
            
            # Habilitar botão de salvar se há conteúdo
            if successful > 0:
                self.root.after(0, lambda: self.save_files_btn.configure(state="normal"))
            
            # Atualizar lista de páginas (mostrar páginas pendentes restantes)
            self.root.after(0, self._create_cached_page_checkboxes)
            
        except Exception as e:
            error_msg = f"ERRO na extração: {str(e)}"
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
            self.root.after(0, lambda: self.update_status("Erro na extração", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.extract_pages_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
    
    def extract_markdown_content(self):
        """Extrai conteúdo das páginas selecionadas em formato Markdown"""
        if not self.client or not self.page_checkboxes:
            self.log_message("ERRO: Carregue as páginas primeiro")
            self.update_status("Carregue as páginas primeiro", "red")
            return
        
        selected_pages = self.get_selected_pages()
        if not selected_pages:
            self.log_message("ERRO: Nenhuma página selecionada")
            self.update_status("Nenhuma página selecionada", "red")
            return
            
        self.extract_markdown_btn.configure(state="disabled")
        self.update_status("Extraindo páginas em Markdown...", "yellow")
        self.content_textbox.delete("1.0", "end")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._extract_markdown_worker, args=(selected_pages,), daemon=True).start()
    
    def _extract_markdown_worker(self, selected_pages):
        """Worker thread para extrair conteúdo em Markdown"""
        try:
            page_titles = [page['title'] for page in selected_pages]
            page_ids = [page['pageid'] for page in selected_pages]
            total_pages = len(page_titles)
            processed = 0
            
            self.log_message(f"Iniciando extração Markdown de {total_pages} páginas selecionadas...")
            
            def progress_callback(current_total, batch_size):
                nonlocal processed
                processed = current_total
                progress = processed / total_pages if total_pages > 0 else 0
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.progress_label.configure(text=f"Extraindo Markdown: {processed}/{total_pages}"))
            
            # Extrair conteúdo em formato Markdown
            expand_templates = self.expand_templates_var.get()
            contents = self.client.get_page_content_batch(
                page_titles, 
                callback=progress_callback, 
                format_type='markdown',  # Formato Markdown
                expand_templates=expand_templates
            )
            
            # Processar resultados e atualizar status no cache
            successful = 0
            failed = 0
            processed_ids = []
            failed_details = []
            markdown_content = {}
            
            for i, (title, content) in enumerate(contents.items()):
                page_id = page_ids[i] if i < len(page_ids) else None
                
                if isinstance(content, dict) and content.get('markdown'):
                    # Sucesso
                    successful += 1
                    markdown_content[title] = content
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 1)  # Marcar como processada
                        processed_ids.append(page_id)
                else:
                    # Falha
                    failed += 1
                    error_msg = content if isinstance(content, str) else "Erro desconhecido"
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 0, error_msg)  # Manter pendente com erro
                    failed_details.append(f"❌ {title}: {error_msg}")
            
            # Salvar cache atualizado
            self.pages_cache.save_cache()
            
            # Preparar relatório
            stats = self.pages_cache.get_statistics()
            
            summary = [
                f"=== EXTRAÇÃO MARKDOWN CONCLUÍDA ===",
                f"Páginas selecionadas: {total_pages}",
                f"Extraídas com sucesso: {successful}",
                f"Falharam: {failed}",
                f"",
                f"=== PROGRESSO GERAL ===",
                f"Total no cache: {stats['total_pages']:,}",
                f"Processadas: {stats['processed_pages']:,}",
                f"Pendentes: {stats['pending_pages']:,}",
                f"Progresso: {stats['progress_percentage']:.1f}%",
                ""
            ]
            
            # Adicionar detalhes de falhas se houver
            if failed_details:
                summary.append("=== PÁGINAS COM ERRO ===")
                summary.extend(failed_details[:10])  # Mostrar até 10 erros
                if len(failed_details) > 10:
                    summary.append(f"... e mais {len(failed_details) - 10} erros")
                summary.append("")
            
            if successful > 0:
                summary.append("✅ Páginas processadas foram marcadas como concluídas no cache")
                summary.append(f"📄 {successful} arquivos Markdown prontos para download")
                
                # Salvar arquivos Markdown automaticamente
                self._save_markdown_files(markdown_content)
            
            result_text = "\n".join(summary)
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", result_text))
            
            # Status final
            status_msg = f"Markdown: {successful}/{total_pages} | Cache: {stats['progress_percentage']:.1f}%"
            status_color = "green" if failed == 0 else "orange"
            self.root.after(0, lambda: self.update_status(status_msg, status_color))
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            
            # Log
            self.log_message(f"Extração Markdown completa: {successful}/{total_pages} páginas. Progresso geral: {stats['progress_percentage']:.1f}%")
            
            # Atualizar lista de páginas (mostrar páginas pendentes restantes)
            self.root.after(0, self._create_cached_page_checkboxes)
            
        except Exception as e:
            error_msg = f"ERRO na extração Markdown: {str(e)}"
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
            self.root.after(0, lambda: self.update_status("Erro na extração Markdown", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.extract_markdown_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
    
    def _save_markdown_files(self, markdown_content):
        """Salva automaticamente os arquivos Markdown extraídos"""
        try:
            # Importar módulos necessários
            import os
            from datetime import datetime
            
            # Criar diretório para os arquivos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"extracted_markdown_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            saved_count = 0
            
            # Salvar cada página como arquivo Markdown
            for title, content in markdown_content.items():
                if isinstance(content, dict) and content.get('markdown'):
                    # Sanitizar nome do arquivo
                    filename = self._sanitize_filename(title) + ".md"
                    filepath = os.path.join(output_dir, filename)
                    
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            # Escrever cabeçalho
                            f.write(f"# {title}\n\n")
                            f.write(f"**Fonte:** MediaWiki  \n")
                            f.write(f"**Data de extração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  \n")
                            f.write(f"**Formato:** Markdown\n\n")
                            f.write("---\n\n")
                            
                            # Escrever conteúdo Markdown
                            f.write(content['markdown'])
                            
                        saved_count += 1
                        
                    except Exception as e:
                        self.log_message(f"ERRO ao salvar {filename}: {str(e)}")
            
            # Criar arquivo de índice
            index_path = os.path.join(output_dir, "README.md")
            self._create_markdown_index(index_path, markdown_content)
            
            self.log_message(f"✅ {saved_count} arquivos Markdown salvos em: {output_dir}")
            
        except Exception as e:
            self.log_message(f"ERRO ao salvar arquivos Markdown: {str(e)}")
    
    def _create_markdown_index(self, index_path, content_dict):
        """Cria arquivo de índice para os arquivos Markdown"""
        try:
            from datetime import datetime
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("# 📚 Índice de Páginas Extraídas - Markdown\n\n")
                f.write(f"**Data de extração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  \n")
                f.write(f"**Formato:** Markdown  \n")
                f.write(f"**Total de páginas:** {len(content_dict)}\n\n")
                f.write("---\n\n")
                
                # Listar páginas com sucesso
                successful_pages = [(title, content) for title, content in content_dict.items() 
                                   if isinstance(content, dict) and content.get('markdown')]
                
                if successful_pages:
                    f.write("## ✅ Páginas Extraídas com Sucesso\n\n")
                    for i, (title, content) in enumerate(successful_pages, 1):
                        filename = self._sanitize_filename(title) + ".md"
                        f.write(f"{i}. **[{title}](./{filename})**\n")
                    f.write("\n")
                
                # Listar páginas com erro
                failed_pages = [(title, content) for title, content in content_dict.items() 
                               if not (isinstance(content, dict) and content.get('markdown'))]
                
                if failed_pages:
                    f.write("## ❌ Páginas com Erro\n\n")
                    for i, (title, content) in enumerate(failed_pages, 1):
                        error_msg = content if isinstance(content, str) else "Erro desconhecido"
                        f.write(f"{i}. **{title}** - *{error_msg}*\n")
                    f.write("\n")
                
                f.write("---\n\n")
                f.write("*Gerado automaticamente pelo MediaWiki to BookStack Converter*\n")
                
        except Exception as e:
            self.log_message(f"ERRO ao criar índice Markdown: {str(e)}")
    
    def extract_txt_content(self):
        """Extrai conteúdo das páginas selecionadas e salva como arquivos TXT"""
        if not self.client or not self.page_checkboxes:
            self.log_message("ERRO: Carregue as páginas primeiro")
            self.update_status("Carregue as páginas primeiro", "red")
            return
        
        selected_pages = self.get_selected_pages()
        if not selected_pages:
            self.log_message("ERRO: Nenhuma página selecionada")
            self.update_status("Nenhuma página selecionada", "red")
            return
            
        self.extract_txt_btn.configure(state="disabled")
        self.update_status("Extraindo páginas como TXT...", "yellow")
        self.content_textbox.delete("1.0", "end")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._extract_txt_worker, args=(selected_pages,), daemon=True).start()
    
    def _extract_txt_worker(self, selected_pages):
        """Worker thread para extrair conteúdo como TXT"""
        try:
            page_titles = [page['title'] for page in selected_pages]
            page_ids = [page['pageid'] for page in selected_pages]
            total_pages = len(page_titles)
            processed = 0
            
            self.log_message(f"Iniciando extração TXT de {total_pages} páginas selecionadas...")
            
            def progress_callback(current_total, batch_size):
                nonlocal processed
                processed = current_total
                progress = processed / total_pages if total_pages > 0 else 0
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.progress_label.configure(text=f"Extraindo TXT: {processed}/{total_pages}"))
            
            # Extrair conteúdo em formato Wikitext (que funciona)
            expand_templates = self.expand_templates_var.get()
            contents = self.client.get_page_content_batch(
                page_titles, 
                callback=progress_callback, 
                format_type='wikitext',  # Usar wikitext que sabemos que funciona
                expand_templates=expand_templates
            )
            
            # Processar resultados e salvar como TXT
            successful = 0
            failed = 0
            txt_content = {}
            failed_details = []
            
            for i, (title, content) in enumerate(contents.items()):
                page_id = page_ids[i] if i < len(page_ids) else None
                
                # Aceitar qualquer conteúdo de texto (seja dict, string, etc.)
                text_content = ""
                if isinstance(content, dict):
                    # Se é dict, pode ter wikitext, markdown, ou outro campo
                    text_content = content.get('wikitext', '') or content.get('markdown', '') or content.get('content', '') or str(content)
                elif isinstance(content, str):
                    # Se é string direta, usar como está
                    text_content = content
                else:
                    # Qualquer outro tipo, converter para string
                    text_content = str(content)
                
                if text_content and text_content.strip():
                    # Sucesso - qualquer conteúdo não vazio
                    successful += 1
                    txt_content[title] = text_content
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 1)  # Marcar como processada
                else:
                    # Falha - conteúdo vazio
                    failed += 1
                    error_msg = "Conteúdo vazio"
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 0, error_msg)
                    failed_details.append(f"❌ {title}: {error_msg}")
            
            # Salvar cache atualizado
            self.pages_cache.save_cache()
            
            # Salvar arquivos TXT automaticamente
            if successful > 0:
                self._save_txt_files(txt_content)
            
            # Preparar relatório
            stats = self.pages_cache.get_statistics()
            
            summary = [
                f"=== EXTRAÇÃO TXT CONCLUÍDA ===",
                f"Páginas selecionadas: {total_pages}",
                f"Extraídas com sucesso: {successful}",
                f"Falharam: {failed}",
                f"",
                f"=== PROGRESSO GERAL ===",
                f"Total no cache: {stats['total_pages']:,}",
                f"Processadas: {stats['processed_pages']:,}",
                f"Pendentes: {stats['pending_pages']:,}",
                f"Progresso: {stats['progress_percentage']:.1f}%",
                ""
            ]
            
            # Adicionar detalhes de falhas se houver
            if failed_details:
                summary.append("=== PÁGINAS COM ERRO ===")
                summary.extend(failed_details[:10])  # Mostrar até 10 erros
                if len(failed_details) > 10:
                    summary.append(f"... e mais {len(failed_details) - 10} erros")
                summary.append("")
            
            if successful > 0:
                summary.append("✅ Páginas processadas foram marcadas como concluídas no cache")
                summary.append(f"📄 {successful} arquivos TXT salvos automaticamente")
            
            result_text = "\n".join(summary)
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", result_text))
            
            # Status final
            status_msg = f"TXT: {successful}/{total_pages} | Cache: {stats['progress_percentage']:.1f}%"
            status_color = "green" if failed == 0 else "orange"
            self.root.after(0, lambda: self.update_status(status_msg, status_color))
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            
            # Log
            self.log_message(f"Extração TXT completa: {successful}/{total_pages} páginas. Progresso geral: {stats['progress_percentage']:.1f}%")
            
            # Atualizar lista de páginas (mostrar páginas pendentes restantes)
            self.root.after(0, self._create_cached_page_checkboxes)
            
        except Exception as e:
            error_msg = f"ERRO na extração TXT: {str(e)}"
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
            self.root.after(0, lambda: self.update_status("Erro na extração TXT", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.extract_txt_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
    
    def _save_txt_files(self, txt_content):
        """Salva automaticamente os arquivos TXT extraídos"""
        try:
            # Criar diretório para os arquivos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"extracted_txt_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            saved_count = 0
            
            # Salvar cada página como arquivo TXT
            for title, content in txt_content.items():
                # Sanitizar nome do arquivo
                filename = self._sanitize_filename(title) + ".txt"
                filepath = os.path.join(output_dir, filename)
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        # Escrever cabeçalho
                        f.write(f"TÍTULO: {title}\n")
                        f.write(f"FONTE: MediaWiki\n")
                        f.write(f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                        f.write(f"FORMATO: TXT\n")
                        f.write("=" * 50 + "\n\n")
                        
                        # Escrever conteúdo
                        f.write(content)
                        
                    saved_count += 1
                    
                except Exception as e:
                    self.log_message(f"ERRO ao salvar {filename}: {str(e)}")
            
            # Criar arquivo de índice
            index_path = os.path.join(output_dir, "INDICE.txt")
            self._create_txt_index(index_path, txt_content)
            
            self.log_message(f"✅ {saved_count} arquivos TXT salvos em: {output_dir}")
            
        except Exception as e:
            self.log_message(f"ERRO ao salvar arquivos TXT: {str(e)}")
    
    def _create_txt_index(self, index_path, content_dict):
        """Cria arquivo de índice para os arquivos TXT"""
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("ÍNDICE DE PÁGINAS EXTRAÍDAS - TXT\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Data de extração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Formato: TXT\n")
                f.write(f"Total de páginas: {len(content_dict)}\n\n")
                f.write("-" * 40 + "\n\n")
                
                # Listar páginas extraídas
                f.write("PÁGINAS EXTRAÍDAS:\n\n")
                for i, title in enumerate(content_dict.keys(), 1):
                    filename = self._sanitize_filename(title) + ".txt"
                    f.write(f"{i:3d}. {title}\n")
                    f.write(f"     Arquivo: {filename}\n\n")
                
                f.write("-" * 40 + "\n")
                f.write("Gerado automaticamente pelo MediaWiki to BookStack Converter\n")
                
        except Exception as e:
            self.log_message(f"ERRO ao criar índice TXT: {str(e)}")

    def extract_txt_with_images(self):
        """Extrai conteúdo das páginas selecionadas como TXT e baixa suas imagens"""
        if not self.client or not self.page_checkboxes:
            self.log_message("ERRO: Carregue as páginas primeiro")
            self.update_status("Carregue as páginas primeiro", "red")
            return
        
        selected_pages = self.get_selected_pages()
        if not selected_pages:
            self.log_message("ERRO: Nenhuma página selecionada")
            self.update_status("Nenhuma página selecionada", "red")
            return
            
        self.extract_txt_images_btn.configure(state="disabled")
        self.update_status("Extraindo TXT + Imagens...", "yellow")
        self.content_textbox.delete("1.0", "end")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._extract_txt_images_worker, args=(selected_pages,), daemon=True).start()
    
    def _extract_txt_images_worker(self, selected_pages):
        """Worker thread para extrair conteúdo TXT e baixar imagens"""
        try:
            page_titles = [page['title'] for page in selected_pages]
            page_ids = [page['pageid'] for page in selected_pages]
            total_pages = len(page_titles)
            processed = 0
            
            self.log_message(f"Iniciando extração TXT + Imagens de {total_pages} páginas selecionadas...")
            
            # Criar diretório com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"extracted_txt_images_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Inicializar downloader de imagens
            image_downloader = MediaWikiImageDownloader(self.client)
            
            def progress_callback(current_total, batch_size):
                nonlocal processed
                processed = current_total
                progress = processed / (total_pages * 2) if total_pages > 0 else 0  # *2 porque temos texto + imagens
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.progress_label.configure(text=f"Extraindo: {processed}/{total_pages}"))
            
            # FASE 1: Extrair conteúdo de texto
            self.log_message("📝 Fase 1: Extraindo conteúdo de texto...")
            expand_templates = self.expand_templates_var.get()
            
            # Obter tanto wikitext quanto HTML para ter máxima cobertura de imagens
            wikitext_contents = self.client.get_page_content_batch(
                page_titles, 
                callback=progress_callback, 
                format_type='wikitext',
                expand_templates=expand_templates
            )
            
            # Processar resultados de texto
            successful_txt = 0
            failed_txt = 0
            txt_content = {}
            page_full_content = {}  # Para usar no download de imagens
            
            for i, (title, content) in enumerate(wikitext_contents.items()):
                page_id = page_ids[i] if i < len(page_ids) else None
                
                # Extrair texto como na função original
                text_content = ""
                if isinstance(content, dict):
                    text_content = content.get('wikitext', '') or content.get('markdown', '') or content.get('content', '') or str(content)
                    page_full_content[title] = content  # Salvar conteúdo completo
                elif isinstance(content, str):
                    text_content = content
                    page_full_content[title] = {'wikitext': content}
                else:
                    text_content = str(content)
                    page_full_content[title] = {'wikitext': text_content}
                
                if text_content and text_content.strip():
                    successful_txt += 1
                    txt_content[title] = text_content
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 1)
                else:
                    failed_txt += 1
                    if page_id:
                        self.pages_cache.update_page_status(page_id, 0, "Conteúdo vazio")
            
            # Salvar arquivos TXT
            if successful_txt > 0:
                self.log_message(f"💾 Salvando {successful_txt} arquivos TXT...")
                for title, content in txt_content.items():
                    filename = self._sanitize_filename(title) + ".txt"
                    filepath = os.path.join(output_dir, filename)
                    
                    try:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(f"TÍTULO: {title}\n")
                            f.write(f"FONTE: MediaWiki\n")
                            f.write(f"DATA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                            f.write(f"FORMATO: TXT + Imagens\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(content)
                    except Exception as e:
                        self.log_message(f"ERRO ao salvar {filename}: {str(e)}")
            
            # FASE 2: Baixar imagens
            self.log_message("🖼️ Fase 2: Baixando imagens das páginas...")
            
            total_images_found = 0
            total_images_downloaded = 0
            total_images_failed = 0
            image_stats_by_page = {}
            
            for i, (title, full_content) in enumerate(page_full_content.items()):
                # Atualizar progresso
                progress = (total_pages + i + 1) / (total_pages * 2)
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                self.root.after(0, lambda t=title: self.progress_label.configure(text=f"Baixando imagens: {t[:30]}..."))
                
                # Tentar obter também HTML para cobertura completa
                try:
                    html_content = self.client.get_page_content_html(title)
                    if html_content and 'html' in html_content:
                        full_content['html'] = html_content['html']
                except:
                    pass  # HTML opcional
                
                # Baixar imagens da página
                stats = image_downloader.download_page_images(title, full_content, output_dir)
                image_stats_by_page[title] = stats
                
                total_images_found += stats['total_found']
                total_images_downloaded += stats['downloaded']
                total_images_failed += stats['failed']
            
            # Salvar cache atualizado
            self.pages_cache.save_cache()
            
            # Criar relatório completo
            self._create_txt_images_index(output_dir, txt_content, image_stats_by_page)
            
            # Preparar relatório final
            cache_stats = self.pages_cache.get_statistics()
            
            summary = [
                f"=== EXTRAÇÃO TXT + IMAGENS CONCLUÍDA ===",
                f"Páginas selecionadas: {total_pages}",
                f"Texto extraído: {successful_txt}",
                f"Falhas texto: {failed_txt}",
                f"",
                f"=== IMAGENS ===",
                f"Imagens encontradas: {total_images_found}",
                f"Imagens baixadas: {total_images_downloaded}",
                f"Falhas download: {total_images_failed}",
                f"",
                f"=== PROGRESSO GERAL ===",
                f"Total no cache: {cache_stats['total_pages']:,}",
                f"Processadas: {cache_stats['processed_pages']:,}",
                f"Pendentes: {cache_stats['pending_pages']:,}",
                f"Progresso: {cache_stats['progress_percentage']:.1f}%",
                f"",
                f"✅ Arquivos salvos em: {output_dir}",
                f"📄 {successful_txt} arquivos TXT",
                f"🖼️ {total_images_downloaded} imagens",
                f"📋 Veja RELATORIO_COMPLETO.txt para detalhes"
            ]
            
            result_text = "\n".join(summary)
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", result_text))
            
            # Status final
            status_msg = f"TXT+IMG: {successful_txt}p/{total_images_downloaded}i | Cache: {cache_stats['progress_percentage']:.1f}%"
            status_color = "green" if failed_txt == 0 and total_images_failed == 0 else "orange"
            self.root.after(0, lambda: self.update_status(status_msg, status_color))
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            
            # Log
            self.log_message(f"Extração TXT+Imagens completa: {successful_txt}/{total_pages} páginas, {total_images_downloaded} imagens")
            
            # Atualizar lista de páginas
            self.root.after(0, self._create_cached_page_checkboxes)
            
        except Exception as e:
            error_msg = f"ERRO na extração TXT+Imagens: {str(e)}"
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
            self.root.after(0, lambda: self.update_status("Erro na extração TXT+Imagens", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.extract_txt_images_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
    
    def _create_txt_images_index(self, output_dir, txt_content, image_stats):
        """Cria relatório completo da extração TXT + Imagens"""
        try:
            report_path = os.path.join(output_dir, "RELATORIO_COMPLETO.txt")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("RELATÓRIO COMPLETO - EXTRAÇÃO TXT + IMAGENS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Data de extração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Diretório: {output_dir}\n")
                f.write(f"Total de páginas: {len(txt_content)}\n\n")
                
                # Estatísticas gerais de imagens
                total_found = sum(stats['total_found'] for stats in image_stats.values())
                total_downloaded = sum(stats['downloaded'] for stats in image_stats.values())
                total_failed = sum(stats['failed'] for stats in image_stats.values())
                total_skipped = sum(stats['skipped'] for stats in image_stats.values())
                
                f.write("RESUMO DE IMAGENS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Imagens encontradas: {total_found}\n")
                f.write(f"Imagens baixadas: {total_downloaded}\n")
                f.write(f"Imagens que falharam: {total_failed}\n")
                f.write(f"Imagens puladas: {total_skipped}\n")
                f.write(f"Taxa de sucesso: {(total_downloaded / total_found * 100) if total_found > 0 else 0:.1f}%\n\n")
                
                # Detalhes por página
                f.write("DETALHES POR PÁGINA:\n")
                f.write("=" * 30 + "\n\n")
                
                for i, (title, stats) in enumerate(image_stats.items(), 1):
                    filename = self._sanitize_filename(title) + ".txt"
                    f.write(f"{i:3d}. {title}\n")
                    f.write(f"     Arquivo TXT: {filename}\n")
                    f.write(f"     Imagens encontradas: {stats['total_found']}\n")
                    f.write(f"     Imagens baixadas: {stats['downloaded']}\n")
                    
                    if stats['failed'] > 0:
                        f.write(f"     Falhas: {stats['failed']}\n")
                    
                    if stats['image_files']:
                        f.write(f"     Arquivos: {', '.join(stats['image_files'][:3])}")
                        if len(stats['image_files']) > 3:
                            f.write(f" (e mais {len(stats['image_files']) - 3})")
                        f.write("\n")
                    
                    f.write("\n")
                
                # Estrutura de diretórios
                f.write("ESTRUTURA DE ARQUIVOS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"{output_dir}/\n")
                f.write("├── RELATORIO_COMPLETO.txt (este arquivo)\n")
                f.write("├── INDICE.txt (índice dos arquivos TXT)\n")
                
                for title in txt_content.keys():
                    filename = self._sanitize_filename(title) + ".txt"
                    f.write(f"├── {filename}\n")
                
                f.write("└── images/\n")
                for title in image_stats.keys():
                    if image_stats[title]['image_files']:
                        safe_title = self._sanitize_filename(title)
                        f.write(f"    └── {safe_title}/\n")
                        for img_file in image_stats[title]['image_files'][:2]:
                            f.write(f"        ├── {img_file}\n")
                        if len(image_stats[title]['image_files']) > 2:
                            f.write(f"        └── ... (e mais {len(image_stats[title]['image_files']) - 2} arquivos)\n")
                
                f.write("\n" + "-" * 50 + "\n")
                f.write("Gerado automaticamente pelo MediaWiki to BookStack Converter\n")
                
            # Criar também o índice TXT padrão
            index_path = os.path.join(output_dir, "INDICE.txt")
            self._create_txt_index(index_path, txt_content)
            
            self.log_message(f"📋 Relatório completo salvo em: {report_path}")
            
        except Exception as e:
            self.log_message(f"ERRO ao criar relatório completo: {str(e)}")

    def list_all_pages(self):
        """Método legado - redireciona para refresh_pages_from_api"""
        self.log_message("Redirecionando para atualização do cache...")
        self.refresh_pages_from_api()
        
    def extract_all_content(self):
        """Método legado - redireciona para extract_pending_content"""
        self.log_message("Redirecionando para extração de páginas pendentes...")
        self.extract_pending_content()
    
    def select_all_pages(self):
        """Seleciona todas as páginas pendentes"""
        for checkbox in self.page_checkboxes:
            checkbox.var.set(True)
        self.update_selected_count()
    
    def deselect_all_pages(self):
        """Deseleciona todas as páginas pendentes"""
        for checkbox in self.page_checkboxes:
            checkbox.var.set(False)
        self.update_selected_count()
    
    def update_selected_count(self):
        """Atualiza o contador de páginas selecionadas com informações de navegação"""
        # Otimização: usar contador direto ao invés de sum() com generator
        selected_count = 0
        for checkbox in self.page_checkboxes:
            if checkbox.var.get():
                selected_count += 1
        
        total_displayed = len(self.page_checkboxes)
        
        # Obter estatísticas do cache
        all_pending_pages = self._get_filtered_pages()
        total_pending = len(all_pending_pages)
        
        # Informações de navegação
        if hasattr(self, 'current_page'):
            current_page_num = self.current_page + 1
            total_pages = max(1, (total_pending + 50 - 1) // 50)  # 50 páginas fixas por página
            
            # Texto detalhado com navegação
            if total_pending > total_displayed:
                self.selected_count_label.configure(
                    text=f"✅ {selected_count}/{total_displayed} selecionadas | Página {current_page_num}/{total_pages} | Total pendentes: {total_pending}"
                )
            else:
                self.selected_count_label.configure(
                    text=f"✅ {selected_count}/{total_displayed} selecionadas | Total pendentes: {total_pending}"
                )
        else:
            # Fallback para modo legado
            self.selected_count_label.configure(
                text=f"✅ {selected_count}/{total_displayed} selecionadas | Total pendentes: {total_pending}"
            )
    
    def get_selected_pages(self):
        """Retorna lista de páginas selecionadas"""
        selected_pages = []
        for checkbox in self.page_checkboxes:
            if checkbox.var.get():
                selected_pages.append(checkbox.page_data)
        return selected_pages

    def save_extracted_files(self):
        """Salva as páginas extraídas em arquivos HTML"""
        if not self.extracted_content:
            self.log_message("ERRO: Nenhum conteúdo para salvar")
            return
        
        self.save_files_btn.configure(state="disabled")
        threading.Thread(target=self._save_files_worker, daemon=True).start()
    
    def _save_files_worker(self):
        """Worker thread para salvar arquivos em Markdown"""
        try:
            # Criar diretório para os arquivos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"exported_markdown_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            self.log_message(f"Salvando arquivos Markdown em: {output_dir}")
            
            saved_count = 0
            skipped_count = 0
            total_files = len([c for c in self.extracted_content.values() 
                             if isinstance(c, dict) and c.get('markdown')])
            
            # Criar arquivo de log de erros
            error_log_path = os.path.join(output_dir, "extraction_errors.log")
            with open(error_log_path, 'w', encoding='utf-8') as error_log:
                error_log.write(f"Log de Erros da Extração - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                error_log.write("=" * 60 + "\n\n")
                
                for title, content in self.extracted_content.items():
                    if isinstance(content, dict) and content.get('markdown'):
                        try:
                            # Criar nome de arquivo seguro
                            safe_filename = self._sanitize_filename(title)
                            filepath = os.path.join(output_dir, f"{safe_filename}.md")
                            
                            # Usar o markdown já processado
                            markdown_content = content.get('markdown', '')
                            
                            # Salvar arquivo
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(markdown_content)
                            
                            saved_count += 1
                            progress = saved_count / total_files if total_files > 0 else 1
                            self.root.after(0, lambda: self.progress_bar.set(progress))
                            self.root.after(0, lambda: self.progress_label.configure(
                                text=f"Salvando: {saved_count}/{total_files}"))
                            
                        except Exception as e:
                            self.log_message(f"ERRO ao salvar '{title}': {str(e)}")
                    else:
                        # Registrar páginas que falharam na extração
                        skipped_count += 1
                        error_msg = content if isinstance(content, str) else "Erro desconhecido"
                        error_log.write(f"PÁGINA: {title}\n")
                        error_log.write(f"ERRO: {error_msg}\n")
                        error_log.write("-" * 40 + "\n\n")
            
            # Criar arquivo de índice
            index_path = os.path.join(output_dir, "README.md")
            self._create_markdown_index(index_path, self.extracted_content)
            
            # Criar relatório de estatísticas
            stats_path = os.path.join(output_dir, "extraction_stats.md")
            self._create_extraction_stats(stats_path, self.extracted_content)
            
            final_msg = f"Arquivos salvos: {saved_count}/{total_files}"
            if skipped_count > 0:
                final_msg += f" ({skipped_count} páginas com erro)"
            
            self.root.after(0, lambda: self.update_status(final_msg, "green"))
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            
            self.log_message(f"Salvamento completo: {saved_count} arquivos Markdown salvos em '{output_dir}'")
            if skipped_count > 0:
                self.log_message(f"Páginas com erro registradas em 'extraction_errors.log'")
            
        except Exception as e:
            error_msg = f"ERRO ao salvar arquivos: {str(e)}"
            self.root.after(0, lambda: self.update_status("Erro ao salvar", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.save_files_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))

    def _create_extraction_stats(self, stats_path, content_dict):
        """Cria relatório de estatísticas da extração"""
        successful_pages = [(title, content) for title, content in content_dict.items() 
                           if isinstance(content, dict) and content.get('markdown')]
        
        failed_pages = [(title, content) for title, content in content_dict.items() 
                       if not (isinstance(content, dict) and content.get('markdown'))]
        
        # Categorizar tipos de erro
        permission_errors = []
        not_found_errors = []
        other_errors = []
        
        for title, content in failed_pages:
            if isinstance(content, str) and content.startswith("ERRO:"):
                error_msg = content[6:]
                if "403" in error_msg or "Forbidden" in error_msg:
                    permission_errors.append((title, error_msg))
                elif "404" in error_msg or "not found" in error_msg.lower():
                    not_found_errors.append((title, error_msg))
                else:
                    other_errors.append((title, error_msg))
            else:
                other_errors.append((title, "Erro desconhecido"))
        
        # Create the content parts separately to avoid backslash in f-string
        permission_list = ''.join([f'- `{title}`: {error}\n' for title, error in permission_errors[:20]])
        permission_more = f'*... e mais {len(permission_errors) - 20} páginas*\n' if len(permission_errors) > 20 else ''
        
        not_found_list = ''.join([f'- `{title}`: {error}\n' for title, error in not_found_errors[:10]])
        not_found_more = f'*... e mais {len(not_found_errors) - 10} páginas*\n' if len(not_found_errors) > 10 else ''
        
        other_list = ''.join([f'- `{title}`: {error}\n' for title, error in other_errors[:10]])
        other_more = f'*... e mais {len(other_errors) - 10} páginas*\n' if len(other_errors) > 10 else ''
        
        stats_md = f"""# Relatório de Extração - MediaWiki to BookStack

    **Data da extração:** {datetime.now().strftime("%d/%m/%Y às %H:%M")}

    ## Resumo Geral

    | Métrica | Valor |
    |---------|-------|
    | Total de páginas processadas | {len(content_dict)} |
    | Páginas extraídas com sucesso | {len(successful_pages)} |
    | Páginas com erro | {len(failed_pages)} |
    | Taxa de sucesso | {(len(successful_pages) / len(content_dict) * 100):.1f}% |

    ## Detalhamento dos Erros

    ### 🔒 Erros de Permissão (403 Forbidden)
    **Total:** {len(permission_errors)} páginas

    {permission_list}{permission_more}

    ### ❌ Páginas Não Encontradas (404)
    **Total:** {len(not_found_errors)} páginas

    {not_found_list}{not_found_more}

    ### ⚠️ Outros Erros
    **Total:** {len(other_errors)} páginas

    {other_list}{other_more}

    ## Recomendações

    ### Para Erros de Permissão (403):
    - Verifique se o usuário tem as permissões necessárias
    - Solicite acesso ao administrador da wiki
    - Considere usar uma conta com privilégios administrativos

    ### Para Páginas Não Encontradas (404):
    - Verifique se as páginas ainda existem na wiki
    - Confirme se os títulos estão corretos
    - Algumas páginas podem ter sido movidas ou deletadas

    ### Para Outros Erros:
    - Verifique a conectividade com a wiki
    - Confirme se a API está funcionando corretamente
    - Tente extrair novamente após algum tempo

    ---

    *Relatório gerado automaticamente pelo MediaWiki to BookStack Exporter*
    """
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            f.write(stats_md)

    def _sanitize_filename(self, filename):
        """Cria um nome de arquivo seguro removendo caracteres inválidos"""
        import re
        import unicodedata
        
        # Normalizar unicode
        filename = unicodedata.normalize('NFKD', filename)
        
        # Remover caracteres inválidos para nomes de arquivo
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(invalid_chars, '_', filename)
        
        # Substituir múltiplos espaços/underscores por um único
        filename = re.sub(r'[_\s]+', '_', filename)
        
        # Remover underscores do início e fim
        filename = filename.strip('_')
        
        # Limitar tamanho (muitos sistemas têm limite de 255 caracteres)
        max_length = 200  # Deixar espaço para extensão
        if len(filename) > max_length:
            filename = filename[:max_length].rstrip('_')
        
        # Se ficou vazio, usar nome padrão
        if not filename:
            filename = "pagina_sem_nome"
        
        return filename
    
    def _create_markdown_index(self, index_path, content_dict):
        """Cria arquivo de índice das páginas extraídas"""
        successful_pages = [(title, content) for title, content in content_dict.items() 
                           if isinstance(content, dict) and content.get('markdown')]
        
        failed_pages = [(title, content) for title, content in content_dict.items() 
                       if not (isinstance(content, dict) and content.get('markdown'))]
        
        # Ordenar páginas por título
        successful_pages.sort(key=lambda x: x[0])
        failed_pages.sort(key=lambda x: x[0])
        
        index_md = f"""# Índice das Páginas Extraídas

**Data da extração:** {datetime.now().strftime("%d/%m/%Y às %H:%M")}  
**Total de páginas:** {len(content_dict)}  
**Extraídas com sucesso:** {len(successful_pages)}  
**Com erro:** {len(failed_pages)}  

---

## 📄 Páginas Extraídas com Sucesso

"""
        
        if successful_pages:
            for title, content in successful_pages:
                safe_filename = self._sanitize_filename(title)
                markdown_size = len(content.get('markdown', ''))
                categories = content.get('categories', [])
                
                index_md += f"### [{title}]({safe_filename}.md)\n\n"
                index_md += f"- **Arquivo:** `{safe_filename}.md`\n"
                index_md += f"- **Tamanho:** {markdown_size:,} caracteres\n"
                index_md += f"- **ID da página:** {content.get('pageid', 'N/A')}\n"
                
                if categories:
                    index_md += f"- **Categorias:** {', '.join(categories)}\n"
                
                index_md += "\n"
        else:
            index_md += "*Nenhuma página foi extraída com sucesso.*\n\n"
        
        # Adicionar seção de erros se houver
        if failed_pages:
            index_md += "---\n\n## ❌ Páginas com Erro\n\n"
            
            for title, content in failed_pages[:20]:  # Mostrar até 20 erros
                error_msg = content if isinstance(content, str) else "Erro desconhecido"
                index_md += f"- **{title}**: {error_msg}\n"
            
            if len(failed_pages) > 20:
                index_md += f"\n*... e mais {len(failed_pages) - 20} páginas com erro (veja extraction_stats.md para detalhes)*\n"
        
        index_md += f"""

---

## 📊 Estatísticas Rápidas

| Métrica | Valor |
|---------|-------|
| Taxa de sucesso | {(len(successful_pages) / len(content_dict) * 100):.1f}% |
| Páginas por categoria | Varia |
| Tamanho médio | {(sum(len(content.get('markdown', '')) for _, content in successful_pages) / len(successful_pages) if successful_pages else 0):,.0f} caracteres |

## 📁 Arquivos Gerados

- `README.md` - Este arquivo de índice
- `extraction_stats.md` - Relatório detalhado de estatísticas  
- `extraction_errors.log` - Log detalhado de erros
- `*.md` - Arquivos das páginas extraídas

---

*Índice gerado automaticamente pelo MediaWiki to BookStack Exporter*
"""
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_md)

    def open_config_window(self):
        """Abre a janela de configurações"""
        # Se a janela já existe e está aberta, apenas foca nela
        if self.config_window and self.config_window.winfo_exists():
            self.config_window.focus()
            return
        
        # Criar nova janela de configurações
        self.config_window = ctk.CTkToplevel(self.root)
        self.config_window.title("Configurações Avançadas")
        self.config_window.geometry("600x800")  # Aumentei a altura de 600 para 800
        self.config_window.resizable(True, True)
        
        # Centralizar janela
        self.config_window.transient(self.root)
        self.config_window.grab_set()
        
        # Criar conteúdo da janela
        self.create_config_window_content()
        
    def create_config_window_content(self):
        """Cria o conteúdo da janela de configurações"""
        # Frame scrollable principal
        scrollable_frame = ctk.CTkScrollableFrame(self.config_window)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(scrollable_frame, text="Configurações Avançadas", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Seção de Conexão
        connection_frame = ctk.CTkFrame(scrollable_frame)
        connection_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(connection_frame, text="🔗 Configurações de Conexão", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Timeout de conexão
        timeout_frame = ctk.CTkFrame(connection_frame)
        timeout_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(timeout_frame, text="Timeout de conexão (segundos):").pack(anchor="w", padx=10, pady=(10, 0))
        self.timeout_var = ctk.StringVar(value="30")
        self.timeout_entry = ctk.CTkEntry(timeout_frame, textvariable=self.timeout_var, width=100)
        self.timeout_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Retries
        retry_frame = ctk.CTkFrame(connection_frame)
        retry_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(retry_frame, text="Número de tentativas:").pack(anchor="w", padx=10, pady=(10, 0))
        self.retry_var = ctk.StringVar(value="3")
        self.retry_entry = ctk.CTkEntry(retry_frame, textvariable=self.retry_var, width=100)
        self.retry_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Seção de Extração
        extraction_frame = ctk.CTkFrame(scrollable_frame)
        extraction_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(extraction_frame, text="📄 Configurações de Extração", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tamanho do lote
        batch_frame = ctk.CTkFrame(extraction_frame)
        batch_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(batch_frame, text="Tamanho do lote de páginas:").pack(anchor="w", padx=10, pady=(10, 0))
        self.batch_size_var = ctk.StringVar(value="10")
        self.batch_size_entry = ctk.CTkEntry(batch_frame, textvariable=self.batch_size_var, width=100)
        self.batch_size_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Delay entre requisições
        delay_frame = ctk.CTkFrame(extraction_frame)
        delay_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(delay_frame, text="Delay entre lotes (segundos):").pack(anchor="w", padx=10, pady=(10, 0))
        self.delay_var = ctk.StringVar(value="1")
        self.delay_entry = ctk.CTkEntry(delay_frame, textvariable=self.delay_var, width=100)
        self.delay_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Opções de processamento
        processing_options_frame = ctk.CTkFrame(extraction_frame)
        processing_options_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Limpar wikitext
        self.clean_wikitext_var = ctk.BooleanVar(value=True)
        self.clean_wikitext_checkbox = ctk.CTkCheckBox(processing_options_frame, 
                                                       text="Limpar wikitext automaticamente", 
                                                       variable=self.clean_wikitext_var)
        self.clean_wikitext_checkbox.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Incluir metadados
        self.include_metadata_var = ctk.BooleanVar(value=True)
        self.include_metadata_checkbox = ctk.CTkCheckBox(processing_options_frame, 
                                                         text="Incluir metadados nas exportações", 
                                                         variable=self.include_metadata_var)
        self.include_metadata_checkbox.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Log detalhado
        self.verbose_logging_var = ctk.BooleanVar(value=False)
        self.verbose_logging_checkbox = ctk.CTkCheckBox(processing_options_frame, 
                                                        text="Log detalhado (debug)", 
                                                        variable=self.verbose_logging_var)
        self.verbose_logging_checkbox.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Seção de Cache
        cache_frame = ctk.CTkFrame(scrollable_frame)
        cache_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(cache_frame, text="💾 Configurações de Cache", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Auto-salvar cache
        self.auto_save_cache_var = ctk.BooleanVar(value=True)
        self.auto_save_cache_checkbox = ctk.CTkCheckBox(cache_frame, 
                                                        text="Auto-salvar cache após atualizações", 
                                                        variable=self.auto_save_cache_var)
        self.auto_save_cache_checkbox.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Backup do cache
        self.backup_cache_var = ctk.BooleanVar(value=False)
        self.backup_cache_checkbox = ctk.CTkCheckBox(cache_frame, 
                                                     text="Criar backup do cache antes de atualizar", 
                                                     variable=self.backup_cache_var)
        self.backup_cache_checkbox.pack(anchor="w", padx=15, pady=(0, 15))
        
        # 🆕 Seção BookStack
        bookstack_frame = ctk.CTkFrame(scrollable_frame)
        bookstack_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(bookstack_frame, text="📚 Configurações BookStack", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # URL Base do BookStack
        bookstack_url_frame = ctk.CTkFrame(bookstack_frame)
        bookstack_url_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(bookstack_url_frame, text="URL Base do BookStack:").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(bookstack_url_frame, text="(ex: https://bookstack.empresa.com)", 
                    font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 5))
        self.bookstack_url_var = ctk.StringVar(value="")
        self.bookstack_url_entry = ctk.CTkEntry(bookstack_url_frame, textvariable=self.bookstack_url_var, 
                                               width=350, placeholder_text="https://bookstack.empresa.com")
        self.bookstack_url_entry.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Token ID
        bookstack_token_id_frame = ctk.CTkFrame(bookstack_frame)
        bookstack_token_id_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(bookstack_token_id_frame, text="Token ID da API:").pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(bookstack_token_id_frame, text="(obtenha em: Configurações > API Tokens)", 
                    font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=10, pady=(0, 5))
        self.bookstack_token_id_var = ctk.StringVar(value="")
        self.bookstack_token_id_entry = ctk.CTkEntry(bookstack_token_id_frame, textvariable=self.bookstack_token_id_var, 
                                                    width=350, placeholder_text="Digite o Token ID")
        self.bookstack_token_id_entry.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Token Secret
        bookstack_token_secret_frame = ctk.CTkFrame(bookstack_frame)
        bookstack_token_secret_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(bookstack_token_secret_frame, text="Token Secret da API:").pack(anchor="w", padx=10, pady=(10, 0))
        self.bookstack_token_secret_var = ctk.StringVar(value="")
        self.bookstack_token_secret_entry = ctk.CTkEntry(bookstack_token_secret_frame, 
                                                        textvariable=self.bookstack_token_secret_var,
                                                        width=350, show="*", 
                                                        placeholder_text="Digite o Token Secret")
        self.bookstack_token_secret_entry.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Opções BookStack
        bookstack_options_frame = ctk.CTkFrame(bookstack_frame)
        bookstack_options_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Verificar SSL do BookStack
        self.bookstack_verify_ssl_var = ctk.BooleanVar(value=True)
        self.bookstack_verify_ssl_checkbox = ctk.CTkCheckBox(bookstack_options_frame, 
                                                            text="Verificar certificados SSL do BookStack", 
                                                            variable=self.bookstack_verify_ssl_var)
        self.bookstack_verify_ssl_checkbox.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Botão Testar Conexão BookStack
        bookstack_test_frame = ctk.CTkFrame(bookstack_frame)
        bookstack_test_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.test_bookstack_btn = ctk.CTkButton(bookstack_test_frame, 
                                               text="🔗 Testar Conexão BookStack", 
                                               command=self.test_bookstack_connection,
                                               fg_color="#2E8B57", hover_color="#228B22")
        self.test_bookstack_btn.pack(padx=10, pady=10)
        
        # Status da conexão BookStack
        self.bookstack_status_label = ctk.CTkLabel(bookstack_test_frame, text="", 
                                                  font=ctk.CTkFont(size=11))
        self.bookstack_status_label.pack(padx=10, pady=(0, 10))
        
        # Seção de Interface
        ui_frame = ctk.CTkFrame(scrollable_frame)
        ui_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(ui_frame, text="🎨 Configurações de Interface", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tema
        theme_frame = ctk.CTkFrame(ui_frame)
        theme_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(theme_frame, text="Tema da interface:").pack(anchor="w", padx=10, pady=(10, 5))
        self.theme_var = ctk.StringVar(value="dark")
        self.theme_menu = ctk.CTkOptionMenu(theme_frame, values=["dark", "light", "system"], 
                                           variable=self.theme_var, command=self.change_theme)
        self.theme_menu.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Máximo de páginas para exibir
        max_pages_frame = ctk.CTkFrame(ui_frame)
        max_pages_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(max_pages_frame, text="Máximo de páginas para exibir:").pack(anchor="w", padx=10, pady=(10, 0))
        self.max_display_pages_var = ctk.StringVar(value="500")
        self.max_display_pages_entry = ctk.CTkEntry(max_pages_frame, textvariable=self.max_display_pages_var, width=100)
        self.max_display_pages_entry.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Botões da janela
        buttons_frame = ctk.CTkFrame(scrollable_frame)
        buttons_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Botão Restaurar Padrões
        restore_btn = ctk.CTkButton(buttons_frame, text="Restaurar Padrões", 
                                   command=self.restore_default_config, fg_color="orange", hover_color="darkorange")
        restore_btn.pack(side="left", padx=10, pady=15)
        
        # Botão Salvar
        save_btn = ctk.CTkButton(buttons_frame, text="Salvar Configurações", 
                                command=self.save_advanced_config)
        save_btn.pack(side="left", padx=10, pady=15)
        
        # Botão Fechar
        close_btn = ctk.CTkButton(buttons_frame, text="Fechar", 
                                 command=self.config_window.destroy)
        close_btn.pack(side="right", padx=10, pady=15)
        
        # Carregar configurações salvas
        self.load_advanced_config()
        
    def change_theme(self, new_theme):
        """Muda o tema da interface"""
        ctk.set_appearance_mode(new_theme)
        self.log_message(f"Tema alterado para: {new_theme}")
        
    def save_advanced_config(self):
        """Salva as configurações avançadas"""
        try:
            # Obter configurações básicas existentes
            config_data = self.config_manager.load_config() or {}
            
            # Adicionar configurações avançadas
            advanced_config = {
                'timeout': int(self.timeout_var.get()),
                'retry_attempts': int(self.retry_var.get()),
                'batch_size': int(self.batch_size_var.get()),
                'delay_between_batches': float(self.delay_var.get()),
                'clean_wikitext': self.clean_wikitext_var.get(),
                'include_metadata': self.include_metadata_var.get(),
                'verbose_logging': self.verbose_logging_var.get(),
                'auto_save_cache': self.auto_save_cache_var.get(),
                'backup_cache': self.backup_cache_var.get(),
                'theme': self.theme_var.get(),
                'max_display_pages': int(self.max_display_pages_var.get()),
                
                # BookStack configurações
                'bookstack_url': self.bookstack_url_var.get().strip(),
                'bookstack_token_id': self.bookstack_token_id_var.get().strip(),
                'bookstack_token_secret': self.bookstack_token_secret_var.get().strip(),
                'bookstack_verify_ssl': self.bookstack_verify_ssl_var.get()
            }
            
            # Mesclar com configurações existentes
            config_data.update(advanced_config)
            
            # Salvar
            self.config_manager.save_config(config_data)
            self.log_message("Configurações avançadas salvas com sucesso!")
            
            # Fechar janela
            self.config_window.destroy()
            
        except ValueError as e:
            self.log_message(f"ERRO: Valores inválidos nas configurações: {e}")
        except Exception as e:
            self.log_message(f"ERRO ao salvar configurações avançadas: {e}")
            
    def test_bookstack_connection(self):
        """Testa a conexão com o BookStack"""
        try:
            from src.bookstack_client import BookStackClient
            
            # Obter valores dos campos
            base_url = self.bookstack_url_var.get().strip()
            token_id = self.bookstack_token_id_var.get().strip()
            token_secret = self.bookstack_token_secret_var.get().strip()
            verify_ssl = self.bookstack_verify_ssl_var.get()
            
            # Validar campos obrigatórios
            if not base_url:
                self.bookstack_status_label.configure(text="❌ URL Base é obrigatória", text_color="red")
                return
                
            if not token_id:
                self.bookstack_status_label.configure(text="❌ Token ID é obrigatório", text_color="red")
                return
                
            if not token_secret:
                self.bookstack_status_label.configure(text="❌ Token Secret é obrigatório", text_color="red")
                return
            
            # Atualizar status
            self.bookstack_status_label.configure(text="🔄 Testando conexão...", text_color="orange")
            self.test_bookstack_btn.configure(state="disabled")
            
            # Teste em thread separada para não travar a interface
            def test_connection():
                try:
                    # Criar cliente BookStack
                    client = BookStackClient(
                        base_url=base_url,
                        token_id=token_id,
                        token_secret=token_secret,
                        verify_ssl=verify_ssl
                    )
                    
                    # Testar conexão obtendo informações básicas
                    books = client.get_books(limit=1)  # Corrigido: usar 'limit' ao invés de 'count'
                    
                    # Sucesso
                    self.root.after(0, lambda: self.bookstack_status_label.configure(
                        text="✅ Conexão bem-sucedida!", text_color="green"))
                    self.root.after(0, lambda: self.test_bookstack_btn.configure(state="normal"))
                    self.root.after(0, lambda: self.log_message("✅ Teste de conexão BookStack: SUCESSO"))
                    
                except Exception as e:
                    error_msg = str(e)
                    self.root.after(0, lambda: self.bookstack_status_label.configure(
                        text=f"❌ Erro: {error_msg[:50]}...", text_color="red"))
                    self.root.after(0, lambda: self.test_bookstack_btn.configure(state="normal"))
                    self.root.after(0, lambda: self.log_message(f"❌ Teste de conexão BookStack FALHOU: {error_msg}"))
            
            # Executar teste em thread separada
            threading.Thread(target=test_connection, daemon=True).start()
            
        except ImportError:
            self.bookstack_status_label.configure(text="❌ Erro: módulo BookStack não encontrado", text_color="red")
            self.log_message("❌ ERRO: Módulo BookStackClient não encontrado")
        except Exception as e:
            self.bookstack_status_label.configure(text=f"❌ Erro: {str(e)[:30]}...", text_color="red")
            self.log_message(f"❌ ERRO no teste BookStack: {e}")
            self.test_bookstack_btn.configure(state="normal")
            
    def load_advanced_config(self):
        """Carrega as configurações avançadas salvas"""
        try:
            config_data = self.config_manager.load_config()
            
            if config_data:
                # Carregar configurações com valores padrão
                self.timeout_var.set(str(config_data.get('timeout', 30)))
                self.retry_var.set(str(config_data.get('retry_attempts', 3)))
                self.batch_size_var.set(str(config_data.get('batch_size', 10)))
                self.delay_var.set(str(config_data.get('delay_between_batches', 1)))
                self.clean_wikitext_var.set(config_data.get('clean_wikitext', True))
                self.include_metadata_var.set(config_data.get('include_metadata', True))
                self.verbose_logging_var.set(config_data.get('verbose_logging', False))
                self.auto_save_cache_var.set(config_data.get('auto_save_cache', True))
                self.backup_cache_var.set(config_data.get('backup_cache', False))
                self.theme_var.set(config_data.get('theme', 'dark'))
                self.max_display_pages_var.set(str(config_data.get('max_display_pages', 500)))
                
                # BookStack configurações
                self.bookstack_url_var.set(config_data.get('bookstack_url', ''))
                self.bookstack_token_id_var.set(config_data.get('bookstack_token_id', ''))
                self.bookstack_token_secret_var.set(config_data.get('bookstack_token_secret', ''))
                self.bookstack_verify_ssl_var.set(config_data.get('bookstack_verify_ssl', True))
                
        except Exception as e:
            self.log_message(f"ERRO ao carregar configurações avançadas: {e}")
            
    def restore_default_config(self):
        """Restaura configurações para os valores padrão"""
        self.timeout_var.set("30")
        self.retry_var.set("3")
        self.batch_size_var.set("10")
        self.delay_var.set("1")
        self.clean_wikitext_var.set(True)
        self.include_metadata_var.set(True)
        self.verbose_logging_var.set(False)
        self.auto_save_cache_var.set(True)
        self.backup_cache_var.set(False)
        self.theme_var.set("dark")
        self.max_display_pages_var.set("500")
        
        # Aplicar tema padrão
        ctk.set_appearance_mode("dark")
        
        self.log_message("Configurações restauradas para os valores padrão")
    
    def get_max_display_pages(self):
        """Obtém o número máximo de páginas para exibir das configurações"""
        try:
            config_data = self.config_manager.load_config()
            if config_data:
                return config_data.get('max_display_pages', 500)
            return 500
        except:
            return 500

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MediaWikiApp()
    app.run()