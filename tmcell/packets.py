def is_active_packet(packet):
    left = packet['left'].replace(',', '.').replace(' ', '')
    try:
        value = float(left)
        return value > 0.0
    except Exception:
        return False

def print_packets(packets, show_all=True):
    if show_all:
        filtered = packets
        title = "--- ВСЕ ПАКЕТЫ ---"
    else:
        filtered = [p for p in packets if is_active_packet(p)]
        title = "--- АКТИВНЫЕ ПАКЕТЫ (есть остаток) ---"

    print(title)
    if not filtered:
        print("Нет подходящих пакетов.")
    else:
        for idx, pkt in enumerate(filtered, 1):
            print(f"{idx:2d}. {pkt['name']} | {pkt['left']} из {pkt['total']} {pkt['unit']} | {pkt['type']}")
            print(f"    Период: {pkt['start']} — {pkt['end']}")
    print("=============================\n")

def print_available_packets(packets, is_gift=False, balance=0.0):
    print("--- Доступные интернет-пакеты для покупки{} ---".format(" и подарка" if is_gift else ""))
    for idx, pkt in enumerate(packets, 1):
        avail = pkt.get("available", True)
        base_info = f"{idx}. {pkt['name']} | {pkt['amount']} {pkt['unit']} | срок: {pkt['period']} | {pkt['price']} | ID: {pkt.get('packet_id','-')}"
        if avail:
            print(base_info)
        else:
            try:
                lack = float(pkt.get("price", "0").replace(" манат", "").replace(",", ".").replace(" ", "")) - float(balance)
                if lack > 0:
                    msg = f"Недостаточно средств (не хватает {lack:.2f} манат)"
                else:
                    msg = "Недостаточно средств"
            except Exception:
                msg = "Недостаточно средств"
            print(f"{base_info} | {msg}")
    print("=============================")