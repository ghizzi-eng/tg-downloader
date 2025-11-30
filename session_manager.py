"""Gerenciamento de sessões do Pyrogram"""
import os
import glob
import sqlite3
import time
from pyrogram import Client
from config import SESSION_NAME

def clean_old_sessions():
    """Remove arquivos de sessão antigos, mantendo apenas o atual."""
    try:
        session_patterns = [
            f"{SESSION_NAME}.session*",
            f"*-{SESSION_NAME}.session*",
            f"*-pyrogram.session*"
        ]
        
        session_files = []
        for pattern in session_patterns:
            session_files.extend(glob.glob(pattern))
        
        current_session = f"{SESSION_NAME}.session"
        
        for file_path in session_files:
            if file_path == current_session:
                continue
            if file_path.endswith('-journal'):
                continue
                
            try:
                file_size = os.path.getsize(file_path)
                file_age = time.time() - os.path.getctime(file_path)
                
                if file_age > 3600 or file_size < 100:
                    os.remove(file_path)
            except Exception:
                pass
        
        clean_journal_files()
        
    except Exception as e:
        print(f"⚠️  Erro na limpeza de sessões: {e}")

def clean_journal_files():
    """Remove especificamente arquivos journal."""
    try:
        journal_files = glob.glob(f"{SESSION_NAME}.session-*")
        journal_files = [f for f in journal_files if '-journal' in f]
        for journal_file in journal_files:
            try:
                os.remove(journal_file)
            except Exception:
                pass
    except Exception:
        pass

def verify_session_integrity():
    """Verifica se a sessão atual está íntegra."""
    session_file = f"{SESSION_NAME}.session"
    
    if not os.path.exists(session_file):
        return False
    
    try:
        file_size = os.path.getsize(session_file)
        if file_size < 100:
            return False
            
        conn = sqlite3.connect(session_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        found_tables = [table[0] for table in tables]
        
        if 'sessions' not in found_tables or 'version' not in found_tables:
            conn.close()
            return False
        
        conn.close()
        return True
    except Exception:
        return False

def recreate_session_if_needed():
    """Recria a sessão se estiver corrompida."""
    session_file = f"{SESSION_NAME}.session"
    
    # Se não existe, retornamos True para permitir a criação
    if not os.path.exists(session_file):
        return True
        
    if not verify_session_integrity():
        print("🔄 Sessão corrompida detectada. Tentando limpar...")
        try:
            os.remove(session_file)
            return True
        except Exception as e:
            print(f"❌ Não foi possível remover sessão corrompida: {e}")
            return False
    return True

def authenticate():
    """Verifica se a sessão está autenticada, pedindo credenciais se necessário."""
    try:
        clean_old_sessions()
        
        if not recreate_session_if_needed():
            print("❌ Erro ao preparar ambiente da sessão.")
            return False
        
        session_file = f"{SESSION_NAME}.session"
        api_id = None
        api_hash = None

        # --- LÓGICA DE SOLICITAÇÃO DE CREDENCIAIS ---
        # Só pedimos se o arquivo de sessão NÃO existir
        if not os.path.exists(session_file):
            print("\n👋 \033[1mConfiguração Inicial Necessária\033[0m")
            print("   Como o arquivo de sessão não foi encontrado, precisamos logar.")
            print("   Obtenha seus dados em: https://my.telegram.org/apps")
            print("   -----------------------------------------------------")
            
            try:
                user_api_id = input("👉 Digite seu API_ID (apenas números): ").strip()
                user_api_hash = input("👉 Digite seu API_HASH: ").strip()
                
                if not user_api_id or not user_api_hash:
                    print("❌ Dados vazios. Tente novamente.")
                    return False
                    
                api_id = int(user_api_id)
                api_hash = user_api_hash
                
            except ValueError:
                print("❌ O API_ID deve conter apenas números.")
                return False
        # ---------------------------------------------

        # Inicializa o cliente. Se api_id/hash forem None, ele tenta usar a sessão existente.
        # Se forem fornecidos, ele usa para criar a nova conexão.
        print("\n🔄 Conectando aos servidores do Telegram...")
        app = Client(SESSION_NAME, api_id=api_id, api_hash=api_hash)

        with app as client:
            me = client.get_me()
            print(f"✅ \033[1mAutenticado com sucesso!\033[0m")
            print(f"   Usuário: {me.first_name} (@{me.username})")
            print(f"   ID: {me.id}")
            print(f"   Arquivo de sessão criado: {session_file}")
            return True

    except Exception as e:
        print(f"\n❌ \033[1mErro de autenticação:\033[0m {e}")
        
        if "API_ID_INVALID" in str(e) or "API_HASH_INVALID" in str(e):
            print("💡 As credenciais digitadas parecem incorretas.")
        elif "PHONE_CODE_INVALID" in str(e):
            print("💡 O código SMS digitado está errado.")
        elif "The API key is required" in str(e):
            print("💡 O arquivo de sessão está corrompido ou ausente e não foram fornecidas chaves.")
            # Força remoção para garantir que o input apareça na próxima vez
            if os.path.exists(f"{SESSION_NAME}.session"):
                os.remove(f"{SESSION_NAME}.session")
        
        return False

def force_clean_sessions():
    """Limpeza forçada de todas as sessões."""
    try:
        patterns = [f"{SESSION_NAME}.session*", "*.session*"]
        for pattern in patterns:
            for f in glob.glob(pattern):
                try:
                    os.remove(f)
                    print(f"🗑️ Removido: {f}")
                except: pass
    except: pass