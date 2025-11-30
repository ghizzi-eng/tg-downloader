## tg_mirror/
## ├── main.py                    Arquivo principal
## ├── config.py                  Configurações e constantes
## ├── session_manager.py         Gerenciamento de sessões
## ├── chat_selector.py           Seleção de chats e tópicos
## ├── downloader.py              Lógica de download
## └── utils.py                   Funções auxiliares

"""Script principal do Telegram Downloader"""
from session_manager import authenticate, force_clean_sessions
from utils import show_banner, cache_path, rename_files
from chat_selector import get_channel, select_topic_from_chat
from downloader import download_media_from_channel
from config import VIDEO_PATH
import sys
import time

def main():
    """Função principal"""
    show_banner()
    
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--clean-sessions":
            force_clean_sessions()
            return
        elif sys.argv[1] == "--help":
            print("Uso: python main.py [opção]")
            print("Opções:")
            print("  --clean-sessions  Limpa todas as sessões forçadamente")
            print("  --help            Mostra esta ajuda")
            return
    
    # Verifica autenticação primeiro
    if not authenticate():
        print("❌ Por favor, autentique-se primeiro executando o script de configuração.")
        return
    
    cache_path()
    
    # Obtém o canal/grupo
    channel_source, chat_title, is_forum = get_channel()
    
    topic_id = None
    
    # Se for um fórum, lista e seleciona o tópico
    if is_forum == 'IS_FORUM':
        topic_id = select_topic_from_chat(channel_source, chat_title)
        time.sleep(5)
    # Inicia o download SEMPRE com todos os tipos de mídia

    download_media_from_channel(channel_source, chat_title, topic_id) 
    rename_files(VIDEO_PATH, chat_title)

if __name__ == "__main__":
    main()