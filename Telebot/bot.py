import telebot
import config
import random
import aiogram.types
import requests
import codecs
import datetime
import time
import cresql
import logging
import mysql.connector
from telebot import types
from urllib.request import urlopen
import csv
import re

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",
  database="sabs"
)
mycursor = mydb.cursor()
resmes = ""
bot = telebot.TeleBot(config.TOKEN)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler("RegSubBotLog.log")
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
adr = ["", "", "", "", ""]
us_inf = ["ID: ", "Область: ", "Місто: ",
"Вулиця: ", "Будинок: ", "Квартира: ",
"Стан субсидії: ", "Сума субсидії на місяць\n(Ком. послуги): ", 
"Сума субсидії на рік\n(Газ): ", "Місцезнаходження особистих справ \nодержувачів: ",
"Дата першого призначення: ", "Набрання чинності останньою \nсубсидією: ", 
"Кінець останнього призначення \nсубсидії: ",
"Сума субсидії у неопалювальний \nперіод: ",
"Сума субсидії в опалювальний \nперіод: "]
starttime = "00:00"
endtime = "05:00"

#Виведення привітання та ініціалізація кнопок
@bot.message_handler(commands=['start'])
def welcome(message):
    
    item1 = types.KeyboardButton("Пошук за Адресою")
    item2 = types.KeyboardButton("Створити підписку")
    item3 = types.KeyboardButton("Перевірити підписки")
    item4 = types.KeyboardButton("Про програму")
    item5 = types.KeyboardButton("Про розробника")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(item1).row(item2, item3).row(item4, item5)
    bot.send_message(message.chat.id,
    "Вітаю, {0.first_name}!\nЯ - <b>{1.first_name}</b> - бот, що надасть інформацію про субсидії".format(message.from_user, bot.get_me()),
    parse_mode='html')
    bot.send_message(message.chat.id,
    "Щоб знайти необхідну інформацію потрібно послідовно ввести:\nОбласть\nМісто\nВулицю\nБудінок\nКвартиру".format(message.from_user, bot.get_me()),
    parse_mode='html')
    bot.send_message(message.chat.id,
    "Якщо ви не знаєте всієї необхідної інформації, введіть /stop для завершення ведення інформації".format(message.from_user, bot.get_me()),
    parse_mode='html')
    bot.send_message(message.chat.id,
    "Для початку роботи виберіть Пошук за Адресою:".format(message.from_user, bot.get_me()),
    parse_mode='html', reply_markup=markup)  
    bot.register_next_step_handler(message, GetMessageFromUser)
    logger.info("Work started on id %s" % message.chat.id)

#Очистка списку підписок
@bot.message_handler(commands=['clearsubs'])
def ClearSubs(message):
    sql = "delete from subs where user_id = '%s'" % message.chat.id
    mycursor.execute(sql)
    mydb.commit()
    bot.send_message(message.chat.id, "Список підписок очищено.")
    logger.info("Clear subscriptions for id %s" % message.chat.id)

#Пошук по БД за обмеженою кількістю параметрів
@bot.message_handler(commands=['stop'])
def StopSearch(message):
    myresult = ""
    if adr[4] != "":
        sql = "select * from Item where addressAdminUnit regexp %s and addressPostName = %s and addressThoroughfare = %s and" + \
        " addressLocatorDesignator = %s and addressflat = %s"
        val = (adr[0], adr[1], adr[2], adr[3], adr[4])
        bot.send_message(message.chat.id, "Шукаємо...")
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
    elif adr[3] != "":
        sql = "select * from Item where addressAdminUnit regexp %s and addressPostName = %s and addressThoroughfare = %s and" + \
        " addressLocatorDesignator = %s"
        val = (adr[0], adr[1], adr[2], adr[3])
        bot.send_message(message.chat.id, "Шукаємо...")
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
    elif adr[2] != "":
        sql = "select * from Item where addressAdminUnit regexp %s and addressPostName = %s and addressThoroughfare = %s"
        val = (adr[0], adr[1], adr[2])
        bot.send_message(message.chat.id, "Шукаємо...")
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
    elif adr[1] != "":
        sql = "select * from Item where addressAdminUnit regexp %s and addressPostName = %s "
        val = (adr[0], adr[1])
        bot.send_message(message.chat.id, "Шукаємо...")
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
    elif adr[0] != "":
        sql = "select * from Item where addressAdminUnit regexp %s" % adr[0]
        bot.send_message(message.chat.id, "Шукаємо...")
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
    else:
        bot.send_message(message.chat.id, "Шукаємо...")
    number =len(myresult)
    if number != 0:
        for x in myresult:
            resmes = ""
            a = 0
            for i in x:
                resmes += us_inf[a] 
                resmes += i + "\n"
                a += 1
                time.sleep(10)
            bot.send_message(message.chat.id, resmes)
    else:
        bot.send_message(message.chat.id, "Нажаль нам невдалось нічого знайти.")
    logger.info("Search for id %s" % message.chat.id)

#Первинна обробка повідомлень користувача
@bot.message_handler(content_types=['text'])
def GetMessageFromUser(message):
    if time.strftime("%H:%M") >= starttime and time.strftime("%H:%M") <= endtime and datetime.datetime.now().weekday() == 5:
        if message.chat.id == 429371600 and message.text == 'Оновлення':
            newtab()
            sql = "select user_id from subs group by user_id"
            mycursor.execute(sql)
            myresult = mycursor.fetchall()
            for x in myresult:
                for x1 in x:
                    ViewSUBS(x1)
        else:
            bot.send_message(message.chat.id, 'Проводимо оновлення інформації. \nСпробуйте пізніше')
    else:
        if message.chat.type == 'private':
        
            if message.text == 'Пошук за Адресою' :
                bot.send_message(message.chat.id, 'Введіть область:')
                adr = ["", "", "", "", ""]
                bot.register_next_step_handler(message, Search1)
            elif message.text == 'Створити підписку' :
                bot.send_message(message.chat.id, 'Введіть область:')
                adr = ["", "", "", "", ""]
                bot.register_next_step_handler(message, SUBSearch1)
            elif message.text == 'Перевірити підписки' :
                ViewSUBS(message.chat.id)
            elif message.text == 'Про програму' :
                bot.send_message(message.chat.id, 'Бот створено для отримання інформації про субсидії')
                welcome(message)
            elif message.text == 'Про розробника' :
                bot.send_message(message.chat.id, 'Виконай студент групи 535Б\nПерепечай Дмитро')
                welcome(message)
            else:
                welcome(message)

#Введення критерію пошуку – область
@bot.message_handler(content_types=['text'])
def Search1(message):
    if message.text != "/stop":
        adr[0] = message.text
        adr[0] = adr[0].upper()
        bot.send_message(message.chat.id, 'Введіть місто:')
        bot.register_next_step_handler(message, Search2)
    else:
        bot.send_message(message.chat.id, 'Недостатньо даних.')
        bot.register_next_step_handler(message, GetMessageFromUser)
#Введення критерію пошуку – місто
@bot.message_handler(content_types=['text'])
def Search2(message):
    if message.text != "/stop":
        adr[1] = message.text
        adr[1] = adr[1].upper()
        bot.send_message(message.chat.id, 'Введіть вулицю:')
        bot.register_next_step_handler(message, Search3)
    else:
        StopSearch(message)
#Введення критерію пошуку – вулиця
@bot.message_handler(content_types=['text'])
def Search3(message):
    if message.text != "/stop":
        adr[2] = message.text
        adr[2] = adr[2].upper()
        bot.send_message(message.chat.id, 'Введіть будинок:')
        bot.register_next_step_handler(message, Search4)
    else:
        StopSearch(message)
#Введення критерію пошуку – будинок
@bot.message_handler(content_types=['text'])
def Search4(message):
    if message.text != "/stop":
        adr[3] = message.text
        bot.send_message(message.chat.id, 'Введіть квартиру:')
        bot.register_next_step_handler(message, StartSearch)
    else:
        StopSearch(message)
#Введення критерію пошуку – квартира, і початок процесу пошуку за всіма параметрами
@bot.message_handler(content_types=['text'])
def StartSearch(message):
    if message.text != "/stop":
        adr[4] = message.text
        bot.send_message(message.chat.id, "Шукаємо...")
        sql = "select * from Item where addressAdminUnit regexp %s and addressPostName = %s and addressThoroughfare = %s and" + \
        " addressLocatorDesignator = %s and addressflat = %s"
        val = (adr[0], adr[1], adr[2], adr[3], adr[4])
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        number =len(myresult)
        if number != 0:
            for x in myresult:
                resmes = ""
                a = 0
                for i in x:
                    resmes += us_inf[a] 
                    resmes += i + "\n"
                    a += 1
                bot.send_message(message.chat.id, resmes)
        else:
            bot.send_message(message.chat.id, "Нажаль нам невдалось нічого знайти.")
    else:
        StopSearch(message)   
    logger.info("Search for id %s" % message.chat.id)        

#Введення критерію для підписки – область
@bot.message_handler(content_types=['text'])
def SUBSearch1(message):
    if message.text != "/stop":
        adr[0] = message.text
        adr[0] = adr[0].upper()
        bot.send_message(message.chat.id, 'Введіть місто:')
        bot.register_next_step_handler(message, SUBSearch2)
    else:
        bot.send_message(message.chat.id, 'Недостатньо даних.')
        bot.send_message(message.chat.id, 'Введіть область:')
        bot.register_next_step_handler(message, SUBSearch1)
#Введення критерію для підписки – місто
@bot.message_handler(content_types=['text'])
def SUBSearch2(message):
    if message.text != "/stop":
        adr[1] = message.text
        adr[1] = adr[1].upper()
        bot.send_message(message.chat.id, 'Введіть вулицю:')
        bot.register_next_step_handler(message, SUBSearch3)
    else:
        bot.send_message(message.chat.id, 'Недостатньо даних.')
        bot.send_message(message.chat.id, 'Введіть місто:')
        bot.register_next_step_handler(message, SUBSearch2)
#Введення критерію для підписки – вулиця
@bot.message_handler(content_types=['text'])
def SUBSearch3(message):
    if message.text != "/stop":
        adr[2] = message.text
        adr[2] = adr[2].upper()
        bot.send_message(message.chat.id, 'Введіть будинок:')
        bot.register_next_step_handler(message, SUBSearch4)
    else:
        bot.send_message(message.chat.id, 'Недостатньо даних.')
        bot.send_message(message.chat.id, 'Введіть вулицю:')
        bot.register_next_step_handler(message, SUBSearch3)
#Введення критерію для підписки – будинок
@bot.message_handler(content_types=['text'])
def SUBSearch4(message):
    if message.text != "/stop":
        adr[3] = message.text
        bot.send_message(message.chat.id, 'Введіть квартиру:')
        bot.register_next_step_handler(message, SUBStartSearch)
    else:
        bot.send_message(message.chat.id, 'Недостатньо даних.')
        bot.send_message(message.chat.id, 'Введіть вулицю:')
        bot.register_next_step_handler(message, SUBSearch4)
#Введення критерію для підписки – квартира, і створення підписки
@bot.message_handler(content_types=['text'])
def SUBStartSearch(message):
    if message.text != "/stop":
        adr[4] = message.text
        sql = "insert subs(user_id, addressAdminUnit, addressPostName," + \
            " addressThoroughfare, addressLocatorDesignator, addressflat) value ('%s', %s, %s, %s, %s, %s)"
        val = (message.chat.id, adr[0], adr[1], adr[2], adr[3], adr[4])
        mycursor.execute(sql, val)
        mydb.commit()
        bot.send_message(message.chat.id, "Підписку успішно створено.")
    else:
        adr[4] = message.text
        sql = "insert subs(user_id, addressAdminUnit, addressPostName," + \
            " addressThoroughfare, addressLocatorDesignator) value ('%s', %s, %s, %s, %s)"
        val = (message.chat.id, adr[0], adr[1], adr[2], adr[3])
        mycursor.execute(sql, val)
        mydb.commit()
        bot.send_message(message.chat.id, "Підписку успішно створено.")  
    logger.info("Subscription created for id %s" % message.chat.id)        

#Перевірка підписок
@bot.message_handler(content_types=['text'])
def ViewSUBS(us_id):
    sql = "select * from subs where user_id = '%s'" % (us_id)
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    number =len(myresult)
    if number != 0:
        bot.send_message(us_id, "Опрацьовуємо дані...")
        for x in myresult:
            n = 0
            adr = ["", "", "", "", ""]
            for i in x:
                if n > 0:
                    adr[n - 1] = i
                n += 1
            if adr[4] != None:
                sql2 = "select * from Item where addressAdminUnit regexp %s and addressPostName = %s and addressThoroughfare = %s and" + \
                        " addressLocatorDesignator = %s and addressflat = %s"
                val2 = (adr[0], adr[1], adr[2], adr[3], adr[4])
                mycursor.execute(sql2, val2)
                myresult2 = mycursor.fetchall()
                number2 =len(myresult2)
                if number2 != 0:
                    bot.send_message(us_id, "Шукаємо...")
                    for a in myresult2:
                        resmes = ""
                        a1 = 0
                        for b in a:
                            resmes += us_inf[a1] 
                            resmes += b + "\n"
                            a1 += 1
                        bot.send_message(us_id, resmes)
                else:
                    bot.send_message(us_id, "Нажаль нам невдалось нічого знайти.")
            else:
                sql2 = "select * from Item where addressAdminUnit = %s and addressPostName = %s and addressThoroughfare = %s and" + \
                        " addressLocatorDesignator = %s"
                val2 = (adr[0], adr[1], adr[2], adr[3])
                mycursor.execute(sql2, val2)
                myresult2 = mycursor.fetchall()
                number2 =len(myresult2)
                if number2 != 0:
                    bot.send_message(us_id, "Шукаємо...")
                    for a in myresult2:
                        resmes = ""
                        a1 = 0
                        for b in a:
                            resmes += us_inf[a1] 
                            resmes += b + "\n"
                            a1 += 1
                        bot.send_message(us_id, resmes)
                else:
                    bot.send_message(us_id, "Нажаль нам невдалось нічого знайти.")

    else:
        bot.send_message(us_id, "Нажаль нам невдалось нічого знайти.")
    logger.info("Search for id %s" % us_id)

#Запуск оновлення бази даних
def newtab():
    mydb.disconnect()
    cresql.job()
    mydb.connect()
    
bot.polling(none_stop=True)