import telebot
import requests
import jsons
from Class_ModelResponse import *

API_TOKEN = '8481135940:AAHIti_sIFMzTXzBxv-C6NistCKWyfAXNuM'
LM_URL = '127.0.0.1:1234'
LM_STUDIO_MODELS_URL = f'http://{LM_URL}/v1/models'
LM_STUDIO_API_URL = f'http://{LM_URL}/v1/chat/completions'
bot = telebot.TeleBot(API_TOKEN)


user_contexts = {}

def get_context(user_id):
    if user_id not in user_contexts:
        user_contexts[user_id] = [
            {
                'role': 'system', 
                'content':'Ты поленый ассистент.'
            }
        ]
    return user_contexts[user_id]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я ваш Telegram бот.\n"
        "Доступные команды:\n"
        "/start - вывод всех доступных команд\n"
        "/model - выводит название используемой языковой модели\n"
        "/clear - очистка контекста"
        "Отправьте любое сообщение, и я отвечу с помощью LLM модели."
    )
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['model'])
def send_model_name(message):
    response = requests.get(LM_STUDIO_MODELS_URL)

    if response.status_code == 200:
        model_info = response.json()
        model_name = model_info['data'][0]['id']
        bot.reply_to(message, f"Используемая модель: {model_name}")
    else:
        bot.reply_to(message, 'Не удалось получить информацию о модели.')

@bot.message_handler(commands=['clear'])
def clear_context(message):
    user_id = message.from_user.id

    if user_id in user_contexts:
        del user_contexts[user_id]
        bot.reply_to(message, "История диалога очищена")
    else:
        bot.reply_to(message, "История диалога уже пуста")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    user_query = message.text

    current_context = get_context(user_id)

    current_context.append({
        'role': 'user', 
        'content': user_query
        }
    )

    request = {
        "messages": current_context
    }
    response = requests.post(
        'http://localhost:1234/v1/chat/completions',
        json=request
    )

    if response.status_code == 200:
        model_response :ModelResponse = jsons.loads(response.text, ModelResponse)
        bot.reply_to(message, model_response.choices[0].message.content)
    else:
        bot.reply_to(message, 'Произошла ошибка при обращении к модели.')


if __name__ == '__main__':
    bot.polling(none_stop=True)