
MAX_USERS = 5  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 5_000  # 5 000 символов
MAX_USER_GPT_TOKENS = 2_000  # 2 000 токенов

LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор, но чётко отвечай на вопросы. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом
HOME_DIR = '/home/student/Final_Project'  # путь к папке с проектом
LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/messages.db'  # файл для базы данных

IAM_TOKEN_PATH = fr'{HOME_DIR}/creds/iam_token.json'  # путь к файлу с IAM токеном
#IAM_TOKEN_PATH = ""
FOLDER_ID_PATH = fr'{HOME_DIR}/creds/folder_id.txt'# путь к файлу с ID папки
#FOLDER_ID_PATH = "b1gvi183qbhglaftheoa"
BOT_TOKEN_PATH = fr'{HOME_DIR}/creds/bot_token.txt'  # путь к файлу с токеном бота
#BOT_TOKEN_PATH = '7058190803:AAFYE9BQzzmnQEuUXSFNTpGvx2nT4VHoa1Y'
