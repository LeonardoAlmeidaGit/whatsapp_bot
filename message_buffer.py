import asyncio
import redis.asyncio as redis

from collections import defaultdict

from config import (
    REDIS_URL,
    BUFFER_KEY_SUFIX,
    DEBOUNCE_SECONDS,
    BUFFER_TTL,
    CLINIC_NAME,
    APPOINTMENT_MARKER,
    FIRST_MESSAGE_KEY_SUFFIX,
)

from chains import get_conversational_rag_chain
from evolution_api import send_whatsapp_message
from waiting_list import add_to_waiting_list, is_in_waiting_list


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
conversational_rag_chain = get_conversational_rag_chain()
debounce_tasks = defaultdict(asyncio.Task)

WELCOME_MESSAGE = (
    f'Olá! Seja bem-vindo(a) à {CLINIC_NAME}! 😊\n\n'
    'Sou a assistente virtual da clínica e estou aqui para responder '
    'suas dúvidas sobre nossos serviços, horários, valores e muito mais.\n\n'
    'Caso queira marcar uma consulta ou qualquer outro serviço, '
    'basta solicitar um agendamento e nossa secretaria dará continuidade '
    'ao seu atendimento. Como posso te ajudar?'
)


def log(*args):
    print('[BUFFER]', *args)


async def _is_first_message(chat_id) -> bool:
    buffer_key = f'{chat_id}{FIRST_MESSAGE_KEY_SUFFIX}'
    result = await redis_client.set(buffer_key, '1', nx=True)
    return result is True


async def buffer_message(chat_id, message):
    buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'

    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, int(BUFFER_TTL))

    log(f'Mensagem adicionada ao buffer de {chat_id}: {message}')

    if debounce_tasks.get(chat_id):
        debounce_tasks[chat_id].cancel()
        log(f'Debounce resetado para {chat_id}')

    debounce_tasks[chat_id] = asyncio.create_task(handle_debounce(chat_id))


async def handle_debounce(chat_id):
    try:
        log(f'Iniciando debounce para {chat_id}')
        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        if await is_in_waiting_list(chat_id):
            log(f'Paciente {chat_id} está na lista de espera - mensagem ignorada')
            buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'
            await redis_client.delete(buffer_key)
            return

        buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'
        messages = await redis_client.lrange(buffer_key, 0, -1)
        full_message = ' '.join(messages).strip()

        if not full_message:
            return

        is_first = await _is_first_message(chat_id)
        if is_first:
            log(f'Primeiro contato de {chat_id} - enviando mensagem de boas-vindas')
            send_whatsapp_message(number=chat_id, text=WELCOME_MESSAGE)
            await asyncio.sleep(1.5)

        log(f'Processando mensagem de {chat_id}: {full_message}')
        ai_response = conversational_rag_chain.invoke(
            input={'input': full_message},
            config={'configurable': {'session_id': chat_id}},
        )['answer']

        if APPOINTMENT_MARKER in ai_response:
            ai_response = ai_response.replace(APPOINTMENT_MARKER, '').strip()
            await add_to_waiting_list(chat_id)
            log(f'Paciente {chat_id} adicionado à lista de espera após solicitação de agendamento')

        send_whatsapp_message(number=chat_id, text=ai_response)
        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        log(f'Debounce cancelado para {chat_id}')
