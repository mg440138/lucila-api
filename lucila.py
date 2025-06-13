
# lucila.py

def verificar_marca(nombre, descripcion):
    marcas_prohibidas = ["nike", "apple", "adidas", "gucci", "samsung", "puma", "louis vuitton", "balenciaga"]
    texto = (nombre + " " + descripcion).lower()
    for marca in marcas_prohibidas:
        if marca in texto:
            return False, f"🚫 Producto bloqueado: contiene marca prohibida ({marca})"
    return True, "✅ Producto legal y listo para publicar"

def corregir_descripcion(texto):
    return texto.strip().capitalize()

def subir_producto(producto, supabase=None):
    nombre = producto.get("nombre", "")
    descripcion = producto.get("descripcion", "")
    precio = producto.get("precio", 0)

    legal, mensaje = verificar_marca(nombre, descripcion)
    if not legal:
        return mensaje

    descripcion_limpia = corregir_descripcion(descripcion)

    if supabase:
        supabase.table("mercancilla").insert({
            "nombre": nombre,
            "descripcion": descripcion_limpia,
            "precio": precio
        }).execute()

    return f"✅ Producto '{nombre}' subido con éxito."
