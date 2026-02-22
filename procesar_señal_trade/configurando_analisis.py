
""" modulo que configura el análisis de la señal de trade """


"========================================================"
# importaciones necesarias
from procesar_señal_trade.observado.viendo_video import datos
#from observado.viendo_video import fluctuacion_señal, datos

"========================================================"

def ajustar_region_analisis(ancho_region):
    """Ajusta la región de análisis de la señal de trading."""
    datos.reajustar_region(ancho_region)
    
def analizar_video_con_nueva_url(nueva_url):
    """Abre una nueva URL de video para análisis."""
    datos.abrir_nueva_url(nueva_url)
    
def actualiza_configuracion_analisis(url, ancho_region):
    """Actualiza la configuración del análisis de la señal de trading."""
    ajustar_region_analisis(ancho_region)
    analizar_video_con_nueva_url(url)
    
def visualizar_region_analisis():
    " observar la región de análisis "
    datos.abrir_ventana_pygame()

