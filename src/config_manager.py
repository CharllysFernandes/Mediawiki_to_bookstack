import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file="config/settings.json"):
        self.config_file = config_file
        # Criar diretório de config se não existir
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    def save_config(self, config_data):
        """Salva configurações no arquivo JSON"""
        try:
            # Adicionar configurações padrão se não existirem
            default_config = {
                'verify_ssl': False,  # Padrão desabilitado para evitar problemas
                'timeout': 30,
                'user_agent': 'MediaWiki-to-BookStack/1.0'
            }
            
            # Mesclar com configurações existentes
            config_data = {**default_config, **config_data}
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            raise Exception(f"Erro ao salvar configurações: {str(e)}")
    
    def load_config(self):
        """Carrega configurações do arquivo JSON"""
        try:
            if not os.path.exists(self.config_file):
                return None
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Adicionar configurações padrão se não existirem
            default_values = {
                'verify_ssl': False,
                'timeout': 30,
                'user_agent': 'MediaWiki-to-BookStack/1.0'
            }
            
            for key, value in default_values.items():
                if key not in config:
                    config[key] = value
                    
            return config
                
        except Exception as e:
            raise Exception(f"Erro ao carregar configurações: {str(e)}")
    
    def delete_config(self):
        """Remove o arquivo de configurações"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                return True
            return False
        except Exception as e:
            raise Exception(f"Erro ao deletar configurações: {str(e)}")
    
    def config_exists(self):
        """Verifica se existe arquivo de configuração"""
        return os.path.exists(self.config_file)
