from bs4 import BeautifulSoup

def get_csrf_token(soup):
    token_input = soup.find("input", {"name": "__RequestVerificationToken"})
    return token_input["value"] if token_input else None

def login(session, headers, LOGIN, PASSWORD):
    login_url = "https://hyzmat.tmcell.tm/User?RetUrl=%2FProfile"
    resp = session.get(login_url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    csrf_token = get_csrf_token(soup)
    if not csrf_token:
        print("CSRF токен не найден, вход невозможен.")
        return None
    payload = {
        "__RequestVerificationToken": csrf_token,
        "login": LOGIN,
        "password": PASSWORD,
    }
    login_response = session.post(login_url, data=payload, headers=headers)
    if "/Profile" not in login_response.url:
        print("Вход не удался, проверьте логин и пароль.")
        return None
    print("Вход выполнен успешно.")
    return csrf_token