import urllib.request
import os
import json
from dotenv import load_dotenv

load_dotenv()

def makeRequest(method: str, **params) -> dict:
    token = os.getenv('TOKEN')
    base_uri = os.getenv('TELEGRAM_BASE_URI')
    
    if not token or not base_uri:
        print("Error: TOKEN or TELEGRAM_BASE_URI not found in .env file")
        return {}
    
    url = f"{base_uri}/bot{token}/{method}"
    
    if method in ['getMe', 'getUpdates'] and params:
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{query_string}"
        request_data = None
    else:
        request_data = json.dumps(params, ensure_ascii=False).encode('utf-8') if params else None
    
    request = urllib.request.Request(
        url=url,
        data=request_data,
        headers={"Content-Type": "application/json; charset=utf-8"} if request_data else {}
    )

    try:
        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")
            response_json = json.loads(response_body)
            return response_json["result"] if response_json["ok"] else {}
    except Exception as e:
        print(f"Error: {e}")
        return {}

def getUpdates(**params) -> list:
    result = makeRequest('getUpdates', **params)
    return result if result else []

def sendMessage(chat_id: int, text: str, **params) -> dict:
    return makeRequest('sendMessage', chat_id=chat_id, text=text, **params)

def sendPhoto(chat_id: int, photo: str, **params) -> dict:
    return makeRequest('sendPhoto', chat_id=chat_id, photo=photo, **params)

def deleteMessage(chat_id: int, message_id: int) -> dict:
    return makeRequest("deleteMessage", chat_id=chat_id, message_id=message_id)

def answerCallbackQuery(callback_query_id: str, **kwargs) -> dict:
    return makeRequest("answerCallbackQuery", callback_query_id=callback_query_id, **kwargs)

def getMe() -> dict:
    return makeRequest('getMe')