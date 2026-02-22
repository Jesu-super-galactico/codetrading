"""
visual_de_pygame.py

Proceso separado que recibe frames (región BGR) desde una multiprocessing.Queue
y los muestra en una ventana Pygame. Se detiene cuando se recibe un Event de parada.
"""
import pygame
import numpy as np
import time

def visual_loop(frame_queue, stop_event, width, height):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Zona analizada (visual)')

    last_surface = None
    try:
        while not stop_event.is_set():
            # Procesar eventos para permitir cerrar la ventana desde el usuario
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    stop_event.set()

            # Intentar obtener frame más reciente (non-blocking con timeout corto)
            try:
                region = frame_queue.get(timeout=0.1)
                # region es un array BGR (numpy)
                region_rgb = np.array(region, copy=True)
                region_rgb = region_rgb[:, :, ::-1]  # BGR -> RGB
                # Ajustar orientación para Pygame (rotar y voltear si es necesario)
                surface = pygame.surfarray.make_surface(np.fliplr(np.rot90(region_rgb, 3)))
                last_surface = surface
            except Exception:
                # timeout o cola vacía
                pass

            if last_surface is not None:
                screen.blit(last_surface, (0, 0))
                pygame.display.flip()

            time.sleep(0.01)
    finally:
        pygame.quit()
