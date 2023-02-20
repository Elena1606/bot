from database import creating_database
from keyboard import sender
from main import *


for event in bot.longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = str(event.user_id)
        msg = event.text.lower()
        sender(user_id, msg.lower())
        if request == 'поиск':
            creating_database()
            bot.find_user(user_id)
            bot.write_msg(event.user_id, f'Посмотри, кого я нашёл!')
            bot.find_persons(user_id, offset)

        elif request == 'привет':
            bot.write_msg(user_id, f'Привет, {bot.name(user_id)}. Жми кнопку "Поиск"')
        elif request == 'пока':
            bot.write_msg(user_id, f'До встречи! Я буду ждать тебя тут.')
        elif request == 'как дела?':
            bot.write_msg(user_id, f'Отлично, надеюсь, что и у Вас тоже! Давайте посмотрим, кого я для Вас нашел!  Нажмите на кнопку "Поиск".')

        elif request == 'дальше':
            for i in line:
                offset += 1
                bot.find_persons(user_id, offset)
                break

        else:
            bot.write_msg(event.user_id, 'Я тебя не понимаю')
