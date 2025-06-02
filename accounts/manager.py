from .encryption import load_accounts, save_accounts
import os

def add_account():
    accounts = load_accounts()
    print("\n=== Добавление нового аккаунта ===")
    name = input("Введите имя аккаунта (например, 'мой'): ").strip()
    if not name:
        print("Имя аккаунта не может быть пустым.")
        return
    if name in accounts:
        print("Аккаунт с таким именем уже существует.")
        return
    login = input("Введите логин без 993: ").strip()
    password = input("Введите пароль: ").strip()
    accounts[name] = {"login": login, "password": password}
    save_accounts(accounts)
    print(f"Аккаунт '{name}' добавлен.")

def remove_account():
    accounts = load_accounts()
    if not accounts:
        print("Нет сохранённых аккаунтов.")
        return
    print("\nСписок аккаунтов:")
    keys = list(accounts.keys())
    for idx, name in enumerate(keys, 1):
        print(f" [{idx}] {name}")
    try:
        num = int(input("Введите номер аккаунта для удаления: ").strip())
        if not (1 <= num <= len(keys)):
            print("Некорректный номер.")
            return
        key = keys[num-1]
    except Exception:
        print("Некорректный ввод.")
        return
    confirm = input(f"Удалить аккаунт '{key}'? (y/n): ").strip().lower()
    if confirm == "y":
        del accounts[key]
        save_accounts(accounts)
        print(f"Аккаунт '{key}' удалён.")
    else:
        print("Удаление отменено.")

def edit_account():
    accounts = load_accounts()
    if not accounts:
        print("Нет сохранённых аккаунтов.")
        return
    print("\nСписок аккаунтов:")
    keys = list(accounts.keys())
    for idx, name in enumerate(keys, 1):
        print(f" [{idx}] {name}")
    try:
        num = int(input("Введите номер аккаунта для изменения: ").strip())
        if not (1 <= num <= len(keys)):
            print("Некорректный номер.")
            return
        key = keys[num-1]
    except Exception:
        print("Некорректный ввод.")
        return
    print(f"Текущий логин без 993: {accounts[key]['login']}")
    print(f"Текущий пароль: {accounts[key]['password']}")
    login = input("Введите новый логин без 993 (Enter чтобы не менять): ").strip()
    password = input("Введите новый пароль (Enter чтобы не менять): ").strip()
    if login:
        accounts[key]["login"] = login
    if password:
        accounts[key]["password"] = password
    save_accounts(accounts)
    print(f"Аккаунт '{key}' изменён.")

def choose_account():
    while True:
        accounts = load_accounts()
        if not accounts:
            print("Нет сохранённых аккаунтов. Сейчас будет добавлен первый аккаунт.")
            add_account()
            accounts = load_accounts()
        keys = list(accounts.keys())
        print("\nДоступные аккаунты:")
        for idx, name in enumerate(keys, 1):
            print(f" [{idx}] {name}")
        print("=== Выберите аккаунт сверху для продолжение входа в скрипт ===")
        print(f" [{len(keys)+1}] Добавить аккаунт")
        print(f" [{len(keys)+2}] Удалить аккаунт")
        print(f" [{len(keys)+3}] Изменить аккаунт")
        print(f" [{len(keys)+4}] Выйти")
        try:
            num = int(input("Выберите действие по номеру: ").strip())
        except Exception:
            print("Некорректный ввод.")
            continue
        if 1 <= num <= len(keys):
            key = keys[num-1]
            return accounts[key]
        elif num == len(keys)+1:
            add_account()
        elif num == len(keys)+2:
            remove_account()
        elif num == len(keys)+3:
            edit_account()
        elif num == len(keys)+4:
            exit()
        else:
            print("Некорректный ввод.")