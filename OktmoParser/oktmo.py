import os
import re
import csv
import json
import requests


class OktmoParser:

    def __init__(self):
        self.url = 'https://rosstat.gov.ru/opendata/7708234640-oktmo'
        self.file_name = 'data.csv'

    def parse_oktmo(self, start_keyword, end_keyword):

        response = requests.get(self.url)

        if response.status_code == 200:

            match = re.search(r'<a href="(https://rosstat\.gov\.ru/opendata/7708234640-oktmo/data-[^\"]+)"', response.text)

            if match:
                download_url = match.group(1)
                print(f'Найдена ссылка для скачивания: {download_url}')

                file_response = requests.get(download_url)

                if file_response.status_code == 200:

                    os.makedirs('data/csv/', exist_ok=True)
                    with open('data/csv/' + self.file_name, 'wb') as f:
                        f.write(file_response.content)
                    print('Файл успешно загружен, формирую результат в формате JSON')

                    encoding = 'windows-1251'
                    data_found = False
                    result_data = {}
                    try:
                        with open('data/csv/data.csv', newline='', encoding=encoding) as csvfile:
                            csvreader = csv.reader(csvfile, delimiter=';')

                            for row in csvreader:
                                if start_keyword and end_keyword:
                                    if row[6] == start_keyword:
                                        data_found = True
                                    elif row[6] == end_keyword:
                                        data_found = False
                                        break
                                    if data_found and row[6] != end_keyword:
                                        oktmo_code = row[0] + ' ' + row[1] + ' ' + row[2]
                                        if row[3] != '000':
                                            oktmo_code += ' ' + row[3]
                                        settlement_name = row[6]
                                        result_data[settlement_name] = {
                                            'ОКТМО': oktmo_code,
                                            'КЧ': row[4]
                                        }
                                else:
                                    oktmo_code = row[0] + ' ' + row[1] + ' ' + row[2]
                                    if row[3] != '000':
                                        oktmo_code += ' ' + row[3]
                                    settlement_name = row[6]
                                    result_data[settlement_name] = {
                                        'ОКТМО': oktmo_code,
                                        'КЧ': row[4]
                                    }

                    except UnicodeDecodeError:
                        print(f'Не удалось прочитать файл с кодировкой {encoding}')

                    os.makedirs('data/json/', exist_ok=True)
                    with open('data/json/result.json', 'w', encoding='utf-8') as json_file:
                        json.dump(result_data, json_file, ensure_ascii=False, indent=4)
                        print('Готово')
                else:
                    print('Не удалось загрузить файл')
            else:
                print('Ссылка на файл не найдена')
        else:
            print('Не удалось получить доступ к странице')
