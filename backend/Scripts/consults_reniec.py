import requests
from config import API_TOKEN_DNI_RUC

# Token de autorización
token = API_TOKEN_DNI_RUC

if token is None:
    raise ValueError('El Token no está configurado')


def validar_dni(dni):
    return dni.isdigit() and len(dni) == 8


def validar_ruc(ruc):
    return ruc.isdigit() and len(ruc) == 11


def get_info_by_dni(dni):
    if not validar_dni(dni):
        print("Número de DNI inválido. Debe ser un número de 8 dígitos.")
        return None

    url = f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}'
    headers = {
        'Referer': 'https://apis.net.pe/consulta-dni-api',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        persona = response.json()
        return persona
    else:
        return None


def get_info_by_ruc(ruc):
    if not validar_ruc(ruc):
        print("Número de RUC inválido. Debe ser un número de 11 dígitos.")
        return None

    url = f'https://api.apis.net.pe/v2/sunat/ruc?numero={ruc}'
    headers = {
        'Referer': 'http://apis.net.pe/api-ruc',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        empresa = response.json()
        return empresa
    else:
        return None