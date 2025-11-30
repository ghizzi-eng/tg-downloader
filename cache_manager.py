"""Gerenciamento de cache para mensagens"""
import os
import json
import pickle
import time
import re
from pyrogram import Client
from config import SESSION_NAME,MAX_MESSAGES, CACHE_DIRECTORY
from utils import limpar_nome_arquivo

def get_cache_file_path(chat_id, chat_title):
    """Retorna o caminho do arquivo de cache para um chat."""
    if not os.path.exists(CACHE_DIRECTORY):
        os.makedirs(CACHE_DIRECTORY)
    
    safe_chat_title = limpar_nome_arquivo(chat_title)
    return os.path.join(CACHE_DIRECTORY, f"{chat_id}_{safe_chat_title}_cache.pkl")

def save_messages_to_cache(chat_id, chat_title, messages):
    """Salva as mensagens no cache."""
    try:
        cache_file = get_cache_file_path(chat_id, chat_title)
        
        # Salvar as mensagens completas (serializáveis)
        cache_data = {
            'chat_id': chat_id,
            'chat_title': chat_title,
            'total_messages': len(messages),
            'last_updated': time.time(),
            'messages': messages  # Salvar mensagens completas
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"💾 Cache salvo: {len(messages)} mensagens")
        return True
        
    except Exception as e:
        print(f"⚠️  Erro ao salvar cache: {e}")
        return False

def load_messages_from_cache(chat_id, chat_title):
    """Carrega as mensagens do cache."""
    try:
        cache_file = get_cache_file_path(chat_id, chat_title)
        
        if not os.path.exists(cache_file):
            return None
        
        print(f"📂 Verificando cache: {cache_file}")
        with open(cache_file, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Verificar se o cache é do mesmo chat
        if cache_data.get('chat_id') != chat_id:
            print("⚠️  Cache de chat diferente, ignorando")
            return None
            
        print(f"💾 Cache encontrado: {cache_data['total_messages']} mensagens")
        
        return cache_data
        
    except Exception as e:
        print(f"⚠️  Erro ao carregar cache: {e}")
        return None

# No topo do arquivo, garanta que MAX_MESSAGES está importado ou defina um valor
# from config import MAX_MESSAGES

def get_topic_messages_native(client, chat_id, topic_id):
    """
    Busca mensagens de um tópico usando get_discussion_replies.
    Esta função é compatível com versões do Pyrogram que não suportam 
    o filtro message_thread_id no search_messages.
    """
    
    topic_messages = []
    
    try:
        
        # get_discussion_replies itera sobre as mensagens de um tópico/thread
        # Ele lida automaticamente com a paginação.
        # Defina um limite seguro se MAX_MESSAGES não estiver disponível
        limit = 50000 
        
        # Itera sobre o gerador
        for message in client.get_discussion_replies(chat_id=chat_id, message_id=topic_id, limit=limit):
            topic_messages.append(message)
            
            if len(topic_messages) % 500 == 0:
                print(f"   📥 {len(topic_messages)} mensagens coletadas...")
        
        # O get_discussion_replies geralmente retorna do mais novo para o mais antigo.
        # Invertemos para manter a ordem cronológica (Aula 1, Aula 2...)
        topic_messages.reverse()
        
        print(f"\n✅ Total de mensagens encontradas: {len(topic_messages)}")
        
        if topic_messages:
            print(f"   📍 Primeira: {topic_messages[0].id} | Última: {topic_messages[-1].id}")
            
            # Verificação de segurança: Se retornou 0 mensagens, pode ser um erro de acesso.
            if len(topic_messages) == 0:
                print("⚠️  A busca retornou 0 mensagens. O tópico pode estar vazio ou inacessível via API.")

        return topic_messages

    except Exception as e:
        print(f"⚠️ Erro na busca por replies: {e}")
        # Se der erro de atributo, significa que o Pyrogram é MUITO antigo
        if "object has no attribute 'get_discussion_replies'" in str(e):
            print("❌ Seu Pyrogram está desatualizado. Execute: pip install -U pyrogram tgcrypto")
        return []


def get_topic_messages_final_approach(client, channel_id, topic_id):
    """Abordagem final para encontrar mensagens do tópico."""
    print(f"🎯 BUSCA AVANÇADA - Tópico {topic_id}")
    print("=" * 50)
    
    # Método 1: Para tópicos restritos
    print("1. 🔒 Buscando em tópico restrito...")
    restricted_messages = get_topic_messages_for_restricted_topic(client, channel_id, topic_id)
    
    if restricted_messages:
        print(f"✅ SUCCESSO! Encontradas {len(restricted_messages)} mensagens em tópico restrito")
        return restricted_messages
    
    # Método 2: Busca por link pattern (fallback)
    print("2. 🔍 Buscando por padrão de link...")
    link_messages = get_topic_messages_by_link_pattern(client, channel_id, topic_id)
    
    if link_messages:
        print(f"✅ Encontradas {len(link_messages)} mensagens via padrão de link")
        return link_messages
    
    print("❌ Nenhum método funcionou para este tópico")
    print("💡 Possíveis causas:")
    print("   - Tópico está vazio")
    print("   - Restrições muito severas no tópico")
    print("   - IDs das mensagens estão fora do padrão esperado")
    return []

def get_topic_messages_by_link_pattern(client, channel_id, topic_id):
    """Busca mensagens do tópico usando padrão de link."""
    try:
        print(f"🔍 Buscando mensagens do tópico {topic_id} via padrão de link...")
        
        # Converter channel_id para formato de link
        if str(channel_id).startswith('-100'):
            chat_code = str(channel_id)[4:]  # Remove -100
        else:
            chat_code = str(channel_id)
        
        # Padrões de busca para mensagens do tópico
        search_patterns = [
            f"t.me/c/{chat_code}/{topic_id}",
            f"https://t.me/c/{chat_code}/{topic_id}",
            f"t.me/c/{chat_code}/{topic_id}/",
            f"https://t.me/c/{chat_code}/{topic_id}/"
        ]
        
        all_topic_messages = []
        
        for pattern in search_patterns:
            try:
                print(f"   🔎 Buscando: {pattern}")
                found_messages = list(client.search_messages(
                    chat_id=channel_id,
                    query=pattern,
                    limit=100
                ))
                
                if found_messages:
                    print(f"   ✅ Encontradas {len(found_messages)} mensagens com padrão: {pattern}")
                    all_topic_messages.extend(found_messages)
                    
            except Exception as e:
                print(f"   ⚠️  Busca com padrão {pattern} falhou: {e}")
        
        # Remover duplicatas
        unique_messages = []
        seen_ids = set()
        for msg in all_topic_messages:
            if msg.id not in seen_ids:
                seen_ids.add(msg.id)
                unique_messages.append(msg)
        
        print(f"📊 Total de mensagens únicas encontradas no tópico: {len(unique_messages)}")
        return unique_messages
        
    except Exception as e:
        print(f"❌ Erro ao buscar mensagens por padrão de link: {e}")
        return []

def get_message_topic_id(message):
    """Extrai o ID do tópico de uma mensagem com suporte a Fóruns v2."""
    try:
        # 1. Tenta pegar o ID da Thread (Nativo para Fóruns)
        if hasattr(message, 'message_thread_id') and message.message_thread_id:
            return message.message_thread_id

        # 2. Método reply_to_top_id (Antigo/Standard)
        if (hasattr(message, 'reply_to') and 
            hasattr(message.reply_to, 'reply_to_top_id') and 
            message.reply_to.reply_to_top_id):
            return message.reply_to.reply_to_top_id
        
        # 3. Método forum_topic
        elif (hasattr(message, 'reply_to') and 
              hasattr(message.reply_to, 'forum_topic') and 
              message.reply_to.forum_topic):
            return message.reply_to.forum_topic.id
        
        # 4. Método topic_id direto
        elif hasattr(message, 'topic_id') and message.topic_id:
            return message.topic_id
        
        return None
    except Exception:
        return None

def ask_use_cache(chat_title, cached_message_count):
    """Pergunta se o usuário quer usar o cache existente."""
    print(f"\n📂 CACHE ENCONTRADO:")
    print(f"   💬 Chat: {chat_title}")
    print(f"   💾 Mensagens em cache: {cached_message_count}")
    print(f"   ⏰ Use o cache para evitar nova busca (pode ser mais rápido)")
    
    while True:
        choice = input("\nUsar cache existente? (s/N): ").strip().lower()
        if choice in ['s', 'sim', 'y', 'yes']:
            print("✅ Usando cache existente")
            return True
        elif choice in ['n', 'não', 'nao', 'no', '']:
            print("🔄 Iniciando nova busca...")
            return False
        else:
            print("❌ Por favor, responda 's' para sim ou 'n' para não")