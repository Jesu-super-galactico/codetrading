"""
analizis_de_pixeles.py

Funciones para analizar píxeles/porciones de frames (separado de los endpoints
y de la gestión de captura). Actualmente exporta `analizar_region`.

Mantiene la misma API que antes: recibe una porción BGR (numpy array) y devuelve
una tupla (estado, cnt_rojo, cnt_verde) donde estado es 1 si predomina verde
o 0 si predomina rojo.
"""
import cv2
import numpy as np
import yt_dlp
import threading
import time

# Opciones por defecto para yt-dlp (silencioso, no descargar)
ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'noplaylist': True,
}

# Recursos internos del lector de frames
_cap = None
_latest_frame = None
_lock = threading.Lock()
_thread = None
_stop_event = None

def analizar_region(region):
    """Recibe una porción BGR y devuelve (estado, rojo_count, verde_count).
    estado: 1 si predomina verde, 0 si predomina rojo.
    """
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    rojo_bajo1 = np.array([0, 100, 100])
    rojo_alto1 = np.array([10, 255, 255])
    rojo_bajo2 = np.array([160, 100, 100])
    rojo_alto2 = np.array([179, 255, 255])
    verde_bajo = np.array([40, 100, 100])
    verde_alto = np.array([80, 255, 255])
    mask_rojo = cv2.inRange(hsv, rojo_bajo1, rojo_alto1) | cv2.inRange(hsv, rojo_bajo2, rojo_alto2)
    mask_verde = cv2.inRange(hsv, verde_bajo, verde_alto)
    cnt_rojo = int(cv2.countNonZero(mask_rojo))
    cnt_verde = int(cv2.countNonZero(mask_verde))
    estado = 1 if cnt_verde > cnt_rojo else 0
    return estado, cnt_rojo, cnt_verde


def obtener_stream_url(url):
    """Obtiene la URL directa del stream (ffmpeg/http) usando yt-dlp.
    Devuelve la URL si se encuentra, o None.
    """
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'url' in info:
                return info['url']
            if 'formats' in info:
                formats = [f for f in info['formats'] if f.get('url')]
                if formats:
                    formats.sort(key=lambda x: x.get('height', 0) or x.get('tbr', 0), reverse=True)
                    return formats[0]['url']
    except Exception:
        return None
    return None


def _reader_loop(cap_obj, stop_ev):
    global _latest_frame
    try:
        while not stop_ev.is_set():
            ret, frm = cap_obj.read()
            if not ret:
                time.sleep(0.05)
                continue
            with _lock:
                _latest_frame = frm.copy()
    except Exception:
        return


def start_frame_reader(url, direct=False):
    """Inicia la captura y un hilo que mantiene `_latest_frame` actualizado.
    `url` puede ser una URL de YouTube (o cualquier URL aceptada por yt-dlp).
    Devuelve (stream_url, first_frame) o (None, None) en caso de fallo.
    """
    global _cap, _thread, _stop_event, _latest_frame
    if url is None:
        return None, None

    # Si `direct=True` asumimos que `url` ya es la URL directa del stream
    # (p. ej. mp4/http). Evitamos llamar a yt-dlp para no incurrir en
    # descargas/limitaciones de YouTube.
    stream_url = url if direct else obtener_stream_url(url)
    if not stream_url:
        return None, None

    _cap = cv2.VideoCapture(stream_url)
    if not _cap.isOpened():
        return stream_url, None

    ret, frame = _cap.read()
    if not ret:
        # No pudimos leer primer frame, pero mantenemos la captura abierta
        return stream_url, None

    with _lock:
        _latest_frame = frame.copy()

    _stop_event = threading.Event()
    _thread = threading.Thread(target=_reader_loop, args=(_cap, _stop_event), daemon=True)
    _thread.start()
    return stream_url, frame


def get_latest_frame():
    """Devuelve una copia del último frame leído o None si no hay.
    """
    with _lock:
        return None if _latest_frame is None else _latest_frame.copy()


def stop_frame_reader():
    """Detiene el lector de frames y libera la captura.
    """
    global _cap, _thread, _stop_event
    try:
        if _stop_event is not None:
            _stop_event.set()
        if _thread is not None:
            _thread.join(timeout=2)
    except Exception:
        pass
    try:
        if _cap is not None:
            _cap.release()
    except Exception:
        pass
    _thread = None
    _stop_event = None
    _cap = None
