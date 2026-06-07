import json
import redis.asyncio as redis

from datetime import datetime

from config import REDIS_URL, WAITING_LIST_KEY_SUFFIX, WAITING_LIST_TTL


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def log(*args):
    print('[WAITING LIST]', *args)


async def add_to_waiting_list(chat_id):
    waiting_key = f'{chat_id}{WAITING_LIST_KEY_SUFFIX}'
    payload = json.dumps({
        'chat_id': chat_id,
        'added_at': datetime.now().isoformat(),
    })
    await redis_client.set(waiting_key, payload, ex=int(WAITING_LIST_TTL))
    log(f'Paciente {chat_id} adicionado à lista de espera por {WAITING_LIST_TTL}s')


async def is_in_waiting_list(chat_id):
    waiting_key = f'{chat_id}{WAITING_LIST_KEY_SUFFIX}'
    return await redis_client.exists(waiting_key) == 1


async def remove_from_waiting_list(chat_id):
    waiting_key = f'{chat_id}{WAITING_LIST_KEY_SUFFIX}'
    await redis_client.delete(waiting_key)
    log(f'Paciente {chat_id} removido da lista de espera')


async def get_all_waiting():
    pattern = f'*{WAITING_LIST_KEY_SUFFIX}'
    keys = await redis_client.keys(pattern)
    patients = []
    for key in keys:
        raw = await redis_client.get(key)
        ttl = await redis_client.ttl(key)
        if raw:
            data = json.loads(raw)
            data['ttl_seconds'] = ttl
            patients.append(data)
    return patients
