from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()

# === CONFIGURACIÓN ===
EMAIL = "gm4526614@gmail.com"
CLAVE_APP = "Mogd litp fwdr dwdw"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# === FUENTES ===
URL_HONDUCOMPRAS = "https://sicc.honducompras.gob.hn/hc/procesos/busquedahistorico.aspx"
URL_IAIP_ROATAN = "https://portalunico.iaip.gob.hn/190/12/"
URL_ABIERTOS = "https://www.contratacionesabiertas.gob.hn/busqueda"
URL_API_LA = "https://data.lacity.org/resource/n9s8-7k7x.json"
URL_REMAX = "https://www.roatan-realestate.com/"
URL_ABOUT_RE = "https://www.aboutroatanrealestate.com/"
URL_API_LUCILA = "https://lucila-api-gm4526614.repl.co/api/resumen?clave=lucila2025"

# === FILTRO DE MES ACTUAL ===
def es_del_mes_actual(texto):
    hoy = datetime.now()
    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    for nombre, num in meses.items():
        if nombre in texto.lower() and num == hoy.month:
            return True
    return str(hoy.year) in texto

# === RASTREO de contratos ===
def rastrear_honduras():
    resultados = []
    for nombre, url in [
        ("Honducompras", URL_HONDUCOMPRAS),
        ("IAIP Roatán", URL_IAIP_ROATAN),
        ("Contrataciones Abiertas", URL_ABIERTOS),
    ]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            items = (
                soup.find_all("div")
                if nombre == "Honducompras"
                else soup.find_all("tr")
                if nombre == "IAIP Roatán"
                else soup.find_all("div")
            )
            hallados = [i.text.strip() for i in items if es_del_mes_actual(i.text) and any(kw in i.text.lower() for kw in ["roatán", "ceiba", "terreno", "casa", "licitación", "contrato"])]
            resultados.append(f"--- {nombre} ---")
            resultados.extend(hallados if hallados else ["ℹ️ No se detectaron resultados del mes actual."])
        except Exception as ex:
            resultados.append(f"--- {nombre} ---")
            resultados.append(f"⚠️ No accedió: {ex}")
    return resultados

# === RASTREO API Los Ángeles ===
def rastrear_los_angeles():
    resultados = ["--- Los Ángeles (API) ---"]
    claves = ["remodel", "construction", "permit", "cement", "blocks", "foundation", "addition"]
    try:
        resp = requests.get(URL_API_LA, headers=HEADERS, timeout=15)
        data = resp.json()[:20]
        for itm in data:
            texto = str(itm).lower()
            if any(k in texto for k in claves):
                title = itm.get("title", "[sin título]")
                loc = itm.get("location", "[sin ubicación]")
                resultados.append(f"{title} — {loc}")
        if len(resultados) == 1:
            resultados.append("ℹ️ No se detectaron contratos recientes.")
    except Exception as ex:
        resultados.append(f"⚠️ Error API Los Ángeles: {ex}")
    return resultados

# === INMUEBLES ROATÁN ===
def rastrear_inmuebles_roatan():
    resultados = []
    for nombre, url, cls_title, cls_price in [
        ("RE/MAX Roatán", URL_REMAX, "h4", "div.price"),
        ("About Roatán RE", URL_ABOUT_RE, "p.heading", "p.price"),
    ]:
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(res.text, "html.parser")
            resultados.append(f"--- {nombre} ---")
            found = False
            for item in soup.select(f"{cls_title}"):
                price = item.find_next_sibling(cls_price.split(".")[-1])
                if item.text.strip() and price:
                    resultados.append(f"{item.text.strip()} — {price.text.strip()}")
                    found = True
            if not found:
                resultados.append("ℹ️ No se detectaron inmuebles nuevos.")
        except Exception as ex:
            resultados.append(f"⚠️ No accedió {nombre}: {ex}")
    return resultados

# === API LUCILA (REAL) ===
def rastrear_api_lucila():
    resultados = ["--- Lucila API (Real – Replit) ---"]
    try:
        r = requests.get(URL_API_LUCILA, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("resultados", []):
                titulo = item.get("titulo", "[Sin título]")
                fecha = item.get("fecha", "")
                lugar = item.get("lugar", "")
                enlace = item.get("link", "")
                resultados.append(f"{titulo} ({fecha}) — {lugar}")
                if enlace:
                    resultados.append(f"🔗 {enlace}")
        else:
            resultados.append(f"⚠️ Error: {r.status_code} – {r.text.strip()}")
    except Exception as e:
        resultados.append(f"❌ Fallo conexión: {e}")
    return resultados

# === IA — Análisis Final ===
def lucila_analiza(lines):
    if any("⚠️" in ln or "❌" in ln for ln in lines):
        return "⚠️ Lucila: hay errores o fallos, revisa el informe."
    return "✔️ Lucila: todo parece bien."

def arquitecto_opina(lines):
    return "🏗️ Arquitecto: revisa los contratos recientes; puedo ayudarte con planos si lo deseas."

# === RUTA API ===
@app.get("/")
def inicio():
    return {"mensaje": "Lucila API está en línea y lista 🔍📩"}

@app.get("/api/resumen")
def api_resumen():
    hoy = datetime.now().strftime("%d %B %Y")
    resumen = [f"📌 Resumen diario – {hoy}", ""]
    resumen.extend(rastrear_honduras())
    resumen.append("")
    resumen.extend(rastrear_los_angeles())
    resumen.append("")
    resumen.extend(rastrear_inmuebles_roatan())
    resumen.append("")
    resumen.extend(rastrear_api_lucila())
    resumen.append("")
    resumen.append(lucila_analiza(resumen))
    resumen.append(arquitecto_opina(resumen))
    return {"resultados": resumen}
