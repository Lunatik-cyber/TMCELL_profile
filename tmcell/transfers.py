from tmcell.api import parse_funds_transfer_history

def handle_transfers_history(session, headers):
    import datetime
    today = datetime.date.today()
    first_day = today.replace(day=1)
    print(f"Введите даты периода для истории переводов (dd.mm.yyyy).")
    s_date = input(f"Дата начала (Enter для {first_day.strftime('%d.%m.%Y')}): ").strip()
    e_date = input(f"Дата конца (Enter для {today.strftime('%d.%m.%Y')}): ").strip()
    if not s_date:
        s_date = first_day.strftime('%d.%m.%Y')
    if not e_date:
        e_date = today.strftime('%d.%m.%Y')
    transfers = parse_funds_transfer_history(session, headers, s_date, e_date)
    print(f"--- История переводов средств с {s_date} по {e_date} ---")
    if not transfers:
        print("Нет переводов за выбранный период.")
    else:
        for idx, t in enumerate(transfers, 1):
            print(f"{idx}. {t['date']} | Получатель: {t['recipient']} | {t['amount']} | Статус: {t['status']}")
    print("=============================")
    input("Нажмите Enter чтобы вернуться в меню...")