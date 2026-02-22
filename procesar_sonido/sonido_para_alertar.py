""" Módulo para reproducir sonidos de alerta.
    sean sonidos simples o archivos .wav."""
    
from pathlib import Path
import pygame
import time

def obtener_ruta_escritorio():
    """Obtiene la ruta al escritorio del usuario de manera multiplataforma."""
    return Path.home() / "OneDrive" / "Desktop"
    # En Windows también funciona con:
    # return Path.home() / "OneDrive" / "Desktop"  # Si usas OneDrive


class ObjetoSonido:

    def __init__(self):
        pygame.mixer.init() # Inicializar pygame mixer para sonido
        self.sound = None

    def generar_sonido_beep(self, frequency=440, duration=1000):
        """Genera un sonido de beep simple"""
        SAMPLE_RATE = 22050
        
        # Generar onda sinusoidal simple
        import numpy as np
        frames = int(duration * SAMPLE_RATE / 1000)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            wave = 32767 * np.sin(frequency * 2 * np.pi * i / SAMPLE_RATE)
            arr[i][0] = wave  # Canal izquierdo
            arr[i][1] = wave  # Canal derecho
        
        # Crear instancia para posteriormente reproducir sonido
        self.sound = pygame.sndarray.make_sound(arr.astype(np.int16))

    def reproducir_sonido_beep(self):
        """Reproduce el sonido de beep generado"""
        if self.sound is not None:
            self.sound.play()
            # Esperar a que termine de reproducirse
            while pygame.mixer.get_busy():
                time.sleep(0.1)
            return True
        else:
            print("No hay sonido generado para reproducir.")
            return False

    def reproducir_archivo_wav(self, archivo):
                
        """Reproduce un archivo .wav"""
        valor= "C:\\Users\\User\\OneDrive\\Desktop\\alerta_trader.wav"
        
        ruta_escri = obtener_ruta_escritorio()
        escritorio= str(ruta_escri)
        animo= escritorio.replace("\\", "/")
        pulido= animo + "/" + archivo
        print(pulido); print(type(pulido))
        
        try:
            sonido = pygame.mixer.Sound(pulido)
            sonido.play()
            
            # Esperar a que termine de reproducirse
            while pygame.mixer.get_busy():
                time.sleep(0.1)
                                    
        except pygame.error as e:
            
            print(f"No se pudo reproducir el archivo: {e}")
            # ahora limpiar recursos
            self.limpiar()
            
            return False

    def limpiar(self):
        # Limpiar recursos
        if pygame.mixer.get_init(): # Comprobar si el mixer está inicializado antes de intentar cerrarlo
            pygame.mixer.quit()

reproductor= ObjetoSonido()

