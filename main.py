import customtkinter as ctk
import threading
import os
from datetime import datetime
from src.mediawiki_client import MediaWikiClient
from src.logger import Logger
from src.config_manager import ConfigManager

class MediaWikiApp:
    def __init__(self):
        self.client = None
        self.logger = Logger()
        self.config_manager = ConfigManager()
        self.is_connected = False
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title("MediaWiki to BookStack")
        self.root.geometry("600x500")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(main_frame, text="MediaWiki API Client", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20)
        
        # Frame de configuração (login)
        self.config_frame = ctk.CTkFrame(main_frame)
        self.config_frame.pack(fill="x", padx=20, pady=10)
        
        # URL da API
        ctk.CTkLabel(self.config_frame, text="URL da API MediaWiki:").pack(anchor="w", padx=10, pady=(10,0))
        self.url_entry = ctk.CTkEntry(self.config_frame, placeholder_text="https://wiki.example.com/api.php")
        self.url_entry.pack(fill="x", padx=10, pady=(5,10))
        
        # Usuário
        ctk.CTkLabel(self.config_frame, text="Usuário:").pack(anchor="w", padx=10, pady=(0,0))
        self.username_entry = ctk.CTkEntry(self.config_frame, placeholder_text="Digite seu usuário")
        self.username_entry.pack(fill="x", padx=10, pady=(5,10))
        
        # Senha
        ctk.CTkLabel(self.config_frame, text="Senha:").pack(anchor="w", padx=10, pady=(0,0))
        self.password_entry = ctk.CTkEntry(self.config_frame, placeholder_text="Digite sua senha", show="*")
        self.password_entry.pack(fill="x", padx=10, pady=(5,10))
        
        # Checkbox para salvar senha
        self.save_password_var = ctk.BooleanVar()
        self.save_password_checkbox = ctk.CTkCheckBox(self.config_frame, text="Salvar senha (não recomendado)", 
                                                     variable=self.save_password_var)
        self.save_password_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para verificação SSL
        self.verify_ssl_var = ctk.BooleanVar(value=False)
        self.verify_ssl_checkbox = ctk.CTkCheckBox(self.config_frame, text="Verificar certificado SSL", 
                                                  variable=self.verify_ssl_var)
        self.verify_ssl_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para bypass de restrições
        self.bypass_restrictions_var = ctk.BooleanVar(value=True)
        self.bypass_restrictions_checkbox = ctk.CTkCheckBox(self.config_frame, 
                                                           text="Contornar restrições de permissão", 
                                                           variable=self.bypass_restrictions_var)
        self.bypass_restrictions_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para modo bot
        self.bot_mode_var = ctk.BooleanVar(value=False)
        self.bot_mode_checkbox = ctk.CTkCheckBox(self.config_frame, 
                                                text="Usar modo bot (para contas com privilégios)", 
                                                variable=self.bot_mode_var)
        self.bot_mode_checkbox.pack(anchor="w", padx=10, pady=(0,5))
        
        # Checkbox para expansão de templates
        self.expand_templates_var = ctk.BooleanVar(value=True)
        self.expand_templates_checkbox = ctk.CTkCheckBox(self.config_frame, 
                                                        text="Expandir templates (conteúdo completo)", 
                                                        variable=self.expand_templates_var)
        self.expand_templates_checkbox.pack(anchor="w", padx=10, pady=(0,10))
        
        # Botões de login
        self.login_button_frame = ctk.CTkFrame(main_frame)
        self.login_button_frame.pack(fill="x", padx=20, pady=10)
        
        self.connect_btn = ctk.CTkButton(self.login_button_frame, text="Conectar", command=self.connect_to_wiki)
        self.connect_btn.pack(side="left", padx=10, pady=10)
        
        self.save_btn = ctk.CTkButton(self.login_button_frame, text="Salvar Config", command=self.save_config)
        self.save_btn.pack(side="left", padx=10, pady=10)
        
        self.load_btn = ctk.CTkButton(self.login_button_frame, text="Carregar Config", command=self.load_config)
        self.load_btn.pack(side="left", padx=10, pady=10)
        
        # Frame conectado (inicialmente oculto)
        self.connected_frame = ctk.CTkFrame(main_frame)
        
        # Informações da conexão
        self.connection_info_label = ctk.CTkLabel(self.connected_frame, text="", 
                                                 font=ctk.CTkFont(size=14, weight="bold"))
        self.connection_info_label.pack(pady=10)
        
        # Botões para usuário conectado
        connected_buttons_frame = ctk.CTkFrame(self.connected_frame)
        connected_buttons_frame.pack(fill="x", padx=20, pady=10)
        
        self.test_btn = ctk.CTkButton(connected_buttons_frame, text="Testar Conexão", command=self.test_connection)
        self.test_btn.pack(side="left", padx=10, pady=10)
        
        self.list_prefixes_btn = ctk.CTkButton(connected_buttons_frame, text="Listar Prefixos", command=self.list_page_prefixes)
        self.list_prefixes_btn.pack(side="left", padx=10, pady=10)
        
        self.list_pages_btn = ctk.CTkButton(connected_buttons_frame, text="Listar Páginas", command=self.list_all_pages)
        self.list_pages_btn.pack(side="left", padx=10, pady=10)
        
        self.extract_pages_btn = ctk.CTkButton(connected_buttons_frame, text="Extrair Markdown", command=self.extract_all_content)
        self.extract_pages_btn.pack(side="left", padx=10, pady=10)
        
        # Adicionar botão para salvar arquivos
        self.save_files_btn = ctk.CTkButton(connected_buttons_frame, text="Salvar Markdown", 
                                          command=self.save_extracted_files, state="disabled")
        self.save_files_btn.pack(side="left", padx=10, pady=10)
        
        self.logout_btn = ctk.CTkButton(connected_buttons_frame, text="Sair", command=self.logout, 
                                       fg_color="red", hover_color="darkred")
        self.logout_btn.pack(side="right", padx=10, pady=10)
        
        # Status
        self.status_label = ctk.CTkLabel(main_frame, text="Status: Desconectado", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)
        
        # Lista de prefixos/páginas
        self.content_frame = ctk.CTkFrame(main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(self.content_frame, text="Conteúdo da Wiki:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        # Progress bar
        self.progress_label = ctk.CTkLabel(self.content_frame, text="")
        self.progress_label.pack(anchor="w", padx=10, pady=(5,0))
        
        self.progress_bar = ctk.CTkProgressBar(self.content_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(5,5))
        self.progress_bar.set(0)
        
        # Frame para seleção de páginas
        self.pages_selection_frame = ctk.CTkScrollableFrame(self.content_frame, height=200)
        self.pages_selection_frame.pack(fill="both", expand=True, padx=10, pady=(5,5))
        
        # Botões de seleção
        self.selection_buttons_frame = ctk.CTkFrame(self.content_frame)
        self.selection_buttons_frame.pack(fill="x", padx=10, pady=(0,5))
        
        self.select_all_btn = ctk.CTkButton(self.selection_buttons_frame, text="Selecionar Tudo", 
                                          command=self.select_all_pages, width=120)
        self.select_all_btn.pack(side="left", padx=(0,5))
        
        self.select_none_btn = ctk.CTkButton(self.selection_buttons_frame, text="Deselecionar Tudo", 
                                           command=self.deselect_all_pages, width=120)
        self.select_none_btn.pack(side="left", padx=(0,5))
        
        self.selected_count_label = ctk.CTkLabel(self.selection_buttons_frame, text="0 páginas selecionadas")
        self.selected_count_label.pack(side="right", padx=(5,0))
        
        # Textbox para visualização de resultados
        self.content_textbox = ctk.CTkTextbox(self.content_frame, height=100)
        self.content_textbox.pack(fill="x", padx=10, pady=(0,10))
        
        # Inicializar lista de checkboxes de páginas
        self.page_checkboxes = []
        self.current_pages = []
        
        # Inicializar variável para conteúdo extraído
        self.extracted_content = {}
        
        # Carregar configurações automaticamente
        self.load_config(show_message=False)
        
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
        
    def show_login_screen(self):
        """Mostra a tela de login e oculta a tela conectada"""
        self.config_frame.pack(fill="x", padx=20, pady=10)
        self.login_button_frame.pack(fill="x", padx=20, pady=10)
        self.connected_frame.pack_forget()
        self.is_connected = False
        
    def show_connected_screen(self):
        """Mostra a tela conectada e oculta a tela de login"""
        self.config_frame.pack_forget()
        self.login_button_frame.pack_forget()
        self.connected_frame.pack(fill="x", padx=20, pady=10)
        self.is_connected = True
        
        # Atualizar informações da conexão
        username = self.username_entry.get()
        api_url = self.url_entry.get()
        self.connection_info_label.configure(text=f"Conectado como: {username}\nAPI: {api_url}")
        
    def logout(self):
        """Desconecta e volta para a tela de login"""
        try:
            self.client = None
            self.log_message("Desconectado com sucesso!")
            self.update_status("Desconectado", "white")
            self.show_login_screen()
            
            # Limpar senha por segurança
            self.password_entry.delete(0, 'end')
            
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
                self.root.after(0, lambda: self.update_status("Conectado", "green"))
                self.root.after(0, self.show_connected_screen)
            else:
                self.log_message("ERRO: Falha na autenticação")
                self.root.after(0, lambda: self.update_status("Erro de autenticação", "red"))
                
        except Exception as e:
            self.log_message(f"ERRO: {str(e)}")
            self.root.after(0, lambda: self.update_status("Erro de conexão", "red"))
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
        """Carrega as configurações salvas"""
        try:
            config_data = self.config_manager.load_config()
            
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
                    
        except Exception as e:
            self.log_message(f"ERRO ao carregar configurações: {str(e)}")
    
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
    
    def list_all_pages(self):
        """Lista todas as páginas da wiki"""
        if not self.client:
            return
            
        self.list_pages_btn.configure(state="disabled")
        self.update_status("Carregando páginas...", "yellow")
        self.content_textbox.delete("1.0", "end")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Iniciando...")
        
        threading.Thread(target=self._list_pages_worker, daemon=True).start()
        
    def _list_pages_worker(self):
        """Worker thread para listar páginas"""
        try:
            self.log_message("Obtendo lista de todas as páginas...")
            
            def progress_callback(total, batch):
                self.root.after(0, lambda: self.progress_label.configure(text=f"Carregadas: {total} páginas"))
            
            pages = self.client.get_all_pages(callback=progress_callback)
            
            if pages:
                # Armazenar páginas
                self.current_pages = pages
                
                # Criar checkboxes para cada página
                self.root.after(0, lambda: self._create_page_checkboxes(pages))
                self.root.after(0, lambda: self.update_status(f"{len(pages)} páginas encontradas", "green"))
                self.root.after(0, lambda: self.progress_bar.set(1.0))
                
                self.log_message(f"Encontradas {len(pages)} páginas na wiki")
                
            else:
                error_msg = "Nenhuma página encontrada na wiki."
                self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
                self.root.after(0, lambda: self.update_status("Nenhuma página encontrada", "orange"))
                self.log_message("AVISO: Nenhuma página retornada pela API")
                
        except Exception as e:
            error_msg = f"ERRO ao listar páginas: {str(e)}"
            self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
            self.root.after(0, lambda: self.update_status("Erro ao carregar páginas", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.list_pages_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
    
    def _create_page_checkboxes(self, pages):
        """Cria checkboxes para seleção de páginas"""
        # Limpar checkboxes existentes
        for checkbox in self.page_checkboxes:
            checkbox.destroy()
        self.page_checkboxes.clear()
        
        # Criar novo checkbox para cada página
        for i, page in enumerate(pages):
            title = page.get('title', 'Sem título')
            page_id = page.get('pageid', 'N/A')
            
            # Criar variável para o checkbox
            var = ctk.BooleanVar(value=True)  # Selecionado por padrão
            
            # Criar frame para organizar checkbox e info da página
            page_frame = ctk.CTkFrame(self.pages_selection_frame)
            page_frame.pack(fill="x", padx=5, pady=2)
            
            # Checkbox
            checkbox = ctk.CTkCheckBox(
                page_frame, 
                text=f"{title} (ID: {page_id})",
                variable=var,
                command=self.update_selected_count
            )
            checkbox.pack(anchor="w", padx=10, pady=5)
            
            # Armazenar referências
            checkbox.page_data = page
            checkbox.var = var
            self.page_checkboxes.append(checkbox)
        
        # Atualizar contador
        self.update_selected_count()
    
    def select_all_pages(self):
        """Seleciona todas as páginas"""
        for checkbox in self.page_checkboxes:
            checkbox.var.set(True)
        self.update_selected_count()
    
    def deselect_all_pages(self):
        """Deseleciona todas as páginas"""
        for checkbox in self.page_checkboxes:
            checkbox.var.set(False)
        self.update_selected_count()
    
    def update_selected_count(self):
        """Atualiza o contador de páginas selecionadas"""
        selected_count = sum(1 for checkbox in self.page_checkboxes if checkbox.var.get())
        total_count = len(self.page_checkboxes)
        self.selected_count_label.configure(text=f"{selected_count}/{total_count} páginas selecionadas")
    
    def get_selected_pages(self):
        """Retorna lista de páginas selecionadas"""
        selected_pages = []
        for checkbox in self.page_checkboxes:
            if checkbox.var.get():
                selected_pages.append(checkbox.page_data)
        return selected_pages
    
    def extract_all_content(self):
        """Extrai conteúdo das páginas selecionadas"""
        if not self.client or not self.page_checkboxes:
            self.log_message("ERRO: Liste as páginas primeiro")
            self.update_status("Liste as páginas primeiro", "red")
            return
        
        selected_pages = self.get_selected_pages()
        if not selected_pages:
            self.log_message("ERRO: Nenhuma página selecionada")
            self.update_status("Nenhuma página selecionada", "red")
            return
            
        self.extract_pages_btn.configure(state="disabled")
        self.update_status("Extraindo conteúdo...", "yellow")
        self.content_textbox.delete("1.0", "end")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._extract_content_worker, args=(selected_pages,), daemon=True).start()
        
    def _extract_content_worker(self, selected_pages):
        """Worker thread para extrair conteúdo diretamente em markdown"""
        try:
            page_titles = [page['title'] for page in selected_pages]
            total_pages = len(page_titles)
            processed = 0
            
            self.log_message(f"Iniciando extração direta em markdown de {total_pages} páginas selecionadas...")
            
            def progress_callback(current_total, batch_size):
                nonlocal processed
                processed = current_total
                progress = processed / total_pages if total_pages > 0 else 0
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.progress_label.configure(text=f"Extraindo: {processed}/{total_pages}"))
            
            # Extrair diretamente em formato markdown
            expand_templates = self.expand_templates_var.get()
            self.log_message(f"Expansão de templates: {'Ativada' if expand_templates else 'Desativada'}")
            
            contents = self.client.get_page_content_batch(
                page_titles, 
                callback=progress_callback, 
                format_type='markdown',
                expand_templates=expand_templates
            )
            
            # Processar resultados com categorização detalhada de erros
            successful = 0
            failed = 0
            permission_denied = 0
            not_found = 0
            other_errors = 0
            error_details = []
            
            for title, content in contents.items():
                if isinstance(content, dict) and content.get('markdown'):
                    successful += 1
                else:
                    failed += 1
                    if isinstance(content, str) and content.startswith("ERRO:"):
                        error_msg = content[6:]  # Remove "ERRO: " prefix
                        
                        # Categorizar tipos de erro
                        if "403" in error_msg or "Forbidden" in error_msg or "permission" in error_msg.lower():
                            permission_denied += 1
                            error_details.append(f"  🔒 {title}: Sem permissão de acesso")
                        elif "404" in error_msg or "not found" in error_msg.lower() or "não encontrada" in error_msg.lower():
                            not_found += 1
                            error_details.append(f"  ❌ {title}: Página não encontrada")
                        else:
                            other_errors += 1
                            error_details.append(f"  ⚠️ {title}: {error_msg}")
                    else:
                        other_errors += 1
                        error_details.append(f"  ⚠️ {title}: Conteúdo inválido")
            
            summary = [
                f"=== EXTRAÇÃO MARKDOWN COMPLETA ===",
                f"Páginas selecionadas: {total_pages}",
                f"Extraídas com sucesso: {successful}",
                f"Falharam: {failed}",
                ""
            ]
            
            # Estatísticas detalhadas de erros
            if failed > 0:
                summary.extend([
                    "=== ESTATÍSTICAS DE ERROS ===",
                    f"Sem permissão (403): {permission_denied}",
                    f"Não encontradas (404): {not_found}",
                    f"Outros erros: {other_errors}",
                    ""
                ])
                
                # Adicionar detalhes de erros se houver
                if error_details:
                    summary.append("=== DETALHES DOS ERROS ===")
                    summary.extend(error_details[:15])  # Mostrar até 15 erros
                    if len(error_details) > 15:
                        summary.append(f"  ... e mais {len(error_details) - 15} erros")
                    summary.append("")
            
            summary.append("=== PÁGINAS EXTRAÍDAS COM SUCESSO ===")
            
            # Adicionar lista detalhada apenas das páginas bem-sucedidas
            success_count = 0
            for title, content in contents.items():
                if isinstance(content, dict) and content.get('markdown'):
                    success_count += 1
                    if success_count <= 10:  # Mostrar apenas as primeiras 10 para não sobrecarregar
                        categories = len(content.get('categories', []))
                        markdown_size = len(content.get('markdown', ''))
                        
                        summary.append(f"✓ {title}")
                        summary.append(f"    └─ Markdown: {markdown_size:,} caracteres")
                        summary.append(f"    └─ Categorias: {categories}")
                        summary.append(f"    └─ ID: {content.get('pageid', 'N/A')}")
                    elif success_count == 11:
                        summary.append(f"... e mais {successful - 10} páginas extraídas com sucesso")
                        break
            
            result_text = "\n".join(summary)
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", result_text))
            
            # Status com informação sobre permissões
            if permission_denied > 0:
                status_msg = f"Extração completa: {successful}/{total_pages} ({permission_denied} sem permissão)"
                self.root.after(0, lambda: self.update_status(status_msg, "orange"))
            else:
                self.root.after(0, lambda: self.update_status(f"Extração completa: {successful}/{total_pages}", "green"))
                
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            
            # Log detalhado
            log_msg = f"Extração markdown completa: {successful} páginas extraídas"
            if permission_denied > 0:
                log_msg += f", {permission_denied} sem permissão"
            if not_found > 0:
                log_msg += f", {not_found} não encontradas"
            if other_errors > 0:
                log_msg += f", {other_errors} outros erros"
            
            self.log_message(log_msg)
            
            # Log específico para páginas sem permissão
            if permission_denied > 0:
                self.log_message(f"AVISO: {permission_denied} páginas não puderam ser acessadas devido a restrições de permissão")
                self.log_message("Considere usar uma conta com mais privilégios ou solicitar acesso ao administrador")
            
            # Armazenar conteúdo para próximas operações
            self.extracted_content = contents
            
            # Habilitar botão de salvar se há conteúdo extraído
            if successful > 0:
                self.root.after(0, lambda: self.save_files_btn.configure(state="normal"))
            
        except Exception as e:
            error_msg = f"ERRO na extração: {str(e)}"
            self.root.after(0, lambda: self.content_textbox.delete("1.0", "end"))
            self.root.after(0, lambda: self.content_textbox.insert("1.0", error_msg))
            self.root.after(0, lambda: self.update_status("Erro na extração", "red"))
            self.log_message(error_msg)
        finally:
            self.root.after(0, lambda: self.extract_pages_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))

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

{''.join(f'- `{title}`: {error}\\n' for title, error in permission_errors[:20])}
{f'*... e mais {len(permission_errors) - 20} páginas*' if len(permission_errors) > 20 else ''}

### ❌ Páginas Não Encontradas (404)
**Total:** {len(not_found_errors)} páginas

{''.join(f'- `{title}`: {error}\\n' for title, error in not_found_errors[:10])}
{f'*... e mais {len(not_found_errors) - 10} páginas*' if len(not_found_errors) > 10 else ''}

### ⚠️ Outros Erros
**Total:** {len(other_errors)} páginas

{''.join(f'- `{title}`: {error}\\n' for title, error in other_errors[:10])}
{f'*... e mais {len(other_errors) - 10} páginas*' if len(other_errors) > 10 else ''}

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

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MediaWikiApp()
    app.run()