#!/usr/bin/env python3
"""
Teste da Interface de Configurações BookStack
============================================

Este script testa especificamente se a seção BookStack está sendo exibida
corretamente na janela de configurações.
"""

import customtkinter as ctk
import os
import sys

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config_manager import ConfigManager

class ConfigTestWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Teste - Configurações BookStack")
        self.root.geometry("600x800")
        
        self.config_manager = ConfigManager()
        self.create_test_window()
        
    def create_test_window(self):
        """Cria uma janela de teste com apenas as configurações BookStack"""
        # Frame scrollable principal
        scrollable_frame = ctk.CTkScrollableFrame(self.root)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(scrollable_frame, text="🧪 Teste - Configurações BookStack", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # 📚 Seção BookStack
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
        
        # Botões de teste
        test_buttons_frame = ctk.CTkFrame(scrollable_frame)
        test_buttons_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Botão carregar configurações
        load_btn = ctk.CTkButton(test_buttons_frame, text="Carregar Configurações Salvas", 
                                command=self.load_config_test)
        load_btn.pack(side="left", padx=10, pady=15)
        
        # Botão salvar configurações
        save_btn = ctk.CTkButton(test_buttons_frame, text="Salvar Configurações de Teste", 
                                command=self.save_config_test)
        save_btn.pack(side="left", padx=10, pady=15)
        
        # Fechar
        close_btn = ctk.CTkButton(test_buttons_frame, text="Fechar", 
                                 command=self.root.destroy)
        close_btn.pack(side="right", padx=10, pady=15)
        
        # Carregar configurações existentes
        self.load_config_test()
    
    def test_bookstack_connection(self):
        """Testa a conexão com o BookStack"""
        try:
            from bookstack_client import BookStackClient
            
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
            
            # Teste simples
            print(f"🔗 Testando conexão com: {base_url}")
            print(f"📝 Token ID: {token_id[:10]}...")
            print(f"🔒 Verificar SSL: {verify_ssl}")
            
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
            self.bookstack_status_label.configure(text="✅ Conexão bem-sucedida!", text_color="green")
            print("✅ Teste de conexão BookStack: SUCESSO")
            
        except ImportError:
            self.bookstack_status_label.configure(text="❌ Erro: módulo BookStack não encontrado", text_color="red")
            print("❌ ERRO: Módulo BookStackClient não encontrado")
        except Exception as e:
            error_msg = str(e)
            self.bookstack_status_label.configure(text=f"❌ Erro: {error_msg[:50]}...", text_color="red")
            print(f"❌ Teste de conexão BookStack FALHOU: {error_msg}")
        finally:
            self.test_bookstack_btn.configure(state="normal")
    
    def load_config_test(self):
        """Carrega configurações salvas"""
        try:
            config_data = self.config_manager.load_config()
            if config_data:
                # Carregar configurações BookStack
                self.bookstack_url_var.set(config_data.get('bookstack_url', ''))
                self.bookstack_token_id_var.set(config_data.get('bookstack_token_id', ''))
                self.bookstack_token_secret_var.set(config_data.get('bookstack_token_secret', ''))
                self.bookstack_verify_ssl_var.set(config_data.get('bookstack_verify_ssl', True))
                
                print("✅ Configurações carregadas com sucesso!")
                print(f"URL: {config_data.get('bookstack_url', 'não configurada')}")
                print(f"Token ID: {'configurado' if config_data.get('bookstack_token_id') else 'não configurado'}")
                print(f"Token Secret: {'configurado' if config_data.get('bookstack_token_secret') else 'não configurado'}")
            else:
                print("ℹ️ Nenhuma configuração encontrada")
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
    
    def save_config_test(self):
        """Salva configurações de teste"""
        try:
            config_data = self.config_manager.load_config() or {}
            
            # Adicionar configurações BookStack
            config_data.update({
                'bookstack_url': self.bookstack_url_var.get().strip(),
                'bookstack_token_id': self.bookstack_token_id_var.get().strip(),
                'bookstack_token_secret': self.bookstack_token_secret_var.get().strip(),
                'bookstack_verify_ssl': self.bookstack_verify_ssl_var.get()
            })
            
            self.config_manager.save_config(config_data)
            print("✅ Configurações BookStack salvas com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar configurações: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("🧪 Iniciando teste das configurações BookStack...")
    app = ConfigTestWindow()
    app.run()
