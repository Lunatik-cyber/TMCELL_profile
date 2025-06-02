from tmcell.api import parse_payment_history

def handle_payments_history(session, headers):
    import datetime
    today = datetime.date.today()
    first_day = today.replace(day=1)
    print(f"Введите даты периода для истории платежей (dd.mm.yyyy).")
    s_date = input(f"Дата начала (Enter для {first_day.strftime('%d.%m.%Y')}): ").strip()
    e_date = input(f"Дата конца (Enter для {today.strftime('%d.%m.%Y')}): ").strip()
    if not s_date:
        s_date = first_day.strftime('%d.%m.%Y')
    if not e_date:
        e_date = today.strftime('%d.%m.%Y')
    payments = parse_payment_history(session, headers, s_date, e_date)
    print(f"--- История платежей с {s_date} по {e_date} ---")
    if not payments:
        print("Нет платежей за выбранный период.")
    else:
        for idx, p in enumerate(payments, 1):
            print(f"{idx}. {p['date']} | {p['amount']} | {p['type']} | {p['dealer']} | Налог: {p['tax']}")
    print("=============================")
    input("Нажмите Enter чтобы вернуться в меню...")