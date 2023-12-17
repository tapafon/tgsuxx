import telebot
import texts_faq
import database
import re
import random
import tokens

API_TOKEN = tokens.API_TOKEN
INVOICE_PROVIDER_TOKEN = tokens.INVOICE_PROVIDER_TOKEN
bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')


# Початковий запис
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, texts_faq.welcome)


# Часто задаваємі питання
@bot.message_handler(commands=['faq'])
def select_faq(message):
    # "клавіатура". Натискання на будь-яку кнопку відправляє текст на ній, нібито користувач сам його набрав і відправив
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = telebot.types.KeyboardButton('ЧИ МІЙ ПРОКАТНИЙ АВТОМОБІЛЬ ПЕРЕДАЄТЬСЯ З ПОВНИМ БАКОМ?')
    button2 = telebot.types.KeyboardButton('ЯК Я МОЖУ ЗАПЛАТИТИ ЗА СВОЄ АВТО?')
    button3 = telebot.types.KeyboardButton('ЯКОЮ Є СУМА ДОДАТКОВИХ ПЛАТЕЖІВ?')
    button4 = telebot.types.KeyboardButton('ЩО МЕНІ НЕОБХІДНО МАТИ З СОБОЮ, КОЛИ Я ОТРИМУЮ АВТО?')
    button5 = telebot.types.KeyboardButton('ЧИ МОЖНА ПЕРЕТИНАТИ КОРДОН?')
    button6 = telebot.types.KeyboardButton('ЯКЩО ТРАПИЛАСЯ НЕСПРАВНІСТЬ ЧИ ПОТРІБНА ДОПОМОГА В ДОРОЗІ?')
    keyboard.add(button1, button2, button3, button4, button5, button6)
    s = bot.send_message(message.chat.id, "Виберіть питання із списку нижче:", reply_markup=keyboard)
    bot.register_next_step_handler(s, send_faq)

def send_faq(message):
    rm = telebot.types.ReplyKeyboardRemove(selective=False)
    match message.text:
        case 'ЧИ МІЙ ПРОКАТНИЙ АВТОМОБІЛЬ ПЕРЕДАЄТЬСЯ З ПОВНИМ БАКОМ?':
            bot.send_message(message.chat.id, texts_faq.faq1, reply_markup=rm)
        case 'ЯК Я МОЖУ ЗАПЛАТИТИ ЗА СВОЄ АВТО?':
            bot.send_message(message.chat.id, texts_faq.faq2, reply_markup=rm)
        case 'ЯКОЮ Є СУМА ДОДАТКОВИХ ПЛАТЕЖІВ?':
            bot.send_message(message.chat.id, texts_faq.faq3, reply_markup=rm)
        case 'ЩО МЕНІ НЕОБХІДНО МАТИ З СОБОЮ, КОЛИ Я ОТРИМУЮ АВТО?':
            bot.send_message(message.chat.id, texts_faq.faq4, reply_markup=rm)
        case 'ЧИ МОЖНА ПЕРЕТИНАТИ КОРДОН?':
            bot.send_message(message.chat.id, texts_faq.faq5, reply_markup=rm)
        case 'ЯКЩО ТРАПИЛАСЯ НЕСПРАВНІСТЬ ЧИ ПОТРІБНА ДОПОМОГА В ДОРОЗІ?':
            bot.send_message(message.chat.id, texts_faq.faq6, reply_markup=rm)
        case _:
            bot.send_message(message.chat.id, "На жаль, я не можу відповісти на це питання.", reply_markup=rm)

# Власне, оренда (крок вибору локації)
@bot.message_handler(commands=['rent'])
def step_one(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Введіть назву міста або виберіть його із списку...")
    button1 = telebot.types.KeyboardButton('Київ')
    button2 = telebot.types.KeyboardButton('Харків')
    button3 = telebot.types.KeyboardButton('Бориспіль')
    button4 = telebot.types.KeyboardButton('Одеса')
    button5 = telebot.types.KeyboardButton('Львів')
    button6 = telebot.types.KeyboardButton('Вінниця')
    keyboard.add(button1, button2, button3, button4, button5, button6)
    s1 = bot.send_message(message.chat.id, "Де ви розпочнете свою поїздку?", reply_markup=keyboard)
    bot.register_next_step_handler(s1, step_two)

# Вибір машини (крок 2)
def step_two(message, loc=None):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Введіть модель машини або виберіть її із списку...")
    if loc == None:
        loc = message.text
    match loc:
        case "Київ":
            for i in range(0, len(database.kyiv)):
                button = telebot.types.KeyboardButton(database.kyiv[i]['name'] + " (" + str(database.kyiv[i]['price']) + " грн/добу)")
                keyboard.add(button)
        case "Харків":
            for i in range(0, len(database.kharkiv)):
                button = telebot.types.KeyboardButton(database.kharkiv[i]['name'] + " (" + str(database.kharkiv[i]['price']) + " грн/добу)")
                keyboard.add(button)
        case "Одеса":
            for i in range(0, len(database.odesa)):
                button = telebot.types.KeyboardButton(database.odesa[i]['name'] + " (" + str(database.odesa[i]['price']) + " грн/добу)")
                keyboard.add(button)
        case "Львів":
            for i in range(0, len(database.lviv)):
                button = telebot.types.KeyboardButton(database.lviv[i]['name'] + " (" + str(database.lviv[i]['price']) + " грн/добу)")
                keyboard.add(button)
        case "Вінниця":
            for i in range(0, len(database.vinnisa)):
                button = telebot.types.KeyboardButton(database.vinnisa[i]['name'] + " (" + str(database.vinnisa[i]['price']) + " грн/добу)")
                keyboard.add(button)
        case _:
            bot.send_message(message.chat.id, "На жаль, в цій точці машин немає :(")
            step_one(message)
            return
    text="""
<b>Вибрана локація: </b><i>""" + loc + """</i>
Яку саме машину ви хочете орендувати?
"""
    s2 = bot.send_message(message.chat.id, text, reply_markup=keyboard)
    bot.register_next_step_handler(s2, step_three, loc)


# Вибір кількості днів (крок 3)
def step_three(message, loc, mdl=None, price=None):
    fail = False
    if mdl == None:
        mdl = message.text.split(" (")[0] # парсимо назву машини
    if price == None:
        try:
            tmp = re.findall(r'\d+', message.text.split(" (")[1]) # парсимо ціну за добу
            price = int(tmp[0])
        except:
            fail = True
    text1 = """
<b>Вибрана машина: </b><i>""" + mdl + """</i>
Оренда цієї машини буде коштувати <i>""" + str(price) + """ грн/добу.</i>
На скільки днів ви будете орендовувати машину?
"""
    if fail:
        bot.send_message(message.chat.id, "Неправильний формат машини. Будь ласка, виберіть її із списку.")
        step_two(message, loc)
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Введіть кількість днів або виберіть популярний варіант...")
    button1 = telebot.types.KeyboardButton('1')
    button2 = telebot.types.KeyboardButton('7')
    button3 = telebot.types.KeyboardButton('14')
    button4 = telebot.types.KeyboardButton('21')
    button5 = telebot.types.KeyboardButton('30')
    button6 = telebot.types.KeyboardButton('90')
    button7 = telebot.types.KeyboardButton('180')
    button8 = telebot.types.KeyboardButton('365')
    keyboard.add(button1, button2, button3, button4, button5, button6, button7, button8)
    s3 = bot.send_message(message.chat.id, text1, reply_markup=keyboard)
    bot.register_next_step_handler(s3, step_four, loc, mdl, price)

# Перевірка даних (крок 4)
def step_four(message, loc, mdl, price, days=None):
    fail = False
    if days == None:
        try:
            days = int(message.text)
        except:
            fail = True
    if not fail:
        if days <= 0:
            fail = True
    if fail:
        bot.send_message(message.chat.id, "Неправильний формат даних")
        step_three(message, loc, mdl, price)
    else:
        cost = days*price
        text = """
<b>Станція прокату: </b><i>""" + loc + """</i>
<b>Машина: </b><i>""" + mdl + """</i>
<b>Кількість днів прокату: </b><i>""" + str(days) + """</i>
<b>Вартість за добу: </b><i>""" + str(price) + """ грн.</i>
<b>Фінальна вартість: </b><i>""" + str((cost)*1.015) + """ грн.*</i>
<i>З урахуванням комісії Portmone</i>
Все вказано вірно?     
"""
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Так чи ні?")
        button1 = telebot.types.KeyboardButton('Так')
        button2 = telebot.types.KeyboardButton('Ні')
        keyboard.add(button1, button2)
        s4 = bot.send_message(message.chat.id, text, reply_markup=keyboard)
        bot.register_next_step_handler(s4, step_final, loc, mdl, price, days, cost)

# Вибір місця оплати (фінальний крок)
def step_final(message, loc, mdl, price, days, cost):
    rm = telebot.types.ReplyKeyboardRemove(selective=False) # видаляємо "клавіатуру" повністю
    if message.text == "Ні" :
        bot.send_message(message.chat.id, "Операцію скасовано.", reply_markup=rm)
    elif message.text == "Так":
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = telebot.types.KeyboardButton('На місці')
        if 3647 <= int(cost*100) <= 36479179 : # через обмеження інвойсів через Telegram довелося написати ось це
            button2 = telebot.types.KeyboardButton('Онлайн')
            keyboard.add(button1, button2)
        else :
            keyboard.add(button1)
            bot.send_message(message.chat.id, "<b>Зверніть увагу: для цієї оренди оплата онлайн недоступна. Не забудьте принести ДВІ кредитні картки з собою.</b>")
        s5 = bot.send_message(message.chat.id, texts_faq.payment_type, reply_markup=keyboard)
        bot.register_next_step_handler(s5, finish, loc, mdl, price, days, cost)
    else:
        bot.send_message(message.chat.id, "Будь ласка, зробіть ваш вибір.")
        step_four(message, loc, mdl, price, days)

# Підтвердження замовлення (та "оплата онлайн", не виходячи з Telegram, через Portmone)
def finish(message, loc, mdl, price, days, cost):
    info = """
<b>Є нове замовлення!!!!!!!</b>    
        
<b>id користувача: </b><i>""" + str(message.chat.id) + """</i>
<b>handle користувача: </b><i>""" + str(message.chat.username) + """</i>
<b>Ім'я користувача: </b><i>""" + str(message.chat.first_name) + """</i>
<b>Прізвище користувача: </b><i>""" + str(message.chat.last_name) + """</i>
<b>Фото користувача: </b><i>""" + str(message.chat.photo) + """</i>
<b>Станція прокату: </b><i>""" + loc + """</i>
<b>Машина: </b><i>""" + mdl + """</i>
<b>Кількість днів прокату: </b><i>""" + str(days) + """</i>
<b>Вартість за добу: </b><i>""" + str(price) + """ грн.</i>
<b>Фінальна вартість: </b><i>""" + str((cost)*1.015) + """ грн.*</i>
<b>Оплата: </b><i>""" + message.text + """</i>
<i>*З урахуванням комісії Portmone</i>
"""
    rm = telebot.types.ReplyKeyboardRemove(selective=False)
    if message.text == "На місці":
        bot.send_message(message.chat.id, "Бронювання підтверджене. Не забудьте з собою кредитну карту (або дві) для оплати.", reply_markup=rm)
        print(info)
        for i in range(0, len(tokens.admins)):
            bot.send_message(tokens.admins[i], info)
    elif message.text == "Онлайн":
        desc = "Оренда " + mdl + " в місті " + loc + " на " + str(days) + " день/дня/днів"
        final_price = [telebot.types.LabeledPrice("Ціна", amount=int(cost*100))]
        bot.send_message(message.chat.id, "Для підтвердження бронювання виконайте оплату ↓", reply_markup=rm)
        bot.send_invoice(message.chat.id, "Оренда автомобіля", desc, "rent", INVOICE_PROVIDER_TOKEN, "UAH", final_price, need_name=True, need_email=True, need_phone_number=True, protect_content=True, send_email_to_provider=True)
        print(info)
        for i in range(0, len(tokens.admins)):
            bot.send_message(tokens.admins[i], info)
    else:
        bot.send_message(message.chat.id, "Будь ласка, зробіть ваш вибір.")
        step_final(message, loc, mdl, price, days, cost)

# Додаткове підтведження оплати
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    random.seed(a=None, version=2)
    rd = (random.randint(1, 2))
    match rd: # Рандом
        case 1:
            bot.answer_pre_checkout_query(pre_checkout_query.id, True)
        case 2:
            bot.answer_pre_checkout_query(pre_checkout_query.id, False, "На жаль, даного автомобіля вже немає в наявності")
            info = "<i>Замовлення з оплатою онлайн було скасоване великим рандомом.</i>"
            print(info)
            for i in range(0, len(tokens.admins)):
                bot.send_message(tokens.admins[i], info)


# Успішна оплата
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, 'Дякуємо за оплату! Бронювання підтверджене.')
    info = "<i>Замовлення від " + str(message.chat.id) + " було оплачене.</i>"
    print(info)
    for i in range(0, len(tokens.admins)):
        bot.send_message(tokens.admins[i], info)

# Адмін панель
@bot.message_handler(commands=['admin'])
def adminpanel(message):
    admin = False
    for i in range(0, len(tokens.admins)):
        if message.chat.id == tokens.admins[i] :
            admin = True
            break
    if not admin: # Постороннім вхід заборонено!
        unauth = "<i>спроба несанкціонованого доступу</i>"
        bot.send_message(message.chat.id, "<b>ПОСТОРОННІМ ВХІД ЗАБОРОНЕНО!!!</b>")
        for i in range(0, len(tokens.admins)):
            bot.send_message(tokens.admins[i], unauth)
        print(unauth)
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = telebot.types.KeyboardButton('Вимкнути бота!!!')
    button2 = telebot.types.KeyboardButton('Вийти')
    keyboard.add(button1, button2)
    s = bot.send_message(message.chat.id, "Вибери свою долю:", reply_markup=keyboard)
    bot.register_next_step_handler(s, adminaction)

def adminaction(message) :
    rm = telebot.types.ReplyKeyboardRemove(selective=False)
    if message.text == "Вимкнути бота!!!" :
        bot.send_message(message.chat.id, "Бот завершує свою роботу", reply_markup=rm)
        bot.stop_bot()
        bot.stop_polling()
        quit(0)
    else:
        bot.send_message(message.chat.id, "Nuff said", reply_markup=rm)

# Стандартна відповідь
@bot.message_handler(func=lambda message: True)
def default(message):
    random.seed(a=None, version=2)
    bot.send_message(message.chat.id, database.default_phrases[random.randint(0, 9)])
    # Сюди можна прикрутити ChatGPT (зі своїм system prompt), але до цього ми поки не дійшли.


bot.infinity_polling()
