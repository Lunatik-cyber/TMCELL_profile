def manage_services(session, headers, services):
    def print_services_menu():
        print("=== УСЛУГИ ===")
        print(" [1] Подключённые услуги")
        print(" [2] Доступные для подключения")
        print(" [3] Ограниченные услуги (активные)")
        print(" [4] Ограничения, которые можно активировать")
        print(" [0] Назад")
        print("=============================")

    def print_services_list(services, title, show_ids=False):
        print(f"--- {title} ---")
        if not services:
            print("Нет услуг.")
        else:
            for idx, svc in enumerate(services, 1):
                name = svc.get("name", "")
                monthly = svc.get("monthly_fee", "")
                price = svc.get("enable_price", svc.get("disable_price", ""))
                strategy = svc.get("fee_strategy", "")
                monthly_str = f"{monthly} манат" if monthly else "0 манат"
                price_str = f"{price} манат" if price else "0 манат"
                id_str = f" [ID: {svc.get('service_id', '')}]" if show_ids and svc.get("service_id") else ""
                print(f"{idx:2d}. {name}{id_str} | Абонплата: {monthly_str} | Подключение/отключение: {price_str} | {strategy}")
        print("=============================")

    def choose_service_and_act(services, mode):
        if not services:
            print("Нет услуг в этом разделе.")
            input("Нажмите Enter чтобы вернуться ...")
            return
        print_services_list(services, "Выбор услуги", show_ids=True)
        try:
            num = int(input(f"Введите номер услуги для {'подключения' if mode == 'connect' else 'отключения'} (или 0 для отмены): ").strip())
        except ValueError:
            print("Некорректный ввод.")
            return
        if num < 1 or num > len(services):
            print("Отмена.")
            return
        service_id = services[num-1].get("service_id", "")
        if not service_id:
            print("ID услуги не найден, операция невозможна.")
            return
        if mode == "connect":
            from tmcell.api import login as relogin
            from tmcell.api import connect_service
            connect_service(session, headers, service_id)
        else:
            from tmcell.api import login as relogin
            from tmcell.api import disconnect_service
            disconnect_service(session, headers, service_id)
        input("Нажмите Enter чтобы вернуться ...")

    while True:
        print_services_menu()
        sch = input("Выберите раздел услуг: ").strip()
        if sch == "1":
            print_services_list(services["enabled"], "Подключённые услуги", show_ids=True)
            act = input("Хотите отключить услугу? (y/n): ").strip().lower()
            if act == "y":
                choose_service_and_act(services["enabled"], mode="disconnect")
        elif sch == "2":
            print_services_list(services["may_enable"], "Доступные для подключения услуги", show_ids=True)
            act = input("Хотите подключить услугу? (y/n): ").strip().lower()
            if act == "y":
                choose_service_and_act(services["may_enable"], mode="connect")
        elif sch == "3":
            print_services_list(services["restrictions_enabled"], "Ограниченные активные услуги", show_ids=True)
            act = input("Хотите отключить услугу? (y/n): ").strip().lower()
            if act == "y":
                choose_service_and_act(services["restrictions_enabled"], mode="disconnect")
        elif sch == "4":
            print_services_list(services["restrictions_may_enable"], "Ограничения, которые можно активировать", show_ids=True)
            act = input("Хотите подключить услугу? (y/n): ").strip().lower()
            if act == "y":
                choose_service_and_act(services["restrictions_may_enable"], mode="connect")
        elif sch == "0":
            break
        else:
            print("Некорректный выбор. Попробуйте ещё раз.")