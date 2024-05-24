import sqlite3
import logging
from config import LOGS, DB_FILE

# Настройка логирования для записи ошибок в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

# Путь к файлу базы данных
path_to_db = DB_FILE

# Функция для подключения к базе данных и выполнения SQL-запроса
def connect_and_execute(query, params=None):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
            if cursor.fetchone() is None:
                logging.error("DATABASE: Таблица messages не существует.")
                return None
            cursor.execute(query, params)
            return cursor
    except Exception as e:
        logging.error(f"DATABASE: Ошибка при выполнении запроса: {e}")
        return None


def create_database():
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # создаём таблицу messages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                role TEXT,
                total_gpt_tokens INTEGER,
                tts_symbols INTEGER,
                stt_blocks INTEGER)
            ''')
            logging.info("DATABASE: База данных создана")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

# Функция для добавления нового сообщения в таблицу messages
def add_message(user_id, full_message):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            message, role, total_gpt_tokens, tts_symbols, stt_blocks = full_message
            # записываем в таблицу новое сообщение
            cursor.execute('''
                    INSERT INTO messages (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                           (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks)
                           )
            conn.commit()  # сохраняем изменения
            logging.info(f"DATABASE: INSERT INTO messages "
                         f"VALUES ({user_id}, {message}, {role}, {total_gpt_tokens}, {tts_symbols}, {stt_blocks})")
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

# считаем количество уникальных пользователей помимо самого пользователя
def count_users(user_id):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            # получаем количество уникальных пользователей помимо самого пользователя
            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (user_id,))
            count = cursor.fetchone()[0]
            return count 
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None

# Функция для получения последних <n_last_messages> сообщений пользователя
def select_n_last_messages(user_id, n_last_messages=4):
    messages = []  # Список для хранения сообщений
    total_spent_tokens = 0  # Общее количество потраченных токенов
    try:
        # Подключение к базе данных и выбор последних сообщений
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT message, role, total_gpt_tokens FROM messages WHERE user_id=? ORDER BY id DESC LIMIT?''',
                           (user_id, n_last_messages))
            data = cursor.fetchall()
            # Если данные получены, добавляем их в список сообщений
            if data and data[0]:
                for message in reversed(data):
                    messages.append({'text': message[0], 'role': message[1]})
                    total_spent_tokens = max(total_spent_tokens, message[2])
            # Возвращаем список сообщений и общее количество потраченных токенов
            return messages, total_spent_tokens
    except Exception as e:
        # Логирование ошибки при выборе сообщений
        logging.error(e)
        return messages, total_spent_tokens

# Функция для подсчета использования определенных лимитов пользователем
def count_all_limits(user_id, limit_type):
    try:
        # Подключение к базе данных и подсчет использования лимита
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT SUM({limit_type}) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()
            if data and data[0]:
                logging.info(f"DATABASE: У user_id={user_id} использовано {data[0]} {limit_type}")
                return data[0]
            else:
                return 0
    except Exception as e:
        # Логирование ошибки при подсчете использования лимита
        logging.error(e)
        return 0

