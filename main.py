from accounts.manager import choose_account
from auth.login import login
from tmcell.api import (
    parse_main_info, parse_packets, parse_services,
    parse_tariffs, parse_available_packets, parse_payment_history,
    parse_funds_transfer_history
)
from tmcell.packets import print_packets, print_available_packets
from tmcell.services import manage_services
from tmcell.tariffs import handle_tariff_switch
from tmcell.payments import handle_payments_history
from tmcell.transfers import handle_transfers_history
from tmcell.sms import send_sms
from ui.menu import print_main_menu

import requests

balance = 0.0

def main():
    global balance
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://hyzmat.tmcell.tm/User?RetUrl=%2FProfile",
    }

    creds = choose_account()
    LOGIN = creds["login"]
    PASSWORD = creds["password"]
    while True:
        csrf_token = login(session, headers, LOGIN, PASSWORD)
        if not csrf_token:
            return

        main_info = parse_main_info(session, headers)
        try:
            balance = float(main_info.get('balance', '0').split()[0].replace(",", ".").replace("манат", "").replace(" ", ""))
        except Exception:
            balance = 0.0
        packets = parse_packets(session, headers)
        services = parse_services(session, headers)

        print_main_menu(main_info)
        choice = input("Выберите пункт меню: ").strip()
        if choice == "1":
            print_packets(packets, show_all=True)
            input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "2":
            print_packets(packets, show_all=False)
            input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "3":
            manage_services(session, headers, services, LOGIN, PASSWORD)
        elif choice == "4":
            handle_tariff_switch(session, headers, LOGIN, PASSWORD)
        elif choice == "5":
            packets_for_buy = parse_available_packets(session, headers, is_gift=False, balance=balance)
            print_available_packets(packets_for_buy, is_gift=False, balance=balance)
            idx = input("Введите номер пакета для покупки (или 0 для отмены): ").strip()
            if idx == "0":
                continue
            try:
                num = int(idx)
            except ValueError:
                print("Некорректный ввод.")
                continue
            if num < 1 or num > len(packets_for_buy):
                print("Нет такого пакета!")
                continue
            packet_id = packets_for_buy[num-1]["packet_id"]
            from tmcell.api import buy_packet
            buy_packet(session, headers, packet_id, LOGIN, PASSWORD)
            input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "6":
            packets_for_gift = parse_available_packets(session, headers, is_gift=True, balance=balance)
            print_available_packets(packets_for_gift, is_gift=True, balance=balance)
            idx = input("Введите номер пакета для подарка (или 0 для отмены): ").strip()
            if idx == "0":
                continue
            try:
                num = int(idx)
            except ValueError:
                print("Некорректный ввод.")
                continue
            if num < 1 or num > len(packets_for_gift):
                print("Нет такого пакета!")
                continue
            packet = packets_for_gift[num-1]
            from tmcell.api import gift_packet
            gift_packet(session, headers, packet["packet_id"], packet["packet_name"], LOGIN, PASSWORD)
            input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "7":
            handle_payments_history(session, headers)
        elif choice == "8":
            handle_transfers_history(session, headers)
        elif choice == "9":
            send_sms(session, headers, LOGIN, PASSWORD)
            input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "10":
            choose_account()
            input("Нажмите Enter чтобы вернуться в меню...")
        elif choice == "0":
            print("Выход...")
            break
        else:
            print("Некорректный выбор. Попробуйте ещё раз.")

if __name__ == "__main__":
    main()