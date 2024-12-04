import telebot
import google.generativeai as genai
import os
import json

API = "AIzaSyCuIzaLtkDC_PK4EITSlldywsmlT6VB2kE"
bot_api = "6836399431:AAHE6gcjcogdXjNYrRXUuVpK8QCZWHYXs1o"
BOT_TOKEN = bot_api

bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=API)
model = genai.GenerativeModel("gemini-1.5-flash")
model2 = genai.GenerativeModel("gemini-1.5-pro")

user_contexts = {}
pro_access = {}

PRO_ACCESS_FILE = "pro_access.json"

# Load PRO access data from file
def load_pro_access():
    global pro_access
    try:
        with open(PRO_ACCESS_FILE, 'r') as f:
            pro_access = json.load(f)
    except FileNotFoundError:
        pro_access = {}

# Save PRO access data to file
def save_pro_access():
    with open(PRO_ACCESS_FILE, 'w') as f:
        json.dump(pro_access, f)

load_pro_access()

def get_user_context(user_id):
    return user_contexts.get(user_id, None)

def update_user_context(user_id, user_query, bot_response):
    previous_context = get_user_context(user_id)
    if previous_context:
        new_context = model.generate_content(
            f"Этот запрос нужен для ведения твоей стенограммы, ВЕДИ ТОЧНУЮ СТЕНОГРАММУ, "
            f"добавь новую информацию к своей прошлой записи: {previous_context}. "
            f"Вот какой запрос дал пользователь: {user_query} \\ Вот что ты ответил: {bot_response}"
        )
    else:
        new_context = model.generate_content(
            f"Этот запрос нужен для ведения твоей стенограммы, начни ее записывать, ВЕДИ ТОЧНУЮ СТЕНОГРАММУ. "
            f"Вот какой запрос дал пользователь: \"{user_query}\" \\ Вот что ты ответил: \"{bot_response}\""
        )
    user_contexts[user_id] = new_context.text

def AI(text):
    try:
        ans = model.generate_content(text)
        return ans.text
    except Exception as e:
        pass

def AI_mess(message):
    prompt = message.text[7:]
    if prompt:
        user_id = message.from_user.id
        try:
            print(f"Пользователь {message.chat.username} спросил: {prompt}")
            context = get_user_context(user_id)
            if context:
                if pro_access.get(str(message.chat.id)) == True:
                    response = model2.generate_content(
                        f"Запрос: {prompt}, Отвечай в контексте памяти вашего диалога: {context}, "
                        f"если контекст не подходит отвечай без его использования, ни в коем случае не пиши стенограмму в ответе, только сам ответ"
                    )
                    bot.reply_to(message, text=f"{response.text}\nВам ответил: VasyaAI v1.5 PRO")
                else:
                    response = model.generate_content(
                        f"Запрос: {prompt}, Отвечай в контексте памяти вашего диалога: {context}, "
                        f"если контекст не подходит отвечай без его использования, ни в коем случае не пиши стенограмму в ответе, только сам ответ"
                    )
                    bot.reply_to(message, text=f"{response.text}\nВам ответил: VasyaAI v1.5 FAST")
            else:
                if pro_access.get(str(message.chat.id)) == True:
                    response = model2.generate_content(prompt)
                    bot.reply_to(message, text=f"{response.text}\nВам ответил: VasyaAI v1.5 PRO")
                else:
                    response = model.generate_content(prompt)
                    bot.reply_to(message, text=f"{response.text}\nВам ответил: VasyaAI v1.5 FAST")

            print(f"Бот ответил: {response.text}")
            update_user_context(user_id, prompt, response.text)
        except Exception as e:
            print(f"Ошибка: {e}")
            bot.send_message(
                chat_id=message.chat.id,
                text="Простите, я не могу ответить вам, у Liidoteee опять что-то сломалось, скажите ему: "
                     "Здравствуйте, на стороне сервера ошибка: 35631629461. Исправьте ее, пожалуйста."
            )
    else:
        bot.reply_to(message, "Пожалуйста, введите ваш запрос после команды")

@bot.message_handler(commands=["нейро","neiro","Нейро","Neiro"])
def neiro(arg):
    AI_mess(arg)

@bot.message_handler(commands=["заново","start","Заново","Start","Забудь","забудь"])
def new_chat(message):
    try:
        user_contexts.pop(message.from_user.id)
        bot.reply_to(message,"Новый диалог начат")
    except Exception as e:
        bot.reply_to(message,"У меня и так нет памяти о вас")

@bot.message_handler(commands=["Вопрос","вопрос","q","Q"])
def question(message):
    if message.reply_to_message:
        ans = AI(f"Ответь на запрос(вопрос): {message.text} по сообщению: {message.reply_to_message.text}")
        bot.reply_to(message, ans)
        print(f"Ответь на запрос(вопрос): {message.text} .По сообщению: {message.reply_to_message.text}")
        print(f"Ответ: = {ans}")

@bot.message_handler(commands=["про", "pro", "Pro", "Про"])
def pro(message):
    try:
        if message.text.split()[1] == "aB3c5d7eF9gH1jK2L4m6":
            pro_access[str(message.chat.id)] = True
            save_pro_access()  # Save to file each time a user activates PRO access
            bot.reply_to(message, "Вы активировали PRO версию")
        else:
            bot.reply_to(message, "Неверный ключ")
    except Exception as e:
        bot.reply_to(message, "Команда введена неверно")
@bot.message_handler(commands=["фаст","Фаст","fast","Fast"])
def standart(message):
    try:
        pro_access[str(message.chat.id)] = False
        save_pro_access()  # Save to file each time a user activates PRO access
        bot.reply_to(message, "Вы активировали FAST версию")
    except Exception as e:
        bot.reply_to(message, "Команда введена неверно")
@bot.message_handler(commands=["HELLCUM"])
def standartpers(message):
    try:
        pro_access[str(message.chat.id)] = False
        save_pro_access()  # Save to file each time a user activates PRO access
        bot.reply_to(message, "Вы получили cum в рот")
    except Exception as e:
        bot.reply_to(message, "Команда введена неверно")
bot.polling()
