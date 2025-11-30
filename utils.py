## tg_mirror/
## ├── main.py                    Arquivo principal
## ├── config.py                  Configurações e constantes
## ├── session_manager.py         Gerenciamento de sessões
## ├── chat_selector.py           Seleção de chats e tópicos
## ├── downloader.py              Lógica de download
## └── utils.py                   Funções auxiliares

"""Funções utilitárias"""
import os
import re
import json
from config import TASK_DIRECTORY

def limpar_nome_arquivo(nome_arquivo):
    """Remove caracteres inválidos e substitui por '_'."""
    if not nome_arquivo:
        return 'sem_nome'
        
    chars_invalidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\n', '\r']
    nome_limpo = nome_arquivo
    for char in chars_invalidos:
        nome_limpo = nome_limpo.replace(char, '_')
    
    nome_limpo = re.sub(r'_{2,}', '_', nome_limpo)
    
    return nome_limpo.strip('_')

def get_cleaned_file_path(media, directory, chat_title, caption=None):
    """Constrói o caminho completo e limpo para o arquivo de mídia."""
    from config import UNKNOWN_EXTENSION
    
    if caption:
        base_name = limpar_nome_arquivo(caption)
    elif media.file_name:
        base_parts = media.file_name.rsplit('.', 1)
        base_name = limpar_nome_arquivo(base_parts[0]) if len(base_parts) > 1 else limpar_nome_arquivo(media.file_name)
    else:
        base_name = f"arquivo_{media.file_id}"

    extension = media.file_name.split('.')[-1] if media.file_name and '.' in media.file_name else UNKNOWN_EXTENSION
    clean_name = f"{base_name}.{extension}"
    
    chat_directory = os.path.join(directory, limpar_nome_arquivo(chat_title))
    
    return os.path.join(chat_directory, clean_name)

def save_last_processed_message_id(chat_title, channel_source, last_id):
    """Salva o ID da última mensagem processada."""
    if not os.path.exists(TASK_DIRECTORY):
        os.makedirs(TASK_DIRECTORY)
    safe_channel_source = limpar_nome_arquivo(str(channel_source)) 
    json_filepath = f"{TASK_DIRECTORY}/{limpar_nome_arquivo(chat_title)}_{safe_channel_source}.json"
    with open(json_filepath, 'w') as file:
        json.dump({'last_processed_id': last_id}, file)

def load_last_processed_message_id(chat_title, channel_source):
    """Carrega o ID da última mensagem processada para retomar."""
    safe_channel_source = limpar_nome_arquivo(str(channel_source))
    json_filepath = f"{TASK_DIRECTORY}/{limpar_nome_arquivo(chat_title)}_{safe_channel_source}.json"
    try:
        with open(json_filepath, "r") as json_file:
            data = json.load(json_file)
            last_processed_id = data.get("last_processed_id", 0)
            if last_processed_id > 0:
                print(f"⚠️  Detectado progresso anterior no ID {last_processed_id + 1}")
                print("🔄 Ignorando progresso anterior - iniciando do zero")
            return 0
    except FileNotFoundError:
        print("▶️ Iniciando download do zero.")
        return 0

def show_banner():
    print("╔══════════════════════════════════════════════╗")
    print("║          TELEGRAM MEDIA DOWNLOADER           ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"\n O uso inadequado pode resultar em banimento pelo Telegram. Use com responsabilidade.\n")


def cache_path():
    pass

def rename_files(path, title):
    print("Finalizado.")