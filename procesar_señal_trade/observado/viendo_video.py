
"""
viendo_video.py

Funcionalidades:
 - Obtiene URL de stream de YouTube usando yt-dlp
 - Captura frames con OpenCV
 - Analiza una región derecha del frame y decide estado: 1 (verde) o 0 (rojo)
 - Devuelve dos variables estado con un retardo de 1 segundo entre ellas

Dependencias: yt-dlp, opencv-python, numpy

"""

import time
import threading
from multiprocessing import Process, Queue, Event

from objeto_control_general import control_general

from procesar_señal_trade.observado import visual_de_pygame
#from observado import visual_de_pygame
from procesar_señal_trade.observado.analizis_de_pixeles import analizar_region, start_frame_reader, get_latest_frame, stop_frame_reader
#from observado.analizis_de_pixeles import analizar_region, start_frame_reader, get_latest_frame, stop_frame_reader
#from analizis_de_pixeles import analizar_region, start_frame_reader, get_latest_frame, stop_frame_reader

# ---------------------- Clase Operando_video ----------------------
class Operando_video:
        
    def __init__(self):
        self.estado= None
        
        control_general.pixeles_a_observar= 90 # ancho (en píxeles) de la zona derecha que se analizará
        self.estado_de_url= False
        self.alternativa_para_url= None
 
        self.stream_url= None
        self.frame= None

        # Control del proceso de visualización
        self.visual_process = None
        self.visual_queue = None
        self.visual_stop_event = None
        self.video_height = None
        self.region= None
        
        self.salto_actualizacion_de_queue= True
        
        self.iniciar_captura()

    def iniciar_captura(self):

        # Iniciar captura de primer frame
        if self.estado_de_url == False:
            self.stream_url, self.frame = start_frame_reader(control_general.nueva_url_de_video)
        else:
            self.stream_url, self.frame = start_frame_reader(self.alternativa_para_url)

        # Capturar altura del frame si existe
        if self.frame is not None:
            self.video_height = self.frame.shape[0]  # altura del frame
        
    def actualizo_ventana_pygame(self):
        
        while True:
            try:                
                self.visual_queue.put(self.region, timeout=0.016)
            except:
                # aun sin actualizar
                time.sleep(0.3)
            
    def analysis(self):
        """Consiguiendo analizis."""
        current = get_latest_frame()

        if current is None:
            print("Error: no se pudo obtener el frame actual.")
            self.estado = None
            self.estado_obtenido = True
            return

        region = current[:, -90:]
        estado, cnt_rojo, cnt_verde = analizar_region(region)
        
        self.estado = int(estado)
        self.estado_obtenido = True

    def start_analysis(self):
        """Inicia la captura de frames y el hilo de análisis."""
                
        # Verificar si se obtuvo la URL de stream
        if not self.stream_url:
            print('Error: no se pudo obtener la URL de stream')
        else:
            self.analysis()
        
    def stop_analysis(self):
        # Detener captura de frames
        stop_frame_reader()
        
    def start_visual(self):
        """Inicia el proceso de visualización si no está ya iniciado."""
        if self.visual_process is not None and self.visual_process.is_alive():
            return False

        # Crear la Queue para enviar frames al proceso visual
        self.visual_queue = Queue(maxsize=2)
        self.visual_stop_event = Event()

        height = self.video_height if self.video_height is not None else 360

        # Esperar frame válido antes de hacer slicing
        while True:
            current = get_latest_frame()
            if current is not None:
                region = current[:, -control_general.pixeles_a_observar:]
                self.visual_queue.put(region, timeout=0.016)
                break
            else:
                print("Esperando frame válido para visualización...")
                time.sleep(0.5)

        # Pasar la Queue a ser visualizada
        self.visual_process = Process(
            target=visual_de_pygame.visual_loop,
            args=(self.visual_queue, self.visual_stop_event, control_general.pixeles_a_observar, height)
        )
        self.visual_process.start()

        # realizo las actualizaciones de pygame (en un bucle aparte)
        hilo_aisla_boton = threading.Thread(target=self.actualizo_ventana_pygame, daemon=True)
        hilo_aisla_boton.start()
        print("se esta produciendo el ciclo") # para comprobar cuando funciona
                        
    def stop_visual(self):
        """Detiene el proceso de visualización si está activo."""
        if self.visual_process is None:
            return False
        try:
            if self.visual_stop_event is not None:
                self.visual_stop_event.set()
            self.visual_process.join(timeout=2)
            if self.visual_process.is_alive():
                self.visual_process.terminate()
        finally:
            self.visual_process = None
            self.visual_queue = None
            self.visual_stop_event = None
        return True
        
    def abrir_nueva_url(self, nueva_url):
        """Abre una nueva URL de video para análisis."""        
        
        self.alternativa_para_url= nueva_url    # DEfiniendo nueva variable.
        self.estado_de_url= True
    
    def reajustar_region(self, ancho_region):
        """Reajusta la región de análisis si es necesario."""
        control_general.pixeles_a_observar= ancho_region
    
    def abrir_ventana_pygame(self):
        """Abre una ventana para visualizar la región de análisis."""
        self.iniciar_captura()
        self.start_visual()
        
datos= Operando_video()

class SeñalTrade:

    def __init__(self):
        self.primer_estado = None
        self.segundo_estado = None
        
    def devuelve_estado_vivo(self):
        """Devuelve el objeto que contiene los estados."""
        
        # Espera para obtener dos estados con retardo
        #datos.start_analysis()
        #self.segundo_estado= datos.estado
        
        time.sleep(4)  # Retardo de 4 segundo
        datos.start_analysis()
        self.primer_estado= datos.estado
        
        listado_estados= [self.primer_estado, self.segundo_estado]
        
        return listado_estados
    
    def fin_del_analisis(self):
        """Finaliza el análisis de video."""
        datos.stop_analysis()
        print("Análisis de video finalizado.")
        
        if datos.visual_process is not None:
            datos.stop_visual()
        
                
fluctuacion_señal= SeñalTrade()

