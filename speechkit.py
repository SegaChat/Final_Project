import requests
import json
from database import *
from config import LOGS, IAM_TOKEN_PATH, FOLDER_ID_PATH
from creds import get_creds


IAM_TOKEN, FOLDER_ID = get_creds()  # получаем iam_token и folder_id из файлов


def speech_to_text(data):
    try:
        params = {
            "topic": "general",
            "folderId": FOLDER_ID,
            "lang": "ru-RU"
        }

        headers = {
            'Authorization': f'Bearer {IAM_TOKEN}',
        }
        
        response = requests.post(
            "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize",
            headers=headers, 
            params=params,
            data=data
        )
        
        decoded_data = response.json()
        if decoded_data.get("error_code") is None:
            return True, decoded_data.get("result")
        else:
            return False, "При запросе в SpeechKit возникла ошибка"
    except Exception as e:
        print(f"Ошибка при обработке голосового сообщения: {e}")
        return False, "Произошла ошибка при обработке голосового сообщения"

def text_to_speech(text):
    try:
        headers = {
            'Authorization': f'Bearer {IAM_TOKEN}',
        }
        data = {
            'text': text,
            'lang': 'ru-RU',
            'voice': 'filipp',
            'folderId': FOLDER_ID,
        }
        response = requests.post(
            'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
            headers=headers,
            data=data
        )
        if response.status_code == 200:
            return True, response.content
        else:
            return False, "При запросе в SpeechKit возникла ошибка"
    except Exception as e:
        print(f"Ошибка при синтезе речи: {e}")
        return False, "Произошла ошибка при синтезе речи"
