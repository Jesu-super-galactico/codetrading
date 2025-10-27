README - viendo_video (FastAPI + análisis de vídeo)
===============================================

Resumen
-------
Este pequeño proyecto captura frames desde una URL de streaming (por ejemplo YouTube), analiza una región derecha del frame para detectar predominio de color (rojo/verde) y expone endpoints HTTP con FastAPI para consultar el estado.

Características principales
- Obtención de URL de stream con `yt-dlp`.
- Captura de frames con OpenCV en un hilo separado.
- Análisis de una región (BGR -> HSV) para decidir estado (verde=1, rojo=0).
- Endpoints FastAPI:
	- GET /estado    -> devuelve el estado "controlado" (se actualiza según flag)
	- GET /estado2   -> devuelve el estado "vivo" (siempre actualizado)
	- POST /set_pending_stream  -> establecer URL pendiente
	- POST /apply_pending_stream -> aplicar la URL pendiente
	- POST /visual/{on|off} -> activar/desactivar actualización de `/estado`

Estructura
---------
- `viendo_video.py`: aplicación FastAPI y lógica de arranque del background thread.
- `analizis_de_pixeles.py`: funciones de lectura de stream y análisis de región.
- `visual_de_pygame.py`: proceso independiente para mostrar la región (opcional).
- `requirements.txt`: dependencias del proyecto.

Dependencias
------------
Instala las dependencias listadas en `requirements.txt`. Para un entorno virtual en Windows PowerShell:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ejecución local (rápida)
-----------------------
Puedes ejecutar la aplicación usando Python directamente (esto lanzará uvicorn embebido usando el bloque `if __name__ == '__main__'`):

```powershell
# puerto por defecto 8000
python viendo_video.py
# o especificando puerto
$env:PORT=8080; python viendo_video.py
```

Ejecución recomendada / despliegue en Render
-------------------------------------------
Parte de la aplicación exporta la variable `app` (FastAPI). En un host como Render deberías configurar el Start Command para ejecutar un ASGI server importando esa app. Render proporciona la variable de entorno `$PORT` que debes usar en el comando.

Comandos recomendados para Start Command:

- Desarrollo (uvicorn):

```text
uvicorn viendo_video:app --host 0.0.0.0 --port $PORT
```

- Producción (gunicorn + uvicorn workers) — más robusto para concurrencia:

```text
gunicorn -k uvicorn.workers.UvicornWorker viendo_video:app --bind 0.0.0.0:$PORT
```

Notas para Render
-----------------
- Asegúrate de que `requirements.txt` esté en la raíz del servicio para que Render instale las dependencias.
- Render ejecutará el Start Command; al importar `viendo_video:app` se ejecutarán los handlers `@app.on_event('startup')` y se arrancará el hilo de análisis en background.
- Si no configuras Start Command, la plataforma no arrancará la app automáticamente — debes proporcionar ese comando (o usar `python viendo_video.py` como Start Command si prefieres arrancar uvicorn embebido).

Consideraciones sobre Pygame / visualización
--------------------------------------------
- La visualización con Pygame requiere un entorno gráfico (display). En servidores headless (como Render) normalmente no funcionará. Mantén `VISUAL_DEFAULT_ON = False` para despliegues en la nube.
- La parte visual se ejecuta en un proceso separado y es opcional.

Variables de entorno útiles
--------------------------
- `PORT`: puerto en el que escuchar (Render define esto automáticamente). Si ejecutas con `python viendo_video.py` y `PORT` no existe, usa 8000.

Recomendaciones
---------------
- Para desarrollo local, `python viendo_video.py` es cómodo.
- Para despliegue en Render, crear Start Command con uvicorn o gunicorn y usar `$PORT`.
- Considera fijar versiones en `requirements.txt` si quieres reproducibilidad.

Problemas comunes y debugging
-----------------------------
- Si al arrancar ves errores relacionados con Pygame en la nube, desactiva la visualización.
- Si no llegan frames, revisa que `yt-dlp` esté funcionando y que la URL de YouTube sea accesible.

Contacto / siguiente pasos
--------------------------
Si quieres, puedo:
- Añadir un script de despliegue para Render.
- Pinnear versiones en `requirements.txt`.
- Añadir un archivo `Procfile` o plantilla de configuración para Render.

Ejemplo alternativo de Start Command
-----------------------------------
Si prefieres no usar gunicorn/uvicorn desde la plataforma y quieres que el
propio script arranque el servidor (uvicorn embebido), puedes usar este
Start Command alternativo. El script `viendo_video.py` acepta la variable
de entorno `PORT` y la usará si está definida.

Comando alternativo (arranca uvicorn embebido mediante `python`):

```text
python viendo_video.py
```

En Render puedes usar exactamente `python viendo_video.py` como Start Command
si prefieres no escribir el comando de uvicorn/gunicorn. Ten en cuenta que
esto ejecuta el servidor en el mismo proceso y es más apropiado para
desarrollo o despliegues sencillos; para producción se recomienda
gunicorn+uvicorn workers.

