import requests

# Token de autorización
token = 'apis-token-9962.z64rt6OGzlm1oXHEl43MsGDs3gkZDyHI' #Token de isai :)

def consultar_por_dni(dni):
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

def consultar_por_ruc(ruc):
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