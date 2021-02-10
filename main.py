from __future__ import division
from __future__ import print_function
import telebot
from telebot import *
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

src = ""

bot = telebot.TeleBot('API_TOKEN')


@bot.message_handler(commands=['zadacha_2'])
def start_z2(message):
    sent = bot.send_message(message.chat.id, 'A, B = ')
    bot.register_next_step_handler(sent, z_2)


@bot.message_handler(commands=['zadacha_1'])
def start_z1(message):
    sent = bot.send_message(message.chat.id, 'A, B = ')
    bot.register_next_step_handler(sent, z_1)


def z_2(message):
    tmp = []
    file_name = src
    data = pd.read_excel(file_name)
    used_index_list = []
    first_tabel, second_tabel = map(int, message.text.split(','))
    current_index = -1
    first_index = -1
    second_index = -1
    allowed_age_difference = 5
    step_count = 10

    # Закоментил для более быстрого теста

    headers = list(data.columns.ravel())
    columns_weight = [1] * len(headers)

    for index in range(len(data['№'])):
        if data['Табельный номер'][index] == first_tabel:
            first_index = index
            used_index_list.append(first_index)
            bot.send_message(message.chat.id,
                             "Табельный номер: " + str(
                                 first_tabel) + " | " + "ФИО: " + str(
                                 data['ФИО'][first_index]))
        if data['Табельный номер'][index] == second_tabel:
            second_index = index
            used_index_list.append(second_index)
            current_index = index

    for i in range(step_count - 1):
        max_weight = 0
        closest_person_index = -1

        for index in range(len(data['№'])):
            current_weight = 0
            for column in data:

                if column == '№' or column == 'Табельный номер' or column == 'ФИО' or column == 'Пол':
                    continue

                elif column == 'Дата рождения':
                    time_delta = abs(data['Дата рождения'][current_index] - data['Дата рождения'][index])
                    if time_delta.days <= 366 * allowed_age_difference:
                        current_weight += 1 * columns_weight[headers.index(column)]

                else:
                    if data[column][index] == data[column][current_index] \
                            and data[column][index] != "-" and index not in used_index_list:
                        current_weight += 1  # * columns_weight[headers.index(column)]

            if current_weight >= max_weight:
                max_weight = current_weight
                closest_person_index = index
        tmp.append(data['Табельный номер'][closest_person_index])
        bot.send_message(message.chat.id,
                         "Табельный номер: " + str(
                             data['Табельный номер'][closest_person_index]) + " | " + "ФИО: " + str(
                             data['ФИО'][closest_person_index]))
        used_index_list.append(closest_person_index)
        current_index = closest_person_index

    # Новое -----------------------------------------------------------------------------
    # Сделал вывод в более удобном виде (Табельный номер и ФИО)
    # Добавил импут, чтобы граф сразу не выскакивал

    bot.send_message(message.chat.id, "Количество замешанных сотрудников: " + str(len(used_index_list)))

    G = nx.DiGraph()
    # explicitly set positions
    pos = {}
    w, h = 0, 0
    delta = 1000
    flag = True
    for number in data['Табельный номер']:
        pos[number] = (h, w)
        if flag:
            if w + delta < 10000:
                w += delta
            else:
                flag = False
        else:
            h += 2 * delta
            if w - delta >= 0:
                w -= delta
            else:
                flag = True

    # Plot nodes with different properties for the "wall" and "roof" nodes
    nx.draw_networkx_nodes(
        G, pos, node_size=10, nodelist=pos, node_color="tab:blue"
    )
    nx.draw_networkx_nodes(G, pos, node_size=100, nodelist=tmp, node_color="tab:orange")
    nx.draw_networkx_nodes(G, pos, node_size=100, nodelist=[first_tabel, second_tabel], node_color="tab:red")
    for i in range(len(used_index_list) - 1):
        G.add_edge(data['Табельный номер'][used_index_list[i]], data['Табельный номер'][used_index_list[i + 1]])
    nx.draw_networkx_edges(G, pos, width=1,
                           arrowstyle="->",
                           arrowsize=10,
                           )
    dict_labels = {first_tabel: first_tabel, second_tabel: second_tabel}
    nx.draw_networkx_labels(G, pos, labels=dict_labels, font_size=10)
    plt.tight_layout()
    plt.axis("off")
    plt.savefig("path2.png")
    bot.send_photo(message.chat.id, photo=open("example/path2.png", 'rb'))
    plt.close()
    G = nx.path_graph(len(used_index_list))
    nx.draw(G)
    plt.savefig("path3.png")
    bot.send_photo(message.chat.id, photo=open("example/path3.png", 'rb'))
    bot.send_message(message.chat.id, "Решение получено!")


def z_1(message):
    tmp = []
    start_tabel, finish_tabel = map(int, message.text.split(','))
    bot.send_message(message.chat.id, 'Запускаем решение вашей задачи!\nПожалуйста, подождите...')
    file_name = src
    data = pd.read_excel(file_name)
    used_index_list = []
    current_index = -1
    finish_index = -1

    allowed_age_difference = 5

    headers = list(data.columns.ravel())
    columns_weight = [1] * len(headers)

    for index in range(len(data['№'])):
        if data['Табельный номер'][index] == start_tabel:
            current_index = index
            used_index_list.append(current_index)
            bot.send_message(message.chat.id,
                             "Табельный номер: " + str(
                                 start_tabel) + " | " + "ФИО: " + str(
                                 data['ФИО'][current_index]))
        if data['Табельный номер'][index] == finish_tabel:
            finish_index = index

    while current_index != finish_index:
        max_weight = 0
        closest_person_index = -1

        for index in range(len(data['№'])):
            current_weight = 0
            for column in data:

                # Новое -------------------------------------------------------------------------------
                # Скипаю ненужные значения (Табель, ФИО, ID, Пол) и проверяю разнцу в возрасте

                if column == '№' or column == 'Табельный номер' or column == 'ФИО' or column == 'Пол':
                    continue

                elif column == 'Дата рождения':
                    time_delta = abs(data['Дата рождения'][current_index] - data['Дата рождения'][index])
                    if time_delta.days <= 366 * allowed_age_difference:
                        current_weight += 1 * columns_weight[headers.index(column)]

                else:
                    if data[column][index] == data[column][current_index] \
                            and data[column][index] != "-" and index not in used_index_list:
                        # Закоментил для быстрого теста
                        current_weight += 1 * columns_weight[headers.index(column)]
                # -------------------------------------------------------------------------------------

            if current_weight >= max_weight:
                max_weight = current_weight
                closest_person_index = index

        tmp.append(data['Табельный номер'][closest_person_index])
        bot.send_message(message.chat.id,
                         "Табельный номер: " + str(
                             data['Табельный номер'][closest_person_index]) + " | " + "ФИО: " + str(
                             data['ФИО'][closest_person_index]))
        used_index_list.append(closest_person_index)
        current_index = closest_person_index

    # Новое -----------------------------------------------------------------------------
    bot.send_message(message.chat.id, "Количество замешанных сотрудников: " + str(len(used_index_list)))
    # -----------------------------------------------------------------------------------

    G = nx.DiGraph()
    # explicitly set positions
    pos = {}
    w, h = 0, 0
    delta = 1000
    flag = True
    for number in data['Табельный номер']:
        pos[number] = (h, w)
        if flag:
            if w + delta < 10000:
                w += delta
            else:
                flag = False
        else:
            h += 2 * delta
            if w - delta >= 0:
                w -= delta
            else:
                flag = True

    # Plot nodes with different properties for the "wall" and "roof" nodes
    nx.draw_networkx_nodes(
        G, pos, node_size=10, nodelist=pos, node_color="tab:blue"
    )
    nx.draw_networkx_nodes(G, pos, node_size=100, nodelist=tmp, node_color="tab:orange")
    nx.draw_networkx_nodes(G, pos, node_size=100, nodelist=[start_tabel, finish_tabel], node_color="tab:red")
    for i in range(len(used_index_list) - 1):
        G.add_edge(data['Табельный номер'][used_index_list[i]], data['Табельный номер'][used_index_list[i + 1]])
    nx.draw_networkx_edges(G, pos, width=1,
                           arrowstyle="->",
                           arrowsize=10,
                           )
    dict_labels = {start_tabel: start_tabel, finish_tabel: finish_tabel}
    nx.draw_networkx_labels(G, pos, labels=dict_labels, font_size=10)
    plt.tight_layout()
    plt.axis("off")
    plt.savefig("path.png")
    bot.send_photo(message.chat.id, photo=open("example/path.png", 'rb'))
    plt.close()
    G = nx.path_graph(len(used_index_list))
    nx.draw(G)
    plt.savefig("path1.png")
    bot.send_photo(message.chat.id, photo=open("example/path1.png", 'rb'))
    bot.send_message(message.chat.id, "Решение получено!")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global src
    if message.text == "/start":
        bot.send_message(message.from_user.id, "HackAtom:Графство")
        # Готовим кнопки
        keyboard = types.InlineKeyboardMarkup()
        # По очереди готовим текст и обработчик для каждого знака зодиака
        key_about_todo = types.InlineKeyboardButton(text='What can this bot do?', callback_data='about_todo')
        # И добавляем кнопку на экран
        keyboard.add(key_about_todo)
        key_about_author = types.InlineKeyboardButton(text='About authors', callback_data='about_author')
        keyboard.add(key_about_author)
        key_todo = types.InlineKeyboardButton(text='Send xlsx file', callback_data='todo')
        keyboard.add(key_todo)
        # Показываем все кнопки сразу и пишем сообщение о выборе
        bot.send_message(message.from_user.id, text='Choose what do you want to know/do: ', reply_markup=keyboard)
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Type /start")
    else:
        bot.send_message(message.from_user.id, "I don't understand you\nType /help")


@bot.message_handler(content_types=['document'])
def get_doc(message):
    global src
    try:
        file_name = message.document.file_name
        file_id = message.document.file_name
        file_id_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_id_info.file_path)
        src = file_name
        save_dir = '/Users/mihailmurunov/PycharmProjects/SaladBowlBot'
        with open(save_dir + "/" + src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_animation(message.from_user.id,
                           animation='https://media2.giphy.com/media/cfuL5gqFDreXxkWQ4o/giphy.gif')
        keyboard = types.InlineKeyboardMarkup()
        # По очереди готовим текст и обработчик для каждого знака зодиака
        key_z1 = types.InlineKeyboardButton(text='ЗАДАЧА 1', callback_data='z1')
        # И добавляем кнопку на экран
        keyboard.add(key_z1)
        key_z2 = types.InlineKeyboardButton(text='ЗАДАЧА 2', callback_data='z2')
        keyboard.add(key_z2)
        key_z3 = types.InlineKeyboardButton(text='ЗАДАЧА 3', callback_data='z3')
        keyboard.add(key_z3)
        # Показываем все кнопки сразу и пишем сообщение о выборе
        bot.send_message(message.from_user.id, text='Choose a current task:', reply_markup=keyboard)
    except Exception as ex:
        bot.send_message(message.chat.id, "[!] error - {}".format(str(ex)))


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global src
    # Если нажали на одну из 3 кнопок — выводим соотствующее
    if call.data == "about_todo":
        # Формируем сообщение
        msg = "I can analyze your xlsx file to connect two person"
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
    if call.data == "about_author":
        # Формируем сообщение
        msg = "This bot was made by mt19937"
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
    if call.data == "todo":
        # Формируем сообщение
        msg = "Waiting for your xlsx file..."
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)
    if call.data == "z1":
        bot.send_message(call.message.chat.id, "Сотрудник А организации (сотрудник с табельным номером 50202) "
                                               "получил доступ к коммерческой тайне на бумажном носителе. "
                                               "Через некоторое время сотрудниками службы безопасности организации "
                                               "был выявлен факт передачи коммерческой тайны сотрудником Б "
                                               "(сотрудник с табельным номером 50404) неопределённому лицу."
                                               " Сотрудники A и Б совершенно незнакомы."
                                               "Необходимо определить наиболее вероятный путь документа "
                                               "с коммерческой тайной от сотрудника A до сотрудника Б.")
        bot.send_message(call.message.chat.id, "Чтобы запустить решение введите /zadacha_1")
    if call.data == "z2":
        bot.send_message(call.message.chat.id, "С помощью камер видеонаблюдения сотрудники службы безопасности выявили"
                                               " факт передачи конфиденциальной информации на бумажном "
                                               "носителе сотрудником "
                                               "А (сотрудник с табельным номером 50445) сотруднику Б "
                                               "(сотрудник с табельным номером 50246)."
                                               " К сожалению, при выяснении обстоятельств произошедшего у сотрудника Б"
                                               " бумажного носителя уже не оказалось."
                                               " Сотрудник Б отказался сотрудничать, однако сообщил, "
                                               "что передал документ коллеге по работе."
                                               "Необходимо определить вероятную «точку выхода» (то есть сотрудника)"
                                               " документа за периметр организации с определённым количеством шагов"
                                               " передачи документа (от 1 до 10).")
        bot.send_message(call.message.chat.id, "Чтобы запустить решение введите /zadacha_2")
    if call.data == "z3":
        bot.send_message(call.message.chat.id, "Запускаем решение второй задачи для вашей таблицы...")


bot.polling(none_stop=True, interval=0)
