
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# Lista de ciudades del área de Los Ángeles y alrededores
CIUDADES_LA = [
    "los angeles", "long beach", "pasadena", "inglewood", "santa monica", "glendale",
    "torrance", "compton", "carson", "west covina", "burbank", "norwalk", "downey",
    "el monte", "culver city", "san pedro", "palos verdes", "wilmington"
]

# Función para obtener contratos
def obtener_contratos():
    urls = [
        "https://www.bidnetdirect.com/california",
        "https://www.constructionbidsource.com/archives/los-angeles-ca"
    ]

    contratos = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            enlaces = soup.find_all("a", href=True)
            for enlace in enlaces:
                texto = enlace.get_text().strip().lower()
                link = enlace["href"]

                if any(ciudad in texto for ciudad in CIUDADES_LA):
                    contratos.append(f"{enlace.text.strip()} => {link}")

        except Exception as e:
            print(f"❌ Error al conectar con el sitio: {url}\n{e}")

    return contratos

# Función para enviar correo con resultados
def enviar_por_correo(lista_contratos, destinatario):
    cuerpo = "\n\n".join(lista_contratos)
    msg = MIMEText(cuerpo)
    msg["Subject"] = "🛠️ Contratos de Construcción en Los Ángeles"
    msg["From"] = "gm4526614@gmail.com"
    msg["To"] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login("gm4526614@gmail.com", "mogdlitpfwdrdwdw")  # Tu contraseña de aplicación
            smtp.send_message(msg)
            print("✅ Correo enviado con éxito.")
    except Exception as e:
        print(f"❌ Error al enviar el correo:\n{e}")

# EJECUCIÓN PRINCIPAL
contratos = obtener_contratos()

if contratos:
    enviar_por_correo(contratos, "gm4526614@gmail.com")
else:
    print("⚠️ No se encontraron contratos en las ciudades indicadas.")
