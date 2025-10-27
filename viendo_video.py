"""
viendo_video.py

Funcionalidades:
 - Obtiene URL de stream de YouTube usando yt-dlp
 - Captura frames con OpenCV
 - Cada 1 segundo analiza una región derecha del frame y decide estado: 1 (verde) o 0 (rojo)
 - Muestra en una ventana Pygame únicamente la región analizada
 - Expone endpoint /estado con FastAPI (puerto 8000) que devuelve el último estado

Dependencias: yt-dlp, opencv-python, pygame, fastapi, uvicorn, numpy

Ejecutar: python viendo_video.py
"""

import time
import os
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import threading
from multiprocessing import Process, Queue, Event
import visual_de_pygame
from analizis_de_pixeles import analizar_region, start_frame_reader, get_latest_frame, stop_frame_reader
import uvicorn

# ---------------------- Configuración ----------------------
# URL por defecto (puedes cambiarla desde los endpoints)
YOUTUBE_URL = "https://www.youtube.com/watch?v=-ps7V40GrA4"
ANCHO_REGION = 90  # ancho (en píxeles) de la zona derecha que se analizará
ANALISIS_INTERVALO = 1.0  # segundos entre análisis
# Nota: no fijamos aquí ningún puerto ni arrancamos uvicorn. El servidor
# que despliegue la app (por ejemplo Render) debe ejecutar el ASGI server
# y decidir el puerto mediante su propia configuración/variable de entorno.

# Nota: la obtención de la URL de stream y la lectura continua de frames
# se gestionan ahora en `analizis_de_pixeles` (start_frame_reader / get_latest_frame).

# ---------------------- FastAPI ----------------------
app = FastAPI()
# Dos estados separados:
# - `estado_actual_controlado`: valor que devuelve `/estado` y se actualiza solo
#    si `estado_update_enabled` está True.
# - `estado_actual_vivo`: valor que devuelve `/estado2` y se actualiza siempre.
estado_actual_controlado = {'estado': None}
estado_actual_vivo = {'estado': None}

# Flag que controla si `/estado` debe actualizarse (POST '/visual/{action}' la cambia)
estado_update_enabled = True

# Lock para proteger lecturas/escrituras concurrentes desde FastAPI y el hilo principal
_estado_lock = threading.Lock()

# Variables para cambiar el stream de entrada en caliente
# - `pending_stream_url`: se establece mediante POST /set_pending_stream
# - `apply_pending_url`: flag que al recibir True en /apply_pending_stream
#    provoca que se reemplace la URL actual por la pendiente.
pending_stream_url = None
apply_pending_url = False

# Lock para operaciones de cambio de stream/start/stop
_stream_lock = threading.Lock()

# Altura del video conocida tras leer el primer frame (se setea en main)

# Altura del video conocida tras leer el primer frame (se setea en start_background)
video_height_global = None

# Control del proceso de visualización
visual_process = None
visual_queue = None
visual_stop_event = None

# Variables para hilo de análisis en background (iniciadas en startup)
_bg_thread = None
_bg_stop_event = None

# Variable simple que puedes cambiar llamando a set_visual_enabled(True/False)
# Por defecto: False (la visual no se inicia automáticamente)
VISUAL_DEFAULT_ON = False

def set_visual_enabled(value: bool):
    """Define la variable booleana VISUAL_DEFAULT_ON.
    Esta función SOLO debe asignar la variable y no ejecutar otra lógica.
    """
    global VISUAL_DEFAULT_ON
    VISUAL_DEFAULT_ON = bool(value)
    
@app.get('/estado')
def get_estado():
    # Devuelve el estado controlado (puede estar congelado si la actualización está desactivada)
    with _estado_lock:
        # Devolvemos una copia simple del dict para evitar condiciones de carrera en el cliente
        return JSONResponse(content={'estado': estado_actual_controlado.get('estado')})


@app.get('/estado2')
def get_estado_alterno():
    """Endpoint alternativo (vivo) que devuelve siempre el último estado calculado.

    Este endpoint NO se ve afectado por `estado_update_enabled`.
    """
    with _estado_lock:
        return JSONResponse(content={'estado': estado_actual_vivo.get('estado')})

# Nota: no lanzamos uvicorn desde este módulo. El servidor (p.ej. Render)
# debe ejecutar el comando ASGI apropiado (uvicorn/gunicorn) y decidir el puerto.


@app.post('/visual/{action}')
def control_visual(action: str):
    """(RE-PURPOSED) Controla si el endpoint `/estado` se actualiza.

    Ahora 'on' habilita la actualización de `/estado` y 'off' la deshabilita.
    Nota: `/estado2` (vivo) NO se ve afectado por esta acción.
    """
    global estado_update_enabled
    action = action.lower()
    if action == 'on':
        with _estado_lock:
            estado_update_enabled = True
        return JSONResponse(content={'result': 'estado_updates_enabled'})
    elif action == 'off':
        with _estado_lock:
            estado_update_enabled = False
        return JSONResponse(content={'result': 'estado_updates_disabled'})
    else:
        return JSONResponse(content={'result': 'unknown_action'}, status_code=400)


@app.get('/estado_status')
def estado_status():
    """Devuelve si la actualización del endpoint `/estado` está ON u OFF.

    Respuesta: {'updates_enabled': True/False, 'status': 'on'|'off'}
    """
    with _estado_lock:
        enabled = bool(estado_update_enabled)
    return JSONResponse(content={'updates_enabled': enabled, 'status': 'on' if enabled else 'off'})


@app.post('/set_pending_stream')
def set_pending_stream(payload: dict):
    """Establece una URL de stream pendiente que luego podrá aplicarse.

    Espera JSON: {'stream_url': 'https://www.youtube.com/watch?v=...'}
    """
    global pending_stream_url
    if not isinstance(payload, dict):
        return JSONResponse(content={'result': 'invalid_payload'}, status_code=400)
    url = payload.get('stream_url') or payload.get('url')
    if not url:
        return JSONResponse(content={'result': 'missing_stream_url'}, status_code=400)
    with _stream_lock:
        pending_stream_url = str(url)
    return JSONResponse(content={'result': 'pending_set', 'pending_stream_url': pending_stream_url})


@app.post('/apply_pending_stream')
def apply_pending_stream(value=Body(...)):
    """Si recibe True (o {'apply': True} o variantes), aplica la `pending_stream_url`.

    Acepta los siguientes cuerpos JSON válidos:
      - true
      - "true" (string)
      - {"apply": true}
      - {"apply": "True"}

    Tras aplicar, devuelve {'result':'applied', 'new_url': ...} y deja el flag en False.
    """
    global pending_stream_url, apply_pending_url, YOUTUBE_URL

    # Normalizar valor entrante a boolean. Puede venir como bool, str, int o dict
    apply_val = False
    try:
        # Si envían un objeto JSON (dict) buscamos clave 'apply' o 'value'
        if isinstance(value, dict):
            # Priorizar 'apply' luego 'value'
            candidate = None
            if 'apply' in value:
                candidate = value['apply']
            elif 'value' in value:
                candidate = value['value']
            else:
                # si el dict tiene un solo elemento, intentar usar su valor
                if len(value) == 1:
                    candidate = list(value.values())[0]
            # Resolver candidate a boolean
            if isinstance(candidate, bool):
                apply_val = candidate
            elif isinstance(candidate, (int, float)):
                apply_val = bool(candidate)
            elif isinstance(candidate, str):
                s = candidate.strip()
                apply_val = s.lower().lstrip('/') in ('true', '1', 'on')
        else:
            # valor primitivo (bool, str, number)
            if isinstance(value, bool):
                apply_val = value
            elif isinstance(value, (int, float)):
                apply_val = bool(value)
            else:
                s = str(value).strip()
                apply_val = s.lower().lstrip('/') in ('true', '1', 'on')
    except Exception:
        apply_val = False

    if not apply_val:
        # Si se envía False, simplemente aseguramos que el flag esté a False
        with _stream_lock:
            apply_pending_url = False
        return JSONResponse(content={'result': 'not_applied', 'apply_pending_url': False})

    # apply_val == True: intentar aplicar la URL pendiente
    with _stream_lock:
        if not pending_stream_url:
            return JSONResponse(content={'result': 'no_pending_url'}, status_code=400)
        new_url = pending_stream_url
        # indicar que estamos procesando
        apply_pending_url = True

    # Stop current reader and start new one. Do this fuera del lock para evitar deadlocks
    try:
        stop_frame_reader()
    except Exception:
        pass

    stream_url, frame = start_frame_reader(new_url)
    if not stream_url:
        with _stream_lock:
            apply_pending_url = False
        return JSONResponse(content={'result': 'failed_to_start_new_stream'}, status_code=500)

    # success: update global YOUTUBE_URL and clear pending
    with _stream_lock:
        YOUTUBE_URL = new_url
        pending_stream_url = None
        apply_pending_url = False

    return JSONResponse(content={'result': 'applied', 'new_url': YOUTUBE_URL})


def start_visual():
    """Inicia el proceso de visualización si no está ya iniciado."""
    global visual_process, visual_queue, visual_stop_event
    if visual_process is not None and visual_process.is_alive():
        return False
    visual_queue = Queue(maxsize=2)
    visual_stop_event = Event()
    height = video_height_global if video_height_global is not None else 480
    visual_process = Process(target=visual_de_pygame.visual_loop, args=(visual_queue, visual_stop_event, ANCHO_REGION, height))
    visual_process.start()
    return True


def stop_visual():
    """Detiene el proceso de visualización si está activo."""
    global visual_process, visual_queue, visual_stop_event
    if visual_process is None:
        return False
    try:
        if visual_stop_event is not None:
            visual_stop_event.set()
        visual_process.join(timeout=2)
        if visual_process.is_alive():
            visual_process.terminate()
    finally:
        visual_process = None
        visual_queue = None
        visual_stop_event = None
    return True

# ---------------------- Análisis de color ----------------------
from analizis_de_pixeles import analizar_region

# ---------------------- Programa principal ----------------------
def _analysis_loop(stop_ev: threading.Event):
    """Bucle de análisis que se puede ejecutar en un hilo de fondo.
    Recibe un Event para indicar parada.
    """
    ultimo_analisis = 0.0
    try:
        # Si la variable por defecto indica iniciar la visual, arrancarla
        if VISUAL_DEFAULT_ON:
            start_visual()

        while not stop_ev.is_set():
            ahora = time.time()
            if ahora - ultimo_analisis >= ANALISIS_INTERVALO:
                current = get_latest_frame()
                if current is None:
                    time.sleep(0.05)
                    ultimo_analisis = ahora
                    continue

                region = current[:, -ANCHO_REGION:]
                estado, cnt_rojo, cnt_verde = analizar_region(region)
                with _estado_lock:
                    val = int(estado) if estado is not None else None
                    estado_actual_vivo['estado'] = val
                    if estado_update_enabled:
                        estado_actual_controlado['estado'] = val

                # imprimir para debugging en logs
                print(f'Estado: {estado}  (rojo={cnt_rojo}, verde={cnt_verde})')

                try:
                    if visual_queue is not None:
                        visual_queue.put(region, block=False)
                except Exception:
                    pass

                ultimo_analisis = ahora

            time.sleep(0.01)
    except Exception:
        # En caso de excepción, solo salir (los handlers de shutdown limpiarán recursos)
        return


def start_background():
    """Inicia la captura de frames y el hilo de análisis en background.

    Esta función será llamada automáticamente en el evento `startup` de FastAPI
    (ver abajo), pero también puede invocarse manualmente si se desea.
    """
    global _bg_thread, _bg_stop_event, video_height_global
    with _stream_lock:
        stream_url, frame = start_frame_reader(YOUTUBE_URL)
    if not stream_url:
        print('Advertencia: no se pudo obtener la URL de stream en start_background')

    # Determinar dimensiones si tenemos un primer frame
    if frame is not None:
        video_h, video_w = frame.shape[:2]
    else:
        tmp = get_latest_frame()
        if tmp is None:
            video_h, video_w = 480, 640
        else:
            video_h, video_w = tmp.shape[:2]

    video_height_global = int(video_h)

    # Iniciar cola/proceso visual si procede (no forzamos que arranque)
    # Iniciar el hilo de análisis
    if _bg_thread is None or not _bg_thread.is_alive():
        _bg_stop_event = threading.Event()
        _bg_thread = threading.Thread(target=_analysis_loop, args=(_bg_stop_event,), daemon=True)
        _bg_thread.start()


def stop_background():
    """Detiene el hilo de análisis, la captura y la visualización.
    """
    global _bg_thread, _bg_stop_event
    try:
        if _bg_stop_event is not None:
            _bg_stop_event.set()
        if _bg_thread is not None:
            _bg_thread.join(timeout=2)
    except Exception:
        pass

    try:
        stop_frame_reader()
    except Exception:
        pass

    try:
        stop_visual()
    except Exception:
        pass


# FastAPI lifecycle: arrancar/detener el procesamiento en background
@app.on_event("startup")
def _on_startup():
    # Este handler se ejecuta cuando el ASGI server importa y arranca la app.
    # Iniciamos la captura y el hilo de análisis aquí para que siempre esté activo
    # cuando se sirvan los endpoints.
    start_background()


@app.on_event("shutdown")
def _on_shutdown():
    # Al apagar el servidor, limpiamos recursos.
    stop_background()


# Nota: este módulo exporta `app`. En despliegues típicos (Render) debes
# proporcionar un Start Command que lance uvicorn/gunicorn importando
# `viendo_video:app`. Si prefieres ejecutar localmente con `python` puedes
# hacerlo ejecutando este archivo directamente; el bloque `__main__` a
# continuación arrancará uvicorn usando la variable de entorno PORT si existe.


if __name__ == '__main__':
    # Permitir que el puerto sea tomado desde la variable de entorno PORT
    port_env = os.environ.get('PORT')
    try:
        port = int(port_env) if port_env is not None else 8000
    except Exception:
        port = 8000

    # Ejecutar uvicorn embebido solo cuando el archivo se ejecuta como script.
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')
