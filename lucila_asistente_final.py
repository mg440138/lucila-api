
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import smtplib
import time

# Lista de sitios a rastrear
sitios = [
    "https://www.rampla.org/s/opportunities",
    "https://www.california.com/california",
    "https://www.californiaprojobs.com/archives/los-angeles-ca"
]

# FUNCIÓN PARA OBTENER CONTRATOS
def obtener_contratos():
    contratos = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    for url in sitios:
        try:
            respuesta = requests.get(url, headers=headers, timeout=10)
            if respuesta.status_code == 200:
                sopa = BeautifulSoup(respuesta.text, "html.parser")
                textos = sopa.get_text().splitlines()
                for texto in textos:
                    if "construction" in texto.lower() or "project" in texto.lower():
                        contratos.append(f"{url} -> {texto.strip()}")
        except Exception as e:
            print(f"⚠️ Error al conectar con el sitio: {url}\n{e}")
    return contratos

# FUNCIÓN PARA ENVIAR CORREO CON CONTRATOS ENCONTRADOS
def enviar_por_correo(lista_contratos, destinatario):
    cuerpo = "\n".join(lista_contratos)
    msg = MIMEText(cuerpo)
    msg["Subject"] = "📄 Contratos de Construcción en Los Ángeles"
    msg["From"] = "gm4526614@gmail.com"
    msg["To"] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login("gm4526614@gmail.com", "mogdltpfwdrwdwv")  # contraseña de aplicación
            smtp.send_message(msg)
            print("✅ Correo enviado con éxito.")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)

# 🚀 EJECUCIÓN DEL SISTEMA
contratos = obtener_contratos()
if contratos:
    enviar_por_correo(contratos, "gm4526614@gmail.com")
else:
    print("⚠️ No se encontraron contratos.")
