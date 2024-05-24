import logging
import math
from config import LOGS, MAX_USERS, MAX_USER_GPT_TOKENS, MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS
from database import count_users, count_all_limits
from yandex_gpt import count_gpt_tokens

# Настройка логирования
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

def check_number_of_users(user_id):
    count = count_users(user_id)
    if count is None:
        return None, "Ошибка при работе с БД"
    if count > MAX_USERS:
        return None, "Превышено максимальное количество пользователей"
    return True, ""

def is_gpt_token_limit(messages, total_spent_tokens):
    all_tokens = count_gpt_tokens(messages) + total_spent_tokens
    if all_tokens > MAX_USER_GPT_TOKENS:
        return None, f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
    return all_tokens, ""

# проверяем, не превысил ли пользователь лимиты на преобразование аудио в текст
def is_stt_block_limit(user_id, duration):
    # Получаем текущее количество использованных STT блоков для пользователя
    used_stt_blocks = count_all_limits(user_id, 'stt_blocks')
    
    # Проверяем, не превышает ли продолжительность голосового сообщения лимит
    if duration > MAX_USER_STT_BLOCKS:
        return False, "Превышен лимит на преобразование аудио в текст"
    
    # Если продолжительность не превышает лимит, но использованные блоки уже достигли максимума
    if used_stt_blocks >= MAX_USER_STT_BLOCKS:
        return False, "Превышен лимит на использование STT блоков"
    
    return True, ""


# проверяем, не превысил ли пользователь лимиты на преобразование текста в аудио
def is_tts_symbol_limit(user_id, text):
    # Получаем текущее количество использованных TTS символов для пользователя
    used_tts_symbols = count_all_limits(user_id, 'tts_symbols')
    
    # Подсчитываем количество символов в тексте
    text_length = len(text)
    
    # Проверяем, не превышает ли длина текста лимит
    if text_length > MAX_USER_TTS_SYMBOLS:
        return False, "Превышен лимит на преобразование текста в аудио"
    
    # Если длина текста не превышает лимит, но использованные символы уже достигли максимума
    if used_tts_symbols >= MAX_USER_TTS_SYMBOLS:
        return False, "Превышен лимит на использование TTS символов"
    
    return True, ""
