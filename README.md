# 📥 tg-downloader

**Script para salvar conteúdo de grupos e canais do Telegram.**

Este script é uma ferramenta de automação desenvolvida em Python para realizar o download em massa de mídias (fotos, vídeos, áudios e documentos) de chats do Telegram.

É baseado no projeto [tg_mirror](https://github.com/viniped/tg_mirror), porém modificado e expandido para atender necessidades específicas, como suporte aprimorado a **Tópicos (Fóruns)**, sistemas de cache para grandes volumes de mensagens e retomar downloads interrompidos.

## 🚀 Funcionalidades

* **Suporte a Tópicos (Fóruns v2):** Capaz de baixar chats normais ou grupos divididos em Tópicos, permitindo escolher um tópico específico.
* **Resume Capability (Retomada):** Verifica se o arquivo já existe e se o tamanho corresponde, evitando baixar novamente itens já concluídos.
* **Sistema de Cache Inteligente:** Salva o histórico de mensagens localmente (`cache/`) para acelerar execuções futuras e evitar *flood wait* da API.
* **Autenticação Automática:** Gerencia sessões do Pyrogram e solicita credenciais (`API_ID` e `HASH`) via terminal apenas na primeira execução.
* **Organização:** Salva os arquivos em pastas organizadas pelo nome do chat e limpa caracteres inválidos para o Windows.

## 📋 Pré-requisitos

Antes de começar, você precisará:

1.  **Python 3.8+** instalado e adicionado ao PATH.
2.  Uma conta no Telegram.
3.  **API ID e API HASH**:
    * Acesse [my.telegram.org](https://my.telegram.org).
    * Vá em "API Development tools".
    * Crie um novo aplicativo (pode colocar qualquer nome e URL) para obter seu `App api_id` e `App api_hash`.

## 🛠️ Instalação e Uso

1.  Execute **`install_requirements.bat`** para instalar as dependências necessárias automaticamente.
2.  Execute **`tg_downloader.bat`** para iniciar o programa.

## ⚙️ Primeira Execução

Ao rodar o script pela primeira vez (e caso não exista o arquivo `user.session`), será necessário autenticar:

1.  O script detectará que não há uma sessão salva.
2.  Digite seu **API ID** (apenas números) quando solicitado no terminal.
3.  Digite seu **API HASH**.
4.  Insira seu número de telefone (com código do país, ex: `+5567999999999`) e o código de confirmação que chegará no seu aplicativo do Telegram.

> **Nota:** As credenciais serão salvas em `user.session` e não serão solicitadas novamente nas próximas execuções.

## 📂 Estrutura do Projeto

* `main.py`: Arquivo principal que orquestra a execução.
* `config.py`: Configurações globais (pastas de destino, limites, tipos de arquivo).
* `downloader.py`: Lógica principal de download, verificação de arquivos e barra de progresso.
* `session_manager.py`: Gerencia login, autenticação e limpeza de sessões antigas.
* `chat_selector.py`: Menus interativos para listar e selecionar grupos/tópicos.
* `cache_manager.py`: Otimização para salvar metadados de mensagens e reduzir requisições à API.
* `utils.py`: Funções auxiliares para limpeza de nomes de arquivos e pastas.

## ⚠️ Aviso 

O uso de scripts de automação (userbots) está sujeito aos Termos de Serviço do Telegram.
* Use com responsabilidade e por sua conta e risco.
* Evite baixar canais gigantescos em um espaço de tempo muito curto para evitar limitações temporárias na sua conta.
* Este software é para uso educacional e pessoal.
