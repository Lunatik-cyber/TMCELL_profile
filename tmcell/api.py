import html
import datetime
from bs4 import BeautifulSoup

def parse_main_info(session, headers):
    profile_url = "https://hyzmat.tmcell.tm/Profile"
    resp = session.get(profile_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    data = {
        "contract": "?",
        "phone": "?",
        "tariff": "?",
        "balance": "?",
        "name": "?",
    }
    rows = soup.find_all("table", class_="profiletable")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) != 2:
            continue
        label = cells[0].get_text(strip=True)
        value = cells[1]
        text_value = value.get_text(" ", strip=True)
        if "Şertnamanyň №" in label:
            data["contract"] = text_value
        elif "Telefon belgisi" in label:
            data["phone"] = text_value
        elif "Nyrhnama meýilnamasy" in label:
            data["tariff"] = text_value
        elif "Şertnamanyň баланс" in label or "Şertnamanyň balansy" in label:
            balance_text = html.unescape(text_value)
            balance_text = balance_text.split(' ')
            balance = balance_text[0].replace('\xa0', ' ')
            date = balance_text[-1] + ' ' + balance_text[-2]
            data["balance"] = balance + ' ' + date
        elif "Ady" in label:
            data["name"] = text_value
    return data

def parse_packets(session, headers):
    url = "https://hyzmat.tmcell.tm/tk-tm/TrafficPackets/Index"
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    packets = []
    for table in soup.find_all("table", class_="table-values"):
        row = table.find("tr")
        cells = row.find_all("td")
        if len(cells) == 7:
            packet = {
                "name": cells[0].get_text(strip=True),
                "total": cells[1].get_text(strip=True),
                "left": cells[2].get_text(strip=True),
                "unit": cells[3].get_text(strip=True),
                "type": cells[4].get_text(strip=True),
                "start": cells[5].get_text(strip=True),
                "end": cells[6].get_text(strip=True),
            }
            packets.append(packet)
    return packets

def is_active_packet(packet):
    left = packet['left'].replace(',', '.').replace(' ', '')
    try:
        value = float(left)
        return value > 0.0
    except Exception:
        return False

def parse_services(session, headers):
    url = "https://hyzmat.tmcell.tm/Service/Index"
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    def parse_table_block(block_id, columns, get_id=False):
        block = soup.find(id=block_id)
        if not block:
            return []
        tables = block.find_all("table", class_="table-values")
        results = []
        for table in tables:
            row = table.find("tr")
            if row:
                cells = row.find_all("td")
                entry = {}
                for col, cell in zip(columns, cells):
                    a = cell.find("a")
                    entry[col] = a.get_text(strip=True) if a else cell.get_text(strip=True)
                    if a and a.has_attr("href"):
                        entry[col+"_url"] = a["href"]
                if get_id:
                    tr_id = row.get("id", "")
                    if tr_id.startswith("es") or tr_id.startswith("sa"):
                        entry["service_id"] = tr_id[2:]
                results.append(entry)
        return results

    restrictions_enabled = parse_table_block("showRestrictionsEnabled", ["name", "disable_price", "monthly_fee", "fee_strategy"], get_id=True)
    restrictions_may_enable = parse_table_block("showRestrictionsMayEnable", ["name", "enable_price", "monthly_fee"], get_id=True)
    enabled = parse_table_block("showEnabled", ["name", "disable_price", "monthly_fee", "fee_strategy"], get_id=True)
    may_enable = parse_table_block("showMayEnable", ["name", "enable_price", "monthly_fee"], get_id=True)
    return {
        "restrictions_enabled": restrictions_enabled,
        "restrictions_may_enable": restrictions_may_enable,
        "enabled": enabled,
        "may_enable": may_enable
    }

def parse_tariffs(session, headers):
    url = "https://hyzmat.tmcell.tm/Tariff/Index"
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    current_tariff = "?"
    cur_h2 = soup.find("h2")
    if cur_h2:
        current_tariff = cur_h2.get_text(strip=True).split(":")[-1].strip()
    tariffs = []
    tables = soup.find_all("table", class_="table-values")
    forms = soup.find_all("form", action="/Tariff/Edit")
    for table, form in zip(tables, forms):
        row = table.find("tr")
        cells = row.find_all("td")
        if len(cells) == 2:
            name = cells[0].get_text(strip=True)
            price = cells[1].get_text(strip=True)
            tariff_id = form.find("input", {"name": "tariffId"}).get("value")
            tariffs.append({
                "name": name,
                "price": price,
                "tariff_id": tariff_id
            })
    return current_tariff, tariffs

def parse_available_packets(session, headers, is_gift=False, balance=0.0):
    url = "https://hyzmat.tmcell.tm/TrafficPackets/Gift" if is_gift else "https://hyzmat.tmcell.tm/TrafficPackets/Buy"
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    packets = []
    forms = soup.find_all("form", action="/TrafficPackets/GiftPacket" if is_gift else "/TrafficPackets/Buy")
    table_values = soup.find_all("table", class_="table-values")
    divactions = soup.find_all("div", class_="divaction")
    for i, table in enumerate(table_values):
        row = table.find("tr")
        cells = row.find_all("td")
        if len(cells) == 5:
            name = cells[0].get_text(strip=True)
            amount = cells[1].get_text(strip=True)
            unit = cells[2].get_text(strip=True)
            period = cells[3].get_text(strip=True)
            price = cells[4].get_text(strip=True)
            period = period.replace("period", "дней").replace("&nbsp;", " ").replace("\xa0", " ").strip()
            price = price.replace("manat", "манат").replace("манат", " манат").replace("\xa0", " ").strip()
            divact = divactions[i] if i < len(divactions) else None
            not_enough = False
            not_enough_amount = ""
            form = None
            if i < len(forms):
                form = forms[i]
            if form and form.find("input"):
                if is_gift:
                    packet_id = form.find("input", {"name": "packetId"}).get("value")
                    packet_name = form.find("input", {"name": "packetName"}).get("value")
                else:
                    packet_id = form.find("input", {"name": "Id"}).get("value")
                    packet_name = name
                packets.append({
                    "name": name,
                    "amount": amount,
                    "unit": unit,
                    "period": period,
                    "price": price,
                    "packet_id": packet_id,
                    "packet_name": packet_name,
                    "available": True,
                    "not_enough": not_enough,
                    "not_enough_amount": not_enough_amount,
                })
            else:
                not_enough = True
                msg = ""
                if divact:
                    msg = divact.get_text(strip=True)
                packets.append({
                    "name": name,
                    "amount": amount,
                    "unit": unit,
                    "period": period,
                    "price": price,
                    "packet_id": None,
                    "packet_name": name,
                    "available": False,
                    "not_enough": not_enough,
                    "not_enough_amount": "",
                    "msg": msg,
                })
    return packets

def buy_packet(session, headers, packet_id, user_login, user_password):
    from auth.login import login
    csrf_token = login(session, headers, user_login, user_password)
    if not csrf_token:
        print("Не удалось получить CSRF токен для покупки пакета.")
        return False
    url = "https://hyzmat.tmcell.tm/TrafficPackets/Buy"
    payload = {
        "__RequestVerificationToken": csrf_token,
        "Id": packet_id
    }
    resp = session.post(url, data=payload, headers=headers)
    if resp.status_code == 200 and ("успешно" in resp.text.lower() or "satyn alyndy" in resp.text.lower()):
        print("Пакет успешно куплен!")
        return True
    elif resp.status_code == 200 and "ýeterlikli däl" in resp.text.lower():
        print("Недостаточно средств для покупки пакета.")
        return False
    else:
        print("Ошибка при покупке пакета!")
        return False

def gift_packet(session, headers, packet_id, packet_name, user_login, user_password):
    from auth.login import login
    csrf_token = login(session, headers, user_login, user_password)
    if not csrf_token:
        print("Не удалось получить CSRF токен для подарка пакета.")
        return False
    url = "https://hyzmat.tmcell.tm/TrafficPackets/GiftPacket"
    params = {
        "packetId": packet_id,
        "packetName": packet_name,
        "BuyPacket": ""
    }
    resp = session.get(url, headers=headers, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")
    csrf_gift = soup.find("input", {"name": "__RequestVerificationToken"})
    csrf_gift = csrf_gift["value"] if csrf_gift else csrf_token
    phone = input("Введите номер телефона получателя в формате 993XXXXXXXX: ").strip()
    post_payload = {
        "__RequestVerificationToken": csrf_gift,
        "phoneNumber": phone,
        "packetId": packet_id
    }
    post_resp = session.post(url, data=post_payload, headers=headers)
    if post_resp.status_code == 200 and ("успешно" in post_resp.text.lower() or "sowgat berildi" in post_resp.text.lower()):
        print("Пакет успешно подарен!")
        return True
    elif post_resp.status_code == 200 and "ýeterlikli däl" in post_resp.text.lower():
        print("Недостаточно средств для подарка пакета.")
        return False
    elif post_resp.status_code == 200 and "nädogry" in post_resp.text.lower():
        print("Неверный номер телефона!")
        return False
    else:
        print("Ошибка при подарке пакета!")
        return False

def parse_payment_history(session, headers, start_date, end_date):
    url = "https://hyzmat.tmcell.tm/Payment/Details"
    params = {
        "StartDate": start_date,
        "EndDate": end_date
    }
    resp = session.get(url, headers=headers, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")
    payments = []
    tables = soup.find_all("table", class_="table-values")
    for table in tables:
        row = table.find("tr")
        if row:
            cells = row.find_all("td")
            if len(cells) == 5:
                date = cells[0].get_text(strip=True)
                amount = cells[1].get_text(strip=True).replace("manat", "манат").replace("\xa0", " ")
                paytype = cells[2].get_text(strip=True)
                dealer = cells[3].get_text(strip=True)
                tax = cells[4].get_text(strip=True)
                payments.append({
                    "date": date,
                    "amount": amount,
                    "type": paytype,
                    "dealer": dealer,
                    "tax": tax,
                })
    return payments

def parse_funds_transfer_history(session, headers, start_date, end_date):
    url = "https://hyzmat.tmcell.tm/FundsTransfer/HistoryTable"
    params = {
        "StartDate": start_date,
        "EndDate": end_date
    }
    resp = session.get(url, headers=headers, params=params)
    soup = BeautifulSoup(resp.text, "html.parser")
    transfers = []
    tables = soup.find_all("table", class_="table-values")
    for table in tables:
        row = table.find("tr")
        if row:
            cells = row.find_all("td")
            if len(cells) == 4:
                date = cells[0].get_text(strip=True)
                recipient = cells[1].get_text(strip=True)
                amount = cells[2].get_text(strip=True).replace("manat", "манат").replace("\xa0", " ")
                status = cells[3].get_text(strip=True)
                transfers.append({
                    "date": date,
                    "recipient": recipient,
                    "amount": amount,
                    "status": status,
                })
    return transfers