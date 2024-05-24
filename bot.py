import telebot
import logging
from validators import*
from yandex_gpt import ask_gpt
from config import LOGS, COUNT_LAST_MSG
from database import create_database, add_message, select_n_last_messages
from speechkit import speech_to_text, text_to_speech
from creds import get_bot_token  


logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

create_database()
bot = telebot.TeleBot(get_bot_token())  # создаём объект бота

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Привет Отправь мне голосовое сообщение или текст, и я тебе отвечу Если ты хочешь чтобы я озвучил текст, то нажми /stt, А если наоборот, то нажми /tts")

@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt)

def stt(message):
    user_id = message.from_user.id
    
    if not message.voice:
        bot.send_message(user_id, "Пожалуйста, отправьте голосовое сообщение.")
        return
    
        
    stt_blocks = is_stt_block_limit(message, message.voice.duration)
    if not stt_blocks:
        return
        
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)

    status, text = speech_to_text(file)

    if status:
        bot.send_message(user_id, text, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, text)

@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщением текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, lambda m: process_message(m, user_id))

def process_message(message, user_id):
    if message.content_type == 'text':
        text = message.text
        status_tts, voice_response = text_to_speech(text)
        if status_tts:
            bot.send_voice(user_id, voice_response)
        else:
            bot.send_message(user_id, "Ошибка при преобразовании текста в речь")

@bot.message_handler(commands=['debug'])
def debug(message): 
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    status_check_users, error_message = check_number_of_users(user_id)
    if not status_check_users:
        bot.send_message(user_id, error_message)
        return

    full_user_message = [message.text, 'user', 0, 0, 0]
    add_message(user_id=user_id, full_message=full_user_message)

    last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
    total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
    if error_message:
        bot.send_message(user_id, error_message)
        return

    status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
    if not status_gpt:
        bot.send_message(user_id, answer_gpt)
        return
    total_gpt_tokens += tokens_in_answer

    full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
    add_message(user_id=user_id, full_message=full_gpt_message)

    bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user_id = message.from_user.id
    status_check_users, error_message = check_number_of_users(user_id)
    if not status_check_users:
        bot.send_message(user_id, error_message)
        return

    stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
    if error_message:
        bot.send_message(user_id, error_message)
        return

    # Загрузка и преобразование голосового сообщения в текст
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    status_stt, stt_text = speech_to_text(file)
    if not status_stt:
        bot.send_message(user_id, stt_text)
        return

    add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

    # Выбор последних сообщений и проверка лимитов токенов GPT
    last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
    total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
    if error_message:
        bot.send_message(user_id, error_message)
        return

    # Запрос ответа от GPT и обработка его
    status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
    if not status_gpt:
        bot.send_message(user_id, answer_gpt)
        return
    total_gpt_tokens += tokens_in_answer

    # Проверка лимитов символов TTS и добавление сообщения
    tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)
    if error_message:
        bot.send_message(user_id, error_message)
        return

    add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

    # Преобразование ответа в голос и отправка
    status_tts, voice_response = text_to_speech(answer_gpt)
    if status_tts:
        bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

bot.polling()
