## tg_mirror/
## ├── chat_selector.py

"""Seleção de chats e tópicos"""
from pyrogram import Client, errors
from config import SESSION_NAME
import re
import time

def list_available_chats():
    """Lista todos os chats/grupos disponíveis para o usuário."""
    try:
        with Client(SESSION_NAME) as client:
            print("📋 Carregando seus chats e grupos...")
            
            chats = []
            try:
                # Obtém diálogos (chats recentes) com limite
                for dialog in client.get_dialogs(limit=50):
                    chat = dialog.chat
                    if chat.type in ["group", "supergroup", "channel"]:
                        chats.append({
                            'id': chat.id,
                            'title': getattr(chat, 'title', 'Sem título'),
                            'type': chat.type,
                            'username': getattr(chat, 'username', None)
                        })
            except Exception as e:
                print(f"⚠️  Aviso ao carregar alguns chats: {e}")
            
            return chats
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def select_chat_from_list():
    """Permite ao usuário selecionar um chat da lista."""
    chats = list_available_chats()
    
    if chats is None:
        print("❌ Erro ao carregar chats. Tente novamente.")
        return None, None
        
    if not chats:
        print("❌ Nenhum grupo ou canal encontrado na sua lista.")
        print("💡 Dica: Entre em algum grupo primeiro ou use um link de convite.")
        return None, None
    
    print("\n--- Seus Grupos e Canais ---")
    for i, chat in enumerate(chats):
        username_str = f" (@{chat['username']})" if chat['username'] else ""
        print(f"{i+1} - {chat['title']} [{chat['type']}]{username_str}")

    while True:
        try:
            choice = input("\nSelecione o número do chat que deseja baixar (ou 0 para usar link manual): ")
            choice_num = int(choice)
            
            if choice_num == 0:
                return get_chat_by_link()
            elif 1 <= choice_num <= len(chats):
                selected_chat = chats[choice_num - 1]
                print(f"✅ Chat selecionado: {selected_chat['title']} (ID: {selected_chat['id']})")
                return selected_chat['id'], selected_chat['title']
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")

def get_chat_by_link():
    """Obtém um chat usando link de convite."""
    with Client(SESSION_NAME) as client:
        while True:
            print("\n📎 Forneça o LINK/CÓDIGO do grupo:")
            link = input("\nLink / ID: ").strip()
            
            if not link:
                continue
                
            try:
                print("🔄 Verificando grupo...")
                try:
                    chat = client.join_chat(link)
                except errors.UserAlreadyParticipant:
                    chat = client.get_chat(link)
                
                print(f"✅ Grupo identificado: {chat.title}")
                return chat.id, chat.title
                
            except Exception as e:
                print(f"❌ Erro ao acessar o chat: {e}")

def get_channel():
    """Obtém a fonte do canal/grupo - sempre usa link/código."""
    with Client(SESSION_NAME) as client:
        print("   Insira o ID do grupo (ex: -100...) ou o Link de Convite")
        
        while True:
            link = input("\nLink / ID do grupo: ").strip()
            
            if not link:
                continue
                
            try:
                try:
                    chat = client.join_chat(link)
                except errors.UserAlreadyParticipant:
                    chat = client.get_chat(link)
                
                print(f"✅ Grupo Conectado: {chat.title}")
                
                is_forum = getattr(chat, 'is_forum', False)
                if is_forum:
                    return chat.id, chat.title, 'IS_FORUM'
                else:
                    return chat.id, chat.title, None
                    
            except Exception as e:
                print(f"❌ Erro: {e}")

def extract_topic_id_from_input(input_str):
    """Extrai o ID do tópico de uma string (Link ou ID puro)."""
    # Se for apenas números
    if input_str.isdigit():
        return int(input_str)
    
    # Se for um link (t.me/c/xxxxx/TOPIC_ID)
    match = re.search(r'/(\d+)(?:/)?$', input_str)
    if match:
        return int(match.group(1))
        
    return None

def select_topic_from_chat(channel_id, chat_title):
    """Solicita ID/Link do tópico, valida o nome e confirma."""
    
    with Client(SESSION_NAME) as client:
        print(f"\n   Insira o ID do tópico ou o Link de uma mensagem do tópico.")
        
        while True:
            user_input = input("\nLink / ID do tópico: ").strip()
            
            if not user_input:
                continue
            
            # 1. Tratamento para TODOS ou MAIN
            if user_input == '0':
                print("✅ Selecionado: TODOS os tópicos")
                return "ALL_TOPICS"
            if user_input == '-1':
                print("✅ Selecionado: Apenas chat principal")
                return None
            
            # 2. Extração do ID
            topic_id = extract_topic_id_from_input(user_input)
            
            if not topic_id:
                print("❌ ID inválido ou link não reconhecido. Tente novamente.")
                continue
            
            print(f"🔍 Buscando informações do tópico {topic_id}...")
            
            try:
                # 3. Validação: Busca a mensagem criadora do tópico para pegar o nome
                topic_info_msg = client.get_messages(channel_id, topic_id)
                
                topic_name = "Desconhecido"
                
                if not topic_info_msg or topic_info_msg.empty:
                    print("⚠️  Não foi possível ler os detalhes deste ID.")
                else:
                    # Obtém o nome
                    if hasattr(topic_info_msg, 'forum_topic_created') and topic_info_msg.forum_topic_created:
                        topic_name = getattr(topic_info_msg.forum_topic_created, 'title', None) or \
                                     getattr(topic_info_msg.forum_topic_created, 'name', "Nome Indisponível")
                                     
                    elif hasattr(topic_info_msg, 'reply_to_top_id'):
                        print("⚠️  Você enviou uma mensagem de dentro do tópico, não o ID principal.")
                        print(f"   💡 ID correto sugerido: {topic_info_msg.reply_to_top_id}")
                        topic_id = topic_info_msg.reply_to_top_id
                        
                        # Busca o nome real agora
                        real_topic = client.get_messages(channel_id, topic_id)
                        if real_topic and hasattr(real_topic, 'forum_topic_created'):
                             topic_name = getattr(real_topic.forum_topic_created, 'title', "Nome Indisponível")
                    else:
                        topic_name = "Nome não detectado (ID Válido)"

                # --- LIMPEZA DO NOME (NOVIDADE) ---
                # Remove "(ID: xxxx)" ou "(ID xxxx)" do final do nome usando Regex
                if topic_name:
                    topic_name = re.sub(r'\s*\(ID:?\s*\d+\)', '', str(topic_name), flags=re.IGNORECASE).strip()

                # 4. Confirmação
                print(f"\n🎯 Tópico Encontrado: {topic_name}")
                print(f"🆔 ID: {topic_id}")
                
                confirm = input("Este é o tópico correto? (s/n): ").lower()
                
                if confirm in ['s', 'sim', 'y']:
                    print("🔍 Analisando mensagens... Aguarde.")
                    time.sleep(5)
                    return topic_id
                else:
                    print("🔄 Tente novamente...")
                    
            except Exception as e:
                print(f"❌ Erro ao validar tópico: {e}")