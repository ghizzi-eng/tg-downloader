
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

1.  **Python <3.12** (testado com 3.11.9)
2.  Uma conta no Telegram.
3.  **API ID e API HASH**:
    * Acesse [my.telegram.org](https://my.telegram.org).
    * Vá em "API Development tools".
    * Crie um novo aplicativo (pode colocar qualquer nome e URL) para obter seu `App api_id` e `App api_hash`.
  
## 🛠️ Instalação 
Se já possui o python na versão 3.11 pule para a [instalação do Script](#Para-instalar-o-script).

### Instalando o Python na versão correta
Possivelmente você está utilizando uma versão superior (3.12+), porém o script usa o tgcrypto e ele não é compatível
Para isto, instale a versão do python anterior, o script foi testado nas versões 3.11.9 e 3.11.0b4, para ter duas versões do python, tem duas formas simples:

*  Utilizando o [pyenv-win](https://github.com/pyenv-win/pyenv-win), um gerenciador de versões do python.
* Utilizando o [UV](https://github.com/astral-sh/uv), um gerenciador de pacotes e versões extremamente rápido e simples (recomendado).
#### 1. Para instalar com o Pyenv
1.  Abra o powershell como administrador e insira o seguinte código:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```
4.  Após isto, digite S (ou Y)
5.  Insira o seguinte comando:
   ```bash 
       Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
   ```
4. Instale a versão do python desejada com o comando:``pyenv install 3.11.0b4``
5. Feche o PowerShell., abra o CMD e navegue até a pasta do script
6.  Determine a utilização da versão baixada: ``pyenv local 3.11.0b4``
7. Crie o ambiente virtual com: ``python -m venv .venv``
8. Agora inicie o ambiente virtual: ``.venv\Scripts\activate``
9. Pronto, seu ambiente virtual está ativado e pronto para iniciar a execução do script
 #### 2. Para instalar com o UV (recomendado)
1.  Abra o powershell como administrador e insira o seguinte código: ``irm https://astral.sh/uv/install.ps1 | iex``
2.  Feche o PowerShell., abra o CMD e navegue até a pasta do script e insira: ``uv venv --python 3.11 .venv``
3. Digite este comando para ativar o ambiente virtual: ``.venv\Scripts\Activate``
4. Pronto, seu ambiente virtual está ativado e pronto para iniciar a execução do script

 ### Para instalar o script
1.  Primeiro, instale as dependencias necessárias:
* Se usou o pyenv ou já possui a versão do python correta: ``pip install -r requirements.txt``
* Se usou o UV: ``uv pip install -r requirements.txt``
2.  Rode o script (independente do uso de pyenv ou UV): ``python.exe main.py``

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
* Utilize para fins educacionais apenas.
* Use com responsabilidade e garanta que você tenha os direitos e permissões necessários para realizar as operações.
* Evite baixar canais gigantescos em um espaço de tempo muito curto para evitar limitações temporárias na sua conta.
* Este software é para uso educacional e pessoal.
* Este código foi feito com ajuda de IA.

## ⚠️ Limitações 

* Requer acesso ao grupo (membro ou link de convite)
* Alguns tópicos podem ter restrições de acesso
* Arquivos muito grandes podem falhar em conexões lentas
* Rate limit da API do Telegram pode causar pausas
