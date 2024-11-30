import json
import csv
import requests

class MetroParsing:

    headers = { #Заголовки для endpoint'a
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Content-Type': 'application/json'
    }

    def __init__(self): #Подгрузка полезной нагрузки
        try:
            with open('payload.json', 'r') as file:
                self.payload = json.load(file)
        except:
            raise 'Ошибка в файле'

    def get_all_items(self, category: str, size: int) -> list: #Получение и возрат всех товаров в одной категории
        if not size:
            return []
        payload = self.payload.copy()
        payload['variables']['slug'] = category
        payload['variables']['size'] = size
        response = requests.post('https://api.metro-cc.ru/products-api/graph', data=json.dumps(payload), headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data['data']['category']['products']:
                return data['data']['category']['products']
            else:
                return []


    def get_products_category(self, category): #Получение количество товаров в категории и получение всех товаров
        payload = self.payload.copy()
        payload['variables']['slug'] = category
        response = requests.post('https://api.metro-cc.ru/products-api/graph', data=json.dumps(payload), headers=self.headers)
        size = 0
        if response.status_code == 200:
            data = response.json()
            if data['data']['category']['total']:
                size = data['data']['category']['total']
        return self.get_all_items(category, size)

    def save_json(self, data: list) -> None: # Сохранение результата в json формат
        data_save_file = []
        for item in data:
            if item['stocks'][0]['value'] == 0:
                continue
            card_item = {
                'id': item['article'],
                'title': item['name'],
                'url': f'https://online.metro-cc.ru{item["url"]}',
            }
            if item['stocks'][0]['prices']['is_promo']:
                card_item['price'] = item['stocks'][0]['prices']['old_price']
                card_item['promo_price'] = item['stocks'][0]['prices']['price']
            else:
                card_item['price'] = item['stocks'][0]['prices']['price']
                card_item['promo_price'] = 0
            card_item['brand'] = item['manufacturer']['name']
            data_save_file.append(card_item)
        try:
            with open('result.json', 'w', encoding='utf-8') as file:
                json.dump(data_save_file, file, indent=4, ensure_ascii=False)
        except Exception as ex:
            print(ex)

    def save_csv(self, data: list) -> None: # Сохранение результата в csv формат
        with open('result.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(('Артикул',
                             'Название товара',
                             'Ссылка',
                             'Цена',
                             'Цена со скидкой',
                             'Бренд'))
            for item in data:
                if item['stocks'][0]['value'] == 0:
                    continue
                card_item = [item['article'],
                             item['name'],
                             f'https://online.metro-cc.ru{item["url"]}',
                             0,
                             0,
                             item['manufacturer']['name']]
                if item['stocks'][0]['prices']['is_promo']:
                    card_item[3] = item['stocks'][0]['prices']['old_price']
                    card_item[4] = item['stocks'][0]['prices']['price']
                else:
                    card_item[3] = item['stocks'][0]['prices']['price']
                    card_item[4] = 0
                writer.writerow(card_item)

if __name__ == '__main__':
    parsing = MetroParsing()
    data = parsing.get_products_category('syry')
    parsing.save_json(data)
    parsing.save_csv(data)