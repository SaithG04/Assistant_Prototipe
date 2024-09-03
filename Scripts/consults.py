import requests
import os

# Token de autorización
token = os.getenv('API_TOKEN_DNI_RUC') #Token

if token is None:
    raise ValueError('El Token no está configurado')

def validar_dni(dni):
    return dni.isdigit() and len(dni) == 8

def validar_ruc(ruc):
    return ruc.isdigit() and len(ruc) == 11

#def buscar_en_historial_por_dni(dni):
#    historial = cargar_historial()
#    for entrada in historial:
#        if entrada['consulta'] == f"Consulta por DNI: {dni}":
#            return entrada['respuesta']
#    return None

#def buscar_en_historial_por_ruc(ruc):
#    historial = cargar_historial()
#    for entrada in historial:
#        if entrada['consulta'] == f"Consulta por RUC: {ruc}":
#            return entrada['respuesta']
#    return None

def consultar_por_dni(dni):
    if not validar_dni(dni):
        print("Número de DNI inválido. Debe ser un número de 8 dígitos.")
        return None

    #respuesta_almacenada = buscar_en_historial_por_dni(dni)
    #if respuesta_almacenada:
    #    print("Mostrando resultados almacenados para este DNI.")
    #    return respuesta_almacenada

    url = f'https://api.apis.net.pe/v2/reniec/dni?numero={dni}'
    headers = {
        'Referer': 'https://apis.net.pe/consulta-dni-api',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        persona = response.json()
        #guardar_en_historial(f"Consulta por DNI: {dni}", persona)
        return persona
    else:
        #guardar_en_historial(f"Consulta por DNI: {dni}", "No se encontró información.")
        return None

def consultar_por_ruc(ruc):
    if not validar_ruc(ruc):
        print("Número de RUC inválido. Debe ser un número de 11 dígitos.")
        return None

    #respuesta_almacenada = buscar_en_historial_por_ruc(ruc)
    #if respuesta_almacenada:
    #    print("Mostrando resultados almacenados para este RUC.")
    #    return respuesta_almacenada

    url = f'https://api.apis.net.pe/v2/sunat/ruc?numero={ruc}'
    headers = {
        'Referer': 'http://apis.net.pe/api-ruc',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        empresa = response.json()
        #guardar_en_historial(f"Consulta por RUC: {ruc}", empresa)
        return empresa
    else:
        #guardar_en_historial(f"Consulta por RUC: {ruc}", "No se encontró información.")
        return None