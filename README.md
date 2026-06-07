# 🤖 Chatbot para Consultório Médico (WhatsApp + IA + RAG)

Chatbot de atendimento para consultório médico, integrado ao WhatsApp, com respostas baseadas em IA e em documentos da clínica (RAG).

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
├── app.py
├── chains.py
├── config.py
├── dockercompose.yml
├── evolution_api.py
├── memory.py
├── message_buffer.py
├── prompts.py
├── requirements.txt
├── vectorstore.py
├── waiting_list.py
├── .env.example
└── .gitignore
```

---

## 🔐 Configuração de ambiente

Este projeto já possui um arquivo **`.env.example`** com as variáveis necessárias.

1. Crie o `.env` com base no exemplo:

```bash
cp .env.example .env
```

2. Preencha os valores reais no `.env` (chaves, prompts e credenciais).

> **Importante:** nunca versione o arquivo `.env` com dados sensíveis.

---

## 🚀 Como executar com Docker

### 1) Subir os serviços

```bash
docker compose -f dockercompose.yml up --build -d
```

### 2) Ver logs do bot

```bash
docker compose -f dockercompose.yml logs -f bot
```

### 3) Parar os serviços

```bash
docker compose -f dockercompose.yml down
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

- Mensagem inicial: envia saudação automática no primeiro contato.
- Debounce: espera alguns segundos para agrupar mensagens enviadas em sequência.
- Lista de espera: quando a IA retorna o APPOINTMENT_MARKER, o paciente entra em fila temporária (TTL no Redis) para continuidade com secretaria.

---

## ✅ Status do projeto

- MVP funcional para cenário de clínica pequena, com arquitetura modular e pronta para evolução incremental.

---

## 👨‍💻 Autor

Desenvolvido por **Leonardo**.

- GitHub: [github.com/LeonardoAlmeidaGit](https://github.com/LeonardoAlmeidaGit)
- LinkedIn: [linkedin.com/in/leonardoalmeida-](https://www.linkedin.com/in/leonardoalmeida-/)
