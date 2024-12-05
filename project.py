# -*- coding: utf-8 -*-

import os
import csv
import json
from operator import itemgetter  # для json сортировки

directory = os.getcwd()


class PriceMachine:

    def __init__(self):
        self.out_file = 'tmp_file.csv'
        self.out_header = ['Наименование', 'цена', 'вес', 'файл', 'цена за кг.']

        self.name = {'название', 'продукт', 'товар', 'наименование'}
        self.price = {'цена', 'розница'}
        self.weight = {'фасовка', 'масса', 'вес'}

        self.product_data = {}

    def load_prices(self, in_file):
        """
            В очередном файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка

            Добавляет данные из текущего файла в промежуточныей файл tmp_file.csv для
            последующей сортировки.
        """
        with open(in_file, 'r') as file:
            reader = csv.DictReader(file)
            header = set(next(reader))

            name_tmp = list(header & self.name)[0]
            price_tmp = list(header & self.price)[0]
            weight_tmp = list(header & self.weight)[0]

            if name_tmp and price_tmp and weight_tmp:  # проверка на наличие нужных колонок

                with open(self.out_file, 'a', newline='') as out_csv:
                    writer = csv.writer(out_csv, delimiter=',')

                    for row in reader:  # берем и сохраняем только нужные колонки
                        price_kg = round(float(row[price_tmp]) / float(row[weight_tmp]), 1)
                        outrow = [row[name_tmp], row[price_tmp], row[weight_tmp], in_file, price_kg]
                        writer.writerow(outrow)

    def export_to_html(self, data, fname='output.html'):
        # Выгружает данные из набора входных csv файлов в html файл,
        # где они хранятся в отсортированном по полю 'цена за кг.' виде.

        self.data = data
        self.result = '''
        <!DOCTYPE html>
        <html>
        <head>
        <title> Позиции продуктов </title>
        </head>
        <body>
        <table>
        <tr>
        <th>Номер</th>
        <th>Название</th>
        <th>Цена</th>
        <th>Фасовка</th>
        <th>Файл </th>
        <th>Цена за кг.</th>
        </tr>
        '''
        for number, item in enumerate(data):
            product_name, price, weight, file_name, price_kg = item.values()

            self.result += '<tr>'
            self.result += f'<td>{number + 1}</td>'
            self.result += f'<td>{product_name}</td>'
            self.result += f'<td>{price}</td>'
            self.result += f'<td>{weight}</td>'
            self.result += f'<td>{file_name}</td>'
            self.result += f'<td>{price_kg}</td>'
            self.result += '</tr>\n'

        self.result += '</table></body></html>'

        out_html = open(fname, 'w')
        out_html.write(self.result)
        out_html.close()

    def sorting(self, csv_file):
        # Сортировка данных по полю "Цена за кг."

        self.data_list = []

        # Открываем временный csv файл, где хранятся промежуточные данные
        with open(csv_file, encoding='utf-8') as file:
            csvRead = csv.DictReader(file)

            # Преобразуем последний столбик в числовой формат для последующей сортировки
            for rows in csvRead:
                rows['цена за кг.'] = float(rows['цена за кг.'])
                self.data_list.append(rows)

            sorted_data = json.dumps(sorted(self.data_list, key=itemgetter('цена за кг.')),
                                     indent=4, ensure_ascii=False)
            sorted_data_list = json.loads(sorted_data)

            return sorted_data_list

    def find_text(self, data):
        # Получает данные из промежуточного файла и возвращает список позиций, содержащий введенный пользователем текст
        # в названии продукта.
        # Список выводится в виде таблицы отсортированной по возрастанию стоимости за килограмм.
        # Цикл обмена с пользователем завершается при вводе "exit".
        while True:
            count = 0
            keep_text = input('Введите строку для поиска:')
            in_text = keep_text.lower()
            if in_text == 'exit':
                break
            print()
            print('№   Наименование             цена   вес   файл          цена за кг.')
            for row in data:
                if in_text in row['Наименование'].lower():
                    count += 1
                    print(count, '\t', row['Наименование'], '\t\t\t', row['цена'], '\t', row['вес'], '\t',
                          row['файл'], '\t', row['цена за кг.'])
            if not count:
                print(f'По запросу \"{keep_text}\" ничего не найдено.')

# =============================


analizer = PriceMachine()

'''
    Логика работы программы
'''

# Создает временный файл для хранения промежуточных данных в режиме добавления.
# В первой строке - заголовки
with open(analizer.out_file, 'w', newline='') as out_csv:
    writer = csv.writer(out_csv, delimiter=',')
    writer.writerow(analizer.out_header)

# Сканирует текущий каталог. Ищет файлы со словом price в названии.
for root, dirs, files in os.walk(directory):
    if directory == root:
        for file in files:
            if 'price' in file and '.csv' in file:
                analizer.load_prices(in_file=file)

data = analizer.sorting(csv_file='tmp_file.csv')
analizer.export_to_html(data)
analizer.find_text(data)
