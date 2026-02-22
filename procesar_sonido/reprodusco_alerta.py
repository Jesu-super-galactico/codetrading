
"""  Módulo para reproducir alguna alerta sonora. """


"========================================================"
# importar el reproductor de sonido
import time

#from sonido_para_alertar import reproductor
from procesar_sonido.sonido_para_alertar import reproductor

"========================================================"

def procesar_senales_trading(modo= True, tendencia= True):
    
    suceso= modo
    
    # solo pueden resultar haber dos tipos de salidas (y la determina 'suceso')
    if suceso == False:
        # Alerta crítica (usando archivo .wav si existe)
        print("⚠️ ALERTA CRÍTICA!")
                
        try:
            reproductor.reproducir_archivo_wav("alerta_trader.wav")
        except Exception as e:
            print(f"Error al reproducir archivo .wav: {e}")
            suceso= True

    if suceso == True:
        "Si no hay archivo, usar beep de emergencia"

        if tendencia == True:
            print("📈 Señal de COMPRA detectada!")
            reproductor.generar_sonido_beep(frequency=800, duration=100)
            for i in range(4):
                reproductor.reproducir_sonido_beep()
                time.sleep(0.1)
        
        else:
            print("📉 Señal de VENTA detectada!")
            reproductor.generar_sonido_beep(frequency=220, duration=1300)
            reproductor.reproducir_sonido_beep()

