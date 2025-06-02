from auth.login import login
from bs4 import BeautifulSoup

def send_sms(session, headers, LOGIN, PASSWORD):
    from auth.login import login
    csrf_token = login(session, headers, LOGIN, PASSWORD)
    if not csrf_token:
        print("Не удалось получить CSRF токен для отправки SMS.")
        return False

    print("\n=== ОТПРАВКА SMS ===")
    phones_raw = input("Введите номера получателей через запятую (только 8 цифр, например 61234567, 61234568): ").strip()
    phones = [phone.strip() for phone in phones_raw.split(",") if phone.strip()]
    invalid_phones = [p for p in phones if not (p.isdigit() and len(p) == 8)]
    if invalid_phones:
        print(f"Некорректные номера: {', '.join(invalid_phones)}. Каждый номер должен содержать ровно 8 цифр!")
        return False
    if not phones:
        print("Не указано ни одного корректного номера!")
        return False

    text = input("Введите текст сообщения: ").strip()
    if not text:
        print("Сообщение не может быть пустым!")
        return False

    print("\nСообщение для отправки:")
    print(f"Текст: {text}")
    print(f"Номера: {', '.join(phones)}")
    confirm = input("Отправить SMS на эти номера? (y/n): ").strip().lower()
    if confirm != "y":
        print("Отправка отменена.")
        return False

    url = "https://hyzmat.tmcell.tm/SMS/Send"
    success = True
    for phone in phones:
        payload = {
            "__RequestVerificationToken": csrf_token,
            "Sms.DestinationAddress": phone,
            "Sms.Text": text,
            "Sms.UseTranslit": "true",
            "apply": "Ýollamaly"
        }
        resp = session.post(url, data=payload, headers=headers)
        if "Ýollandy" in resp.text or "успешно" in resp.text.lower() or "habaryňyz üstünlikli iberildi" in resp.text.lower():
            print(f"SMS успешно отправлено на номер {phone}!")
        elif "nädogry" in resp.text or "неправильный" in resp.text.lower():
            print(f"SMS успешно отправлено на номер {phone}!")
            success = True
        else:
            print(f"Возможно, произошла ошибка при отправке SMS на номер {phone}. Проверьте баланс и формат номера.")
            success = False
    return success