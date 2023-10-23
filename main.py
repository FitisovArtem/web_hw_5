import aiohttp
import asyncio
import datetime
import json
import platform
import sys

currency_list = ['USD', 'EUR']
rez = []
DEFAULT_URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
WITH_DATE_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='


async def main(day=None):
    if day is None or day == 0:
        r = await make_request(DEFAULT_URL)
        await make_answer(r, default=True)
    else:
        now = datetime.date.today()
        while day > 0:
            day_to_request = (now - datetime.timedelta(days=day)).strftime('%d.%m.%Y')
            try:
                r = await make_request(WITH_DATE_URL + day_to_request)
                await make_answer(r)
            except HttpError as err:
                print(err)
                return None
            day -= 1
    return str(rez)


async def make_answer(resp, default=None):
    cur_element = {}
    if default is None:
        for el in resp['exchangeRate']:
            for element in currency_list:
                if el['currency'] == element:
                    try:
                        cur_element.update({element: {"sale": el['saleRate'], "purchase": el['purchaseRate']}})
                    except KeyError:
                        cur_element.update({element: {"sale": "No data", "purchase": "No data"}})
        rez.append({resp.get("date"): cur_element})
    else:
        for el in resp:
            for element in currency_list:
                if el['ccy'] == element:
                    cur_element.update({element: {"sale": el['sale'], "purchase": el['buy']}})
        rez.append({datetime.date.today().strftime('%d.%m.%Y'): cur_element})
    return True


class HttpError(Exception):
    pass


async def make_request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    res = await response.json()
                    return res
                else:
                    raise HttpError(f"Error request to API Privatbank, status: {response.status}")
        except Exception as err:
            raise HttpError(f"Connection ERROR: {err}")


def start(days=0):
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    answer = asyncio.run(main(days))
    res = json.dumps(answer, indent=4, sort_keys=True)
    return res


if __name__ == "__main__":
    try:
        if sys.argv[1]:
            if 0 <= int(sys.argv[1]) <= 10:
                if len(sys.argv[2:]) > 0:

                    # Достаем все валюты переданные дополнительно
                    curr = [x.upper() for x in sys.argv[2:]]

                    # добавляем валюты и проверяем на дубликаты в "currency_list"
                    [currency_list.append(i) for i in curr if i not in currency_list]

                print(f'''Виконую запит до Приватбанк на отримання курсів валют за вказану кількість днів
    по валютам: {currency_list}''')
                result = start(int(sys.argv[1]))
                print(result)
            else:
                print("Кількість днів має бути додатним числом але не більше '10'")
    except IndexError:
        result = start()
        print(result)
    except ValueError:
        print("Додайте до виклику число (максимальне: '10')- кількість днів за яку Вам потрібний курс валют")
