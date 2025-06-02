from auth.login import login
from bs4 import BeautifulSoup

def send_sms(session, headers, LOGIN, PASSWORD):
    csrf_token = login(session, headers, LOGIN, PASSWORD)
    if not csrf_token:
        print("Не удалось получить CSRF токен для отправки SMS.")
        return False

    print("\n=== ОТПРАВКА SMS ===")
    phone = input("Введите номер получателя (только 8 цифр, например 61234567): ").strip()
    if not phone.isdigit() or len(phone) != 8:
        print("Номер должен содержать ровно 8 цифр!")
        return False
    text = input("Введите текст сообщения: ").strip()
    if not text:
        print("Сообщение не может быть пустым!")
        return False
    use_translit = input("Использовать транслитерацию? (y/n, Enter = нет): ").strip().lower() == "y"
    
    url = "https://hyzmat.tmcell.tm/SMS/Send"
    payload = {
        "__RequestVerificationToken": csrf_token,
        "Sms.DestinationAddress": phone,
        "Sms.Text": text,
        "Sms.UseTranslit": "true" if use_translit else "false",
        "apply": "Ýollamaly"
    }
    resp = session.post(url, data=payload, headers=headers)
    if "Ýollandy" in resp.text or "успешно" in resp.text.lower():
        print("SMS успешно отправлено!")
        return True
    elif "nädogry" in resp.text or "неправильный" in resp.text.lower():
        print("SMS успешно отправлено!")
        return False
    elif "habaryňyz üstünlikli iberildi" in resp.text.lower():
        print("SMS успешно отправлено!")
        return True
    else:
        print("Возможно, произошла ошибка при отправке SMS. Проверьте баланс и формат номера.")
        return False