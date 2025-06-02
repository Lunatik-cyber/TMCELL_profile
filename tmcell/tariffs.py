from tmcell.api import parse_tariffs, buy_packet

def handle_tariff_switch(session, headers):
    current_tariff, tariffs = parse_tariffs(session, headers)
    print(f"Ваш текущий тариф: {current_tariff}")
    print("--- Доступные для перехода тарифы ---")
    for idx, t in enumerate(tariffs, 1):
        print(f"{idx}. {t['name']} | Стоимость перехода: {t['price']} | ID: {t['tariff_id']}")
    print("=============================")
    print(" [0] Назад")
    sub_choice = input("Введите номер тарифа для перехода: ").strip()
    if sub_choice == "0":
        return
    try:
        num = int(sub_choice)
    except ValueError:
        print("Некорректный ввод.")
        return
    if num < 1 or num > len(tariffs):
        print("Нет такого тарифа!")
        return
    tariff_id = tariffs[num-1]["tariff_id"]
    from auth.login import login
    csrf_token = login(session, headers, None, None)
    if not csrf_token:
        print("Не удалось получить новый CSRF токен для переключения тарифа.")
        return False
    url = "https://hyzmat.tmcell.tm/Tariff/Edit"
    params = {
        "tariffId": tariff_id
    }
    resp = session.get(url, headers=headers, params=params)
    if resp.status_code == 200 and "ошибка" not in resp.text.lower():
        print("Запрос на переключение тарифа отправлен. Проверьте личный кабинет.")
        return True
    else:
        print("Ошибка при переключении тарифа!")
        return False