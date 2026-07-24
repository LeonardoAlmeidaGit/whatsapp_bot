# 🤖 Chatbot para Consultório Médico (WhatsApp + IA + RAG)

Chatbot de atendimento para consultório médico, integrado ao WhatsApp, com respostas baseadas em IA e em documentos da clínica (RAG).

> ℹ️ Este repositório é uma versão pública e **anonimizada** de um projeto real, sem dados, prompts ou identificação do cliente.

---

## 🎯 Objetivo

Automatizar o primeiro atendimento via WhatsApp para:

- responder dúvidas frequentes;
- manter contexto da conversa por paciente;
- identificar intenção de agendamento e encaminhar para atendimento humano.

Projeto pensado para **clínicas de pequeno porte**, com foco em simplicidade e operação prática.

---

## 🧱 Arquitetura

- **API/Webhook:** FastAPI
- **Canal WhatsApp:** Evolution API
- **IA:** LangChain + OpenAI
- **RAG:** ChromaDB + arquivos `.pdf` e `.txt`
- **Memória de conversa:** Redis
- **Fila de espera para agendamento:** Redis (TTL)
- **Infra:** Docker Compose

---

## ⚙️ Fluxo de funcionamento

1. WhatsApp envia evento para `POST /webhook`.
2. O bot recebe a mensagem e salva no buffer Redis.
3. O debounce agrupa mensagens curtas enviadas em sequência.
4. A cadeia RAG processa o contexto e gera a resposta.
5. Se houver marcador de agendamento, o paciente vai para a lista de espera.
6. A resposta final é enviada ao WhatsApp via Evolution API.

---

## 📁 Estrutura do projeto

```bash
.
├── app.py                 # Aplicação FastAPI e endpoint do webhook
├── message_buffer.py      # Buffer de mensagens com debounce (Redis)
├── chains.py              # Montagem da cadeia RAG conversacional
├── vectorstore.py         # Carga de documentos e base vetorial (ChromaDB)
├── memory.py              # Histórico de conversa por sessão (Redis)
├── waiting_list.py        # Fila de espera para agendamento (Redis + TTL)
├── evolution_api.py       # Integração de envio de mensagens (Evolution API)
├── prompts.py             # Templates de prompt
├── config.py              # Carregamento das variáveis de ambiente
├── rag_files/             # Documentos-fonte para o RAG (.pdf e .txt)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements_dev.txt
├── .flake8
├── .env.example
└── .gitignore
```

---

## 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- Uma **chave de API da OpenAI**
- Um **número de WhatsApp** para parear com a Evolution API (que sobe junto no Docker Compose)

---

## 🔐 Configuração de ambiente

Este projeto já possui um arquivo **`.env.example`** com as variáveis necessárias.

**1. Crie o `.env` com base no exemplo:**
```bash
cp .env.example .env
```

**2. Preencha os valores reais no `.env`**, principalmente:

- `OPENAI_API_KEY` — sua chave da OpenAI
- `AUTHENTICATION_API_KEY` — chave de autenticação da Evolution API (defina uma)
- `EVOLUTION_INSTANCE_NAME` — nome da instância do WhatsApp
- `CLINIC_NAME` e os prompts (`AI_SYSTEM_PROMPT`, `AI_CONTEXTUALIZE_PROMPT`)

> **Importante:** nunca versione o arquivo `.env` com dados sensíveis. Ele já está no `.gitignore`.

---

## 🚀 Como executar com Docker

**1. Suba os serviços** (bot, Evolution API, PostgreSQL e Redis):
```bash
docker compose up --build -d
```

**2. Acompanhe os logs do bot:**
```bash
docker compose logs -f bot
```

**3. Pareie o WhatsApp:** acesse a Evolution API em `http://localhost:8080`, crie/conecte a instância definida em `EVOLUTION_INSTANCE_NAME` lendo o QR Code, e configure o webhook da instância para apontar para o serviço do bot (`http://bot:8000/webhook`).

**4. Parar os serviços:**
```bash
docker compose down
```

---

## 🔗 Endpoint principal

### `POST /webhook`

Payload esperado (exemplo simplificado):

```json
{
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net"
    },
    "message": {
      "conversation": "Olá, quero agendar uma consulta"
    }
  }
}
```

---

## 📚 Base de conhecimento (RAG)

- Adicione arquivos `.pdf` e `.txt` na pasta configurada em `RAG_FILES_DIR`.
- Na inicialização, os documentos são:
  - carregados;
  - divididos em chunks;
  - indexados no ChromaDB;
  - movidos para a pasta `processed/`.

---

## ✅ Funcionalidades implementadas

- Recebimento de mensagens via webhook
- Respostas automáticas com IA
- Memória conversacional por sessão
- RAG com documentos da clínica
- Debounce de mensagens
- Mensagem de boas-vindas no primeiro contato
- Encaminhamento para fila de espera via marcador de agendamento

---

## 🗂️ Regras de atendimento implementadas

- **Mensagem inicial:** envia saudação automática no primeiro contato.
- **Debounce:** espera alguns segundos para agrupar mensagens enviadas em sequência.
- **Lista de espera:** quando a IA retorna o `APPOINTMENT_MARKER`, o paciente entra em fila temporária (TTL no Redis) para continuidade com a secretaria.

---

<!--
## 📸 Demonstração
Adicione aqui um print de uma conversa real (anonimizada) do bot no WhatsApp:
![Demonstração da conversa](docs/demo.png)
-->

## ✅ Status do projeto

MVP funcional para cenário de clínica pequena, com arquitetura modular e pronta para evolução incremental.

---

## 👨‍💻 Autor

Desenvolvido por **Leonardo Almeida**.

- GitHub: [github.com/LeonardoAlmeidaGit](https://github.com/LeonardoAlmeidaGit)
- LinkedIn: [linkedin.com/in/leonardo-almeida-dev](https://www.linkedin.com/in/leonardo-almeida-dev/)
