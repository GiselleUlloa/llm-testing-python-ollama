# ¿Puede tu LLM pasar esta prueba?

## Documentación completa del proyecto

Microdemo educativa de testing aplicado a respuestas generadas por un modelo de lenguaje local. El programa envía opiniones de clientes a **Ollama**, utiliza **Gemma 2B** para clasificar su sentimiento y valida la respuesta con Python.

El objetivo principal no es solamente obtener una clasificación, sino mostrar que la forma de evaluar una respuesta de un LLM es tan importante como la respuesta misma.

---

## 1. Objetivos

El proyecto demuestra cómo:

1. Comprobar que un servicio local está disponible.
2. Verificar que un modelo concreto está instalado.
3. Consumir la API HTTP de Ollama desde Python.
4. Medir el tiempo de respuesta del modelo.
5. Normalizar y analizar una respuesta textual.
6. Rechazar respuestas ambiguas o contradictorias.
7. Contabilizar casos aprobados y fallidos.
8. Identificar los límites de una validación basada en texto.

La clasificación utilizada tiene dos valores válidos:

```text
POSITIVO
NEGATIVO
```

---

## 2. Arquitectura y flujo

```text
Opinión del cliente
        |
        v
  test_llm.py
        |
        v
 API local de Ollama
        |
        v
    Gemma 2B
        |
        v
 Respuesta textual
        |
        v
 normalizar_respuesta()
        |
        v
 detectar_sentimiento()
        |
        v
 PASS / FAIL
        |
        v
 Resumen de estadísticas
```

El programa se ejecuta de forma secuencial:

1. Muestra la configuración.
2. Comprueba la conexión con Ollama.
3. Comprueba la instalación del modelo.
4. Envía los tres casos de prueba.
5. Muestra cada opinión, respuesta, sentimiento y duración.
6. Ejecuta la condición de validación.
7. Muestra el resumen final.

---

## 3. Estructura del proyecto

```text
demo-llm-testing/
|
|-- test_llm.py
|-- readme.md
`-- .venv/                 # Entorno virtual local, si se crea
```

### `test_llm.py`

Contiene toda la lógica de configuración, comunicación con Ollama, análisis de respuestas, ejecución de casos y estadísticas.

### `readme.md`

Contiene esta guía de instalación, uso, arquitectura, diagnóstico y mantenimiento.

---

## 4. Requisitos

### 4.1 Python

Se necesita Python 3.10 o posterior. El proyecto ha sido validado con Python 3.14.

Comprobar la instalación:

```powershell
python --version
```

En Windows también puede utilizarse:

```powershell
py --version
```

### 4.2 Ollama

Instalar Ollama desde su sitio oficial y comprobarlo:

```powershell
ollama --version
```

Ollama debe estar ejecutándose en:

```text
http://localhost:11434
```

### 4.3 Modelo

Descargar el modelo configurado:

```powershell
ollama pull gemma:2b
```

Comprobar los modelos disponibles:

```powershell
ollama list
```

Debe aparecer:

```text
gemma:2b
```

### 4.4 Dependencias Python

La aplicación utiliza:

- `requests`: peticiones HTTP a Ollama.
- `pylint`: revisión estática opcional durante el desarrollo.

---

## 5. Instalación recomendada en Windows

Desde la carpeta del proyecto:

```powershell
cd C:\demo-llm-testing
```

Crear un entorno virtual:

```powershell
py -3 -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación de scripts, puede utilizarse directamente el intérprete del entorno sin activarlo:

```powershell
C:\demo-llm-testing\.venv\Scripts\python.exe -m pip install requests pylint
```

Con el entorno activado, instalar las dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install requests pylint
```

Verificar que `requests` esté instalado en el mismo intérprete que utilizará el proyecto:

```powershell
python -c "import requests; print(requests.__version__)"
```

La regla importante es utilizar siempre:

```powershell
python -m pip ...
python -m pylint ...
```

Así se evita instalar paquetes en un Python diferente al que ejecuta el programa.

---

## 6. Configuración del programa

La configuración se encuentra al principio de [test_llm.py](./test_llm.py):

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"

MODEL = "gemma:2b"
TEMPERATURE = 0.0
TIMEOUT = 120
```

### `OLLAMA_URL`

Endpoint utilizado para generar una respuesta:

```text
POST /api/generate
```

### `OLLAMA_TAGS_URL`

Endpoint utilizado para comprobar la disponibilidad de Ollama y consultar los modelos instalados:

```text
GET /api/tags
```

### `MODEL`

Nombre exacto del modelo que debe existir en Ollama. Si se cambia, también debe descargarse el nuevo modelo:

```powershell
ollama pull nombre-del-modelo
```

### `TEMPERATURE`

Temperatura enviada en las opciones de generación. El valor `0.0` busca respuestas más deterministas.

### `TIMEOUT`

Tiempo máximo, en segundos, para una petición de generación. El valor actual es `120`.

---

## 7. Contratos de la API de Ollama

### 7.1 Consulta de modelos

El programa espera que `GET /api/tags` devuelva un objeto JSON con esta forma:

```json
{
  "models": [
    {
      "name": "gemma:2b"
    }
  ]
}
```

La función `verificar_modelo()` comprueba:

1. Que la respuesta sea un objeto JSON.
2. Que `models` sea una lista.
3. Que el nombre configurado esté presente.

### 7.2 Generación de texto

`consultar_llm()` envía un cuerpo equivalente a:

```json
{
  "model": "gemma:2b",
  "prompt": "Analiza el sentimiento...",
  "stream": false,
  "options": {
    "temperature": 0.0
  }
}
```

La aplicación espera una respuesta con un campo de texto:

```json
{
  "response": "El sentimiento general es POSITIVO."
}
```

El modo `stream: false` hace que Ollama devuelva una respuesta completa en lugar de enviarla por fragmentos.

---

## 8. Descripción de las funciones

### `verificar_ollama()`

Realiza una petición `GET` al endpoint de etiquetas. Devuelve:

- `True` si el servidor responde correctamente.
- `False` si existe un error de conexión HTTP.

Si devuelve `False`, `main()` detiene la ejecución porque no se puede continuar sin el servicio.

### `verificar_modelo()`

Consulta los modelos instalados y verifica que `MODEL` aparezca en la lista. También valida la estructura básica de la respuesta JSON.

Devuelve `True` únicamente cuando el modelo configurado está disponible.

### `consultar_llm(texto)`

Construye el prompt, envía la opinión a Ollama y mide el tiempo con `time.perf_counter()`.

Cuando la petición funciona devuelve un diccionario como:

```python
{
    "respuesta": "El sentimiento general es POSITIVO.",
    "tiempo": 1.23,
    "exito": True
}
```

Cuando falla devuelve:

```python
{
    "respuesta": "",
    "tiempo": 1.23,
    "exito": False,
    "error": "mensaje del error"
}
```

Se controlan errores de red, códigos HTTP no exitosos y JSON inválido.

### `normalizar_respuesta(respuesta)`

Elimina espacios al inicio y al final y convierte el texto a mayúsculas:

```python
normalizar_respuesta("  Positivo  ")
# "POSITIVO"
```

### `detectar_sentimiento(respuesta)`

Busca las etiquetas `POSITIVO` y `NEGATIVO`.

Reglas:

| Respuesta | Resultado |
|---|---|
| Contiene únicamente `POSITIVO` | `POSITIVO` |
| Contiene únicamente `NEGATIVO` | `NEGATIVO` |
| Contiene ambas etiquetas | `None` |
| No contiene ninguna etiqueta | `None` |

Devolver `None` para respuestas ambiguas evita falsos positivos.

### `ejecutar_test(nombre, condicion, contar_estadistica=True)`

Evalúa una condición y actualiza el diccionario global `estadisticas`:

```python
estadisticas = {
    "totales": 0,
    "passed": 0,
    "failed": 0
}
```

El parámetro `contar_estadistica` permite ejecutar una comprobación sin incluirla en el resumen.

### `mostrar_resultado(...)`

Imprime la opinión, la respuesta generada, el sentimiento detectado, el valor esperado y el tiempo de respuesta.

### `ejecutar_caso(...)`

Coordina un caso completo:

1. Consulta el modelo.
2. Detiene el caso si la petición falla.
3. Muestra el resultado.
4. Detecta el sentimiento.
5. Compara el resultado con el valor esperado.
6. Registra PASS o FAIL.

El modo `debug` imprime información adicional cuando el caso falla.

### `mostrar_resumen()`

Muestra:

- Casos validados.
- Tests aprobados.
- Tests fallidos.
- Porcentaje de aprobación.

### `main()`

Es el punto de entrada de la aplicación. Verifica el entorno y ejecuta los tres casos definidos.

---

## 9. Ejecución

Con Ollama ejecutándose y el modelo descargado:

```powershell
cd C:\demo-llm-testing
.\.venv\Scripts\python.exe .\test_llm.py
```

Si el entorno ya está activado:

```powershell
python .\test_llm.py
```

El script no inicia Ollama automáticamente. El servicio debe estar disponible antes de ejecutarlo.

---

## 10. Casos incluidos

### Caso 1: opinión negativa

Entrada:

```text
El producto es bueno, pero tardó tres semanas en llegar.
```

Resultado esperado:

```text
NEGATIVO
```

Se ejecuta en modo `debug` para mostrar información adicional si el modelo responde de manera inesperada.

### Caso 2: opinión positiva

Entrada:

```text
Estoy muy feliz con mi compra.
El producto llegó rápido y funciona perfectamente.
```

Resultado esperado:

```text
POSITIVO
```

### Caso 3: opinión negativa

Entrada:

```text
El producto funciona, pero la atención al cliente fue terrible.
```

Resultado esperado:

```text
NEGATIVO
```

---

## 11. Validación y diseño del test

Una validación demasiado permisiva sería:

```python
esperado.upper() in respuesta.upper()
```

Esta condición puede aprobar una respuesta como:

```text
No considero que el sentimiento sea NEGATIVO.
En realidad, la experiencia fue POSITIVA.
```

La palabra `NEGATIVO` aparece, pero la respuesta es contradictoria. Por eso el programa no comprueba solamente una coincidencia aislada: primero identifica qué etiquetas aparecen y considera inválida cualquier respuesta que contenga las dos.

Una comparación de igualdad estricta también puede ser demasiado limitada:

```python
respuesta.strip() == "POSITIVO"
```

El modelo puede responder:

```text
El sentimiento general es POSITIVO.
```

La validación actual acepta explicaciones que contienen una única etiqueta válida, pero rechaza respuestas sin etiqueta o con etiquetas contradictorias.

---

## 12. Diagnóstico de errores

### `Unable to import 'requests'`

Este mensaje pertenece a Pylint y significa que el analizador está usando un intérprete donde no encuentra `requests`.

Instalarlo en el entorno correcto:

```powershell
.\.venv\Scripts\python.exe -m pip install requests
```

Comprobar el import:

```powershell
.\.venv\Scripts\python.exe -c "import requests; print(requests.__version__)"
```

En VS Code seleccionar:

```text
Python: Select Interpreter
-> C:\demo-llm-testing\.venv\Scripts\python.exe
```

### Ollama no está disponible

Comprobar el servicio:

```powershell
Invoke-WebRequest http://localhost:11434/api/tags
```

Si falla, iniciar Ollama y repetir la ejecución.

### El modelo no está instalado

Ejecutar:

```powershell
ollama pull gemma:2b
ollama list
```

### Error de timeout

El modelo puede tardar en iniciar o cargar sus pesos. Se puede aumentar `TIMEOUT`, aunque un timeout alto no corrige una instalación incompleta o un servidor detenido.

### Respuesta JSON inválida

El programa informa del error y marca la consulta como fallida. Esto puede indicar un problema del servicio, una URL incorrecta o una respuesta incompatible con la API esperada.

### Problemas antiguos en VS Code

Después de instalar dependencias o cambiar de intérprete:

1. Guardar el archivo.
2. Seleccionar el intérprete `.venv`.
3. Ejecutar `Developer: Reload Window`.
4. Volver a abrir el panel de problemas.

---

## 13. Revisión estática y validación local

Ejecutar Pylint:

```powershell
.\.venv\Scripts\python.exe -m pylint .\test_llm.py
```

Comprobar sintaxis:

```powershell
.\.venv\Scripts\python.exe -m py_compile .\test_llm.py
```

Comprobar las funciones de análisis sin llamar a Ollama:

```powershell
.\.venv\Scripts\python.exe -c "import test_llm; assert test_llm.detectar_sentimiento('POSITIVO') == 'POSITIVO'; assert test_llm.detectar_sentimiento('NEGATIVO y POSITIVO') is None; print('OK')"
```

Estas comprobaciones no sustituyen una ejecución real contra Ollama: la prueba completa necesita el servidor y el modelo.

---

## 14. Limitaciones conocidas

1. La detección se basa en palabras, no en una comprensión semántica completa.
2. Una respuesta que use sinónimos distintos de `POSITIVO` o `NEGATIVO` puede resultar no identificada.
3. La palabra puede aparecer en una explicación y no representar necesariamente la conclusión.
4. `gemma:2b` puede producir respuestas variables aunque la temperatura sea `0.0`.
5. No se persisten resultados en un archivo o base de datos.
6. No se ejecutan los casos en paralelo.
7. La aplicación no arranca ni instala Ollama automáticamente.
8. No se valida un esquema JSON de salida.

---

## 15. Mejoras futuras

Una siguiente versión podría:

- solicitar una respuesta JSON estructurada;
- validar el esquema y los campos obligatorios;
- añadir un valor de confianza;
- separar el código en módulos;
- agregar pruebas automatizadas con `pytest`;
- simular la API con mocks;
- guardar métricas en CSV o JSON;
- configurar el modelo mediante variables de entorno;
- añadir reintentos con límites;
- registrar errores con `logging`;
- comparar varios modelos;
- medir latencia media y percentiles;
- validar casos neutrales y ambiguos;
- incorporar evaluación semántica además de coincidencia textual.

Ejemplo de salida estructurada futura:

```json
{
  "sentimiento": "NEGATIVO",
  "confianza": 0.92
}
```

---

## 16. Resumen conceptual

Este proyecto enseña una idea fundamental:

> Probar un LLM no significa solamente comprobar que respondió. También significa comprobar que la prueba interpreta correctamente lo que respondió.

Una prueba que busca una palabra puede producir un falso positivo. Una prueba bien diseñada debe definir:

- qué formato se acepta;
- qué valores son válidos;
- cómo se manejan respuestas ambiguas;
- qué ocurre ante errores de red;
- qué ocurre ante respuestas incompletas;
- qué métricas se van a registrar.

---

## 17. Autora

**Giselle Ulloa**

Software Engineer · AI & Cloud · Tech Speaker · GDG Cartagena Lead Organizer · Women Techmakers Ambassador 2026

Cartagena, Colombia
