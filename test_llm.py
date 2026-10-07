
import requests
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"

MODEL = "gemma:2b"
TEMPERATURE = 0.0
TIMEOUT = 120


# ============================================================
# ESTADÍSTICAS
# ============================================================

estadisticas = {
    "totales": 0,
    "passed": 0,
    "failed": 0
}


# ============================================================
# 1. VERIFICAR OLLAMA
# ============================================================

def verificar_ollama():
    """Comprueba que el servidor local de Ollama esté disponible."""

    print("\n[1] Verificando conexión con Ollama...")

    try:

        respuesta = requests.get(
            OLLAMA_TAGS_URL,
            timeout=10
        )

        respuesta.raise_for_status()

        print("✓ Ollama está disponible.")

        return True

    except requests.exceptions.RequestException as error:

        print("✗ No se pudo conectar con Ollama.")
        print(f"Error: {error}")

        return False


# ============================================================
# 2. VERIFICAR MODELO
# ============================================================

def verificar_modelo():
    """Comprueba que el modelo configurado esté instalado en Ollama."""

    print(f"\n[2] Verificando modelo: {MODEL}")

    try:

        respuesta = requests.get(
            OLLAMA_TAGS_URL,
            timeout=10
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        if not isinstance(datos, dict):
            print("✗ Respuesta inválida del servidor de Ollama.")
            return False

        modelos = datos.get("models", [])

        if not isinstance(modelos, list):
            print("✗ Formato inválido de la lista de modelos.")
            return False

        modelos_disponibles = [
            modelo.get("name")
            for modelo in modelos
        ]

        if MODEL in modelos_disponibles:

            print(f"✓ Modelo {MODEL} encontrado.")

            return True

        print(f"✗ El modelo {MODEL} no está instalado.")

        return False

    except (requests.exceptions.RequestException, ValueError) as error:

        print("✗ Error consultando los modelos.")
        print(f"Error: {error}")

        return False


# ============================================================
# 3. CONSULTAR EL LLM
# ============================================================

def consultar_llm(texto):
    """Envía una opinión al modelo y devuelve su respuesta y duración."""

    payload = {

        "model": MODEL,

        "prompt": f"""
Analiza el sentimiento de la siguiente opinión
de un cliente de una tienda online.

Debes determinar si el sentimiento general es
POSITIVO o NEGATIVO.

Responde siguiendo este formato:

El sentimiento general es POSITIVO.

o

El sentimiento general es NEGATIVO.

No agregues saludos.
No agregues preguntas.
No agregues información adicional.

Opinión del cliente:
{texto}
""",

        "stream": False,

        "options": {
            "temperature": TEMPERATURE
        }
    }

    inicio = time.perf_counter()

    try:

        respuesta = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=TIMEOUT
        )

        respuesta.raise_for_status()

        datos = respuesta.json()

        if not isinstance(datos, dict):
            raise ValueError("La respuesta de Ollama no tiene formato JSON válido.")

        tiempo_respuesta = (
            time.perf_counter() - inicio
        )

        texto_respuesta = datos.get(
            "response",
            ""
        ).strip()

        return {
            "respuesta": texto_respuesta,
            "tiempo": tiempo_respuesta,
            "exito": True
        }

    except (requests.exceptions.RequestException, ValueError) as error:

        tiempo_respuesta = (
            time.perf_counter() - inicio
        )

        return {
            "respuesta": "",
            "tiempo": tiempo_respuesta,
            "exito": False,
            "error": str(error)
        }


# ============================================================
# 4. NORMALIZAR RESPUESTA
# ============================================================

def normalizar_respuesta(respuesta):
    """Normaliza una respuesta para comparaciones insensibles a mayúsculas."""

    return respuesta.strip().upper()


# ============================================================
# 5. DETECTAR SENTIMIENTO
# ============================================================

def detectar_sentimiento(respuesta):
    """Extrae un sentimiento inequívoco de la respuesta del modelo."""

    respuesta_normalizada = normalizar_respuesta(
        respuesta
    )

    contiene_negativo = "NEGATIVO" in respuesta_normalizada
    contiene_positivo = "POSITIVO" in respuesta_normalizada

    if contiene_negativo and not contiene_positivo:
        return "NEGATIVO"

    if contiene_positivo and not contiene_negativo:
        return "POSITIVO"

    if respuesta_normalizada == "NEGATIVO":
        return "NEGATIVO"

    if respuesta_normalizada == "POSITIVO":
        return "POSITIVO"

    return None


# ============================================================
# 6. EJECUTAR TEST
# ============================================================

def ejecutar_test(
    nombre,
    condicion,
    contar_estadistica=True
):
    """Registra y muestra el resultado de una condición de prueba."""

    if contar_estadistica:

        estadisticas["totales"] += 1

    print(f"\nTEST: {nombre}")

    try:

        assert condicion

        if contar_estadistica:

            estadisticas["passed"] += 1

        print("✓ PASS")

        return True

    except AssertionError:

        if contar_estadistica:

            estadisticas["failed"] += 1

        print("✗ FAIL")

        return False


# ============================================================
# 7. MOSTRAR RESULTADO
# ============================================================

def mostrar_resultado(
    texto,
    respuesta,
    tiempo,
    esperado
):
    """Muestra la opinión, la respuesta y el resultado esperado."""

    print("\n" + "-" * 60)

    print("OPINIÓN DEL CLIENTE:")
    print(texto)

    print("\nRESPUESTA DEL MODELO:")
    print(respuesta)

    print("\nSENTIMIENTO DETECTADO:")

    sentimiento = detectar_sentimiento(
        respuesta
    )

    print(
        sentimiento
        if sentimiento
        else "No identificado"
    )

    print("\nSENTIMIENTO ESPERADO:")
    print(esperado)

    print("\nTIEMPO DE RESPUESTA:")
    print(f"{tiempo:.2f} segundos")

    print("-" * 60)


# ============================================================
# 8. EJECUTAR CASO
# ============================================================

def ejecutar_caso(
    numero,
    texto,
    esperado,
    modo="normal"
):
    """Ejecuta un caso completo contra el modelo configurado."""

    print("\n")
    print("=" * 60)
    print(f"CASO DE PRUEBA #{numero}")
    print("=" * 60)

    resultado = consultar_llm(texto)

    if not resultado["exito"]:

        print("\n✗ ERROR CONSULTANDO EL MODELO")

        print(
            resultado.get(
                "error",
                "Error desconocido"
            )
        )

        return False

    respuesta = resultado["respuesta"]

    tiempo = resultado["tiempo"]

    mostrar_resultado(
        texto,
        respuesta,
        tiempo,
        esperado
    )

    if modo == "debug":
        sentimiento = detectar_sentimiento(respuesta)
        resultado_test = ejecutar_test(
            f"Sentimiento detectado igual a {esperado}",
            sentimiento == esperado,
            contar_estadistica=True
        )

        if not resultado_test:
            print("\n" + "=" * 60)
            print("DEBUGGING")
            print("=" * 60)
            print("\nEl test falló.")
            print("\nRespuesta del modelo:")
            print(respuesta)
            print("\nValor esperado:")
            print(esperado)
            print("\nSentimiento detectado:")
            print(sentimiento or "No identificado")

        return resultado_test

    # ========================================================
    # CASOS 2 Y 3
    # TEST CORRECTO
    # ========================================================

    resultado_test = ejecutar_test(
        f"Sentimiento detectado igual a {esperado}",
        detectar_sentimiento(respuesta) == esperado,
        contar_estadistica=True
    )

    return resultado_test


# ============================================================
# 9. MOSTRAR RESUMEN
# ============================================================

def mostrar_resumen():
    """Muestra el resumen acumulado de las pruebas ejecutadas."""

    print("\n")
    print("=" * 60)
    print("RESUMEN DE TESTING")
    print("=" * 60)

    print(
        f"Casos validados   : {estadisticas['totales']}"
    )

    print(
        f"Tests PASS        : {estadisticas['passed']}"
    )

    print(
        f"Tests FAIL        : {estadisticas['failed']}"
    )

    if estadisticas["totales"] > 0:

        porcentaje = (
            estadisticas["passed"] / estadisticas["totales"]
        ) * 100

        print(
            f"Porcentaje PASS   : {porcentaje:.1f}%"
        )

    print("=" * 60)


# ============================================================
# 10. FUNCIÓN PRINCIPAL
# ============================================================

def main():
    """Verifica Ollama y ejecuta todos los casos de prueba."""

    print("\n")
    print("=" * 60)
    print("TESTING DE RESPUESTAS DE UN LLM")
    print("=" * 60)

    print("\nContexto: tienda online")
    print(f"Modelo utilizado: {MODEL}")

    # --------------------------------------------------------
    # VERIFICAR OLLAMA
    # --------------------------------------------------------

    if not verificar_ollama():

        print("\nNo se puede continuar.")

        return

    # --------------------------------------------------------
    # VERIFICAR MODELO
    # --------------------------------------------------------

    if not verificar_modelo():

        print("\nNo se puede continuar.")

        return

    # --------------------------------------------------------
    # CASOS DE PRUEBA
    # --------------------------------------------------------

    casos = [

        # ----------------------------------------------------
        # CASO 1
        # NEGATIVO: la demora afecta el resultado general
        # ----------------------------------------------------

        {
            "texto": (
                "El producto es bueno, "
                "pero tardó tres semanas en llegar."
            ),
            "esperado": "NEGATIVO"
        },

        # ----------------------------------------------------
        # CASO 2
        # PASS
        # ----------------------------------------------------

        {
            "texto": (
                "Estoy muy feliz con mi compra. "
                "El producto llegó rápido "
                "y funciona perfectamente."
            ),
            "esperado": "POSITIVO"
        },

        # ----------------------------------------------------
        # CASO 3
        # PASS
        # ----------------------------------------------------

        {
            "texto": (
                "El producto funciona, "
                "pero la atención al cliente "
                "fue terrible."
            ),
            "esperado": "NEGATIVO"
        }

    ]

    # ========================================================
    # TEST 1 → FAIL
    # ========================================================

    ejecutar_caso(
        1,
        casos[0]["texto"],
        casos[0]["esperado"],
        modo="debug"
    )

    # ========================================================
    # TEST 2 → PASS
    # ========================================================

    ejecutar_caso(
        2,
        casos[1]["texto"],
        casos[1]["esperado"]
    )

    # ========================================================
    # TEST 3 → PASS
    # ========================================================

    ejecutar_caso(
        3,
        casos[2]["texto"],
        casos[2]["esperado"]
    )

    # ========================================================
    # RESUMEN
    # ========================================================

    mostrar_resumen()


# ============================================================
# EJECUTAR PROGRAMA
# ============================================================

if __name__ == "__main__":

    main()
   