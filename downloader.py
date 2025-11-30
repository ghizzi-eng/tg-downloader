"""Lógica de download de mídia"""
import os
import time
import json
from pyrogram import Client
from tqdm import tqdm
from config import SESSION_NAME, VIDEO_PATH, DEFAULT_CHOICES, MAX_MESSAGES, BATCH_SIZE
from utils import (limpar_nome_arquivo, get_cleaned_file_path,
                  save_last_processed_message_id, load_last_processed_message_id)
from cache_manager import (save_messages_to_cache, load_messages_from_cache, 
                          ask_use_cache, get_message_topic_id, 
                          get_topic_messages_by_link_pattern, get_topic_messages_final_approach,
                          get_topic_messages_native) 

def download_progress(current, total, bar):
    """Função de callback para a barra de progresso do tqdm."""
    bar.update(current - bar.n)
      
def get_all_messages_with_topics(client, channel_id, chat_title, use_cache=True):
    """Obtém todas as mensagens do chat, usando cache se disponível."""
    
    if use_cache:
        cache_data = load_messages_from_cache(channel_id, chat_title)
        if cache_data:
            if ask_use_cache(chat_title, cache_data['total_messages']):
                return cache_data['messages']
        else:
            print("📭 Nenhum cache encontrado, iniciando nova busca...")
    
    print(f"🔍 Buscando até {MAX_MESSAGES} mensagens do chat...")
    all_messages = []
    
    try:
        with tqdm(total=MAX_MESSAGES, desc="Coletando mensagens") as pbar:
            offset_id = 0
            batch_count = 0
            
            while len(all_messages) < MAX_MESSAGES:
                try:
                    batch_count += 1
                    messages = list(client.get_chat_history(
                        channel_id, 
                        limit=BATCH_SIZE,
                        offset_id=offset_id
                    ))
                    
                    if not messages:
                        break
                        
                    all_messages.extend(messages)
                    pbar.update(len(messages))
                    
                    if len(messages) < BATCH_SIZE:
                        break
                        
                    offset_id = messages[-1].id
                    time.sleep(1)
                    
                except Exception as e:
                    if "PEER_ID_INVALID" in str(e) or "timeout" in str(e).lower():
                        break
                    time.sleep(5)
                    continue
        
        if all_messages:
            save_messages_to_cache(channel_id, chat_title, all_messages)
        
        return all_messages
        
    except Exception as e:
        print(f"❌ Erro ao buscar mensagens: {e}")
        return []

def get_topic_messages_direct(client, channel_id, topic_id, chat_title):
    """Busca mensagens específicas do tópico usando abordagem nativa."""
    topic_messages = get_topic_messages_native(client, channel_id, topic_id)
    if topic_messages:
        return topic_messages
    
    print("❌ Falha na busca nativa. Tentando padrão de link...")
    link_messages = get_topic_messages_by_link_pattern(client, channel_id, topic_id)
    if link_messages:
        return link_messages
    
    return []

def download_media_from_channel(channel_source, chat_title, topic_id):
    """Lógica principal de download."""
    try:
        with Client(SESSION_NAME) as client:
            chat_directory = os.path.join(VIDEO_PATH, limpar_nome_arquivo(chat_title))
            if not os.path.exists(chat_directory):
                os.makedirs(chat_directory)

            last_id = 0
            
            # --- COLETA DE MENSAGENS ---
            if topic_id and topic_id != "ALL_TOPICS" and topic_id != -1:
                all_messages = get_topic_messages_direct(client, channel_source, int(topic_id), chat_title)
            else:
                all_messages = get_all_messages_with_topics(client, channel_source, chat_title, use_cache=True)
            
            if not all_messages:
                print("❌ Nenhuma mensagem encontrada.")
                return
            
            # Filtra apenas mensagens com mídia para cálculos
            media_messages = [msg for msg in all_messages if msg.photo or msg.audio or msg.video or msg.document]
            
            print(f"📊 Analisando {len(media_messages)} arquivos encontrados...")

            # --- NOVO: PRÉ-CHECAGEM DE ARQUIVOS ---
            # Verifica quantos já existem para mostrar o total correto (Total Encontrado - Já Baixados)
            existing_files_count = 0
            
            # Vamos iterar rapidinho só para checar existência
            for msg in media_messages:
                media = msg.photo or msg.audio or msg.video or msg.document
                # Usamos a função auxiliar para prever o nome
                check_path = get_cleaned_file_path(media, VIDEO_PATH, chat_title, msg.caption)
                if os.path.exists(check_path):
                    # Verifica tamanho para garantir que não está corrompido/incompleto
                    file_size = getattr(media, 'file_size', 0) or 0
                    if os.path.getsize(check_path) == file_size:
                        existing_files_count += 1
            
            real_total_to_download = len(media_messages) - existing_files_count
            print(f"   📂 Já existem: {existing_files_count}")
            print(f"   📥 Restam baixar: {real_total_to_download}")
            print("=" * 60)
            print("             Iniciando Download" )

            downloaded_count = 0
            skipped_count = 0 # Mantemos para log final
            error_count = 0
            
            # --- LOOP PRINCIPAL ---
            for message in all_messages:
                
                # Ignorar mensagens antigas se houver lógica de last_id
                if message.id <= last_id:
                    continue
                
                media = message.photo or message.audio or message.video or message.document
                
                if not media:
                    save_last_processed_message_id(chat_title, channel_source, message.id)
                    continue 

                # Filtro de tipos
                is_valid_type = (
                    (1 in DEFAULT_CHOICES and message.photo) or
                    (2 in DEFAULT_CHOICES and message.audio) or
                    (3 in DEFAULT_CHOICES and message.video) or
                    (4 in DEFAULT_CHOICES and message.document)
                )

                if is_valid_type:
                    file_name = get_cleaned_file_path(media, VIDEO_PATH, chat_title, message.caption)
                    file_size = getattr(media, 'file_size', 0) or 0
                    
                    # Verificação de Existência (De novo, para decidir se baixa)
                    if os.path.exists(file_name):
                        if os.path.getsize(file_name) == file_size:
                            # Arquivo existe e tamanho bate -> Pula
                            skipped_count += 1
                            save_last_processed_message_id(chat_title, channel_source, message.id)
                            continue
                    
                    # Se chegou aqui, VAI baixar
                    downloaded_count += 1
                    
                    # Info visual
                    message_info = message.caption or message.text or getattr(media, 'file_name', f"Arquivo {message.id}")
                    clean_info = message_info.replace('\n', ' ').strip()
                    
                    print(f"\n📥 Baixando: [{downloaded_count}/{real_total_to_download}] | {clean_info} [{file_size / (1024*1024):.2f} MB]")
                    
                    bar = tqdm(
                        total=file_size, 
                        desc="   🚀", 
                        leave=False, 
                        unit='B', 
                        unit_scale=True,
                        ncols=120,
                        bar_format='{desc} {percentage:3.0f}%|{bar:40}| {rate_fmt} | Decorrido: {elapsed} | Restante: {remaining}',
                        colour="#276827"
                    )
                    
                    try:
                        start_time = time.time()
                        
                        client.download_media(
                            media, 
                            file_name=file_name, 
                            progress=lambda current, total: download_progress(current, total, bar)
                        )
                        bar.close()
                        
                        duration = time.time() - start_time
                        time_str = f"{duration:.1f}s" if duration < 60 else f"{int(duration)//60}m {int(duration)%60}s"
                        
                        print(f"   ✅ Download com Sucesso {os.path.basename(file_name)} em {time_str}")
                        
                    except Exception as e:
                        bar.close()
                        error_count += 1
                        print(f"\n❌ ERRO: {e}")
                        if file_name and os.path.exists(file_name):
                             try: os.remove(file_name)
                             except: pass
                        time.sleep(1)

                save_last_processed_message_id(chat_title, channel_source, message.id)
                
            print("=" * 60)
            print(f"🎉 Concluído! Baixados: {downloaded_count} | Existentes: {skipped_count} | Erros: {error_count}")
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")