## tg_mirror/
## ├── main.py                    Arquivo principal
## ├── config.py                  Configurações e constantes
## ├── session_manager.py         Gerenciamento de sessões
## ├── chat_selector.py           Seleção de chats e tópicos
## ├── downloader.py              Lógica de download
## └── utils.py                   Funções auxiliares

"""Configurações e constantes globais"""

# Configurações da sessão
SESSION_NAME = "user"
VIDEO_PATH = 'downloads'
TASK_DIRECTORY = 'chat_download_task'
CACHE_DIRECTORY = 'cache'
UNKNOWN_EXTENSION = 'unknown'

# Sempre baixar todos os tipos de mídia
DEFAULT_CHOICES = [1, 2, 3, 4]  # Fotos, Áudios, Vídeos, Arquivos

# Configurações de download
MAX_MESSAGES = 50000  # Reduzido para evitar timeouts
BATCH_SIZE = 100