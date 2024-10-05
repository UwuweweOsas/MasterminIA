import pygame
import random
import itertools

pygame.init()

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
VERDE = (0, 255, 0)
GRIS = (128, 128, 128)

ancho = 500
alto = 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Mastermind")

colores = [ROJO, AZUL, AMARILLO, VERDE]
codigo_secreto = random.sample(colores, 4)
intentos = 10
tamaño_circulo = 30
espaciado = 10

def dibujar_circulos(fila, colores_elegidos):
    for i, color in enumerate(colores_elegidos):
        pygame.draw.circle(pantalla, color, (50 + i * (tamaño_circulo + espaciado), fila), tamaño_circulo // 2)

def dibujar_pistas(fila, correctos, incorrectos):
    for i in range(correctos):
        pygame.draw.circle(pantalla, NEGRO, (250 + i * 20, fila), 5)
    for i in range(incorrectos):
        pygame.draw.circle(pantalla, BLANCO, (250 + (i + correctos) * 20, fila), 5)

def generar_todas_combinaciones():
    return list(itertools.permutations(colores, 4))

def calcular_pista(codigo, intento):
    codigo_copia = list(codigo)
    intento_copia = list(intento)
    correctos = sum(1 for a, b in zip(codigo, intento) if a == b)
    
    for i in range(4):
        if codigo_copia[i] == intento_copia[i]:
            codigo_copia[i] = None
            intento_copia[i] = None
    
    incorrectos = sum(1 for color in intento_copia if color in codigo_copia and color is not None)
    return correctos, incorrectos

def eliminar_inconsistentes(combinaciones, intento, pista):
    return [comb for comb in combinaciones if calcular_pista(comb, intento) == pista]

def siguiente_intento_ia(combinaciones, intentos_anteriores):
    if not intentos_anteriores:
        return (ROJO, AZUL, AMARILLO, VERDE)
    
    min_max = float('inf')
    mejor_intento = None

    for intento in combinaciones:
        max_eliminados = 0
        for pista in itertools.product(range(5), repeat=2):
            if sum(pista) <= 4:
                eliminados = len(combinaciones) - len(eliminar_inconsistentes(combinaciones, intento, pista))
                max_eliminados = max(max_eliminados, eliminados)
        
        if max_eliminados < min_max:
            min_max = max_eliminados
            mejor_intento = intento

    return mejor_intento

def juego_mastermind():
    jugando = True
    intento_actual = 0
    colores_elegidos = []
    intentos_anteriores = []
    pistas_anteriores = []
    mensaje = ""
    modo_ia = False
    combinaciones_posibles = generar_todas_combinaciones()

    while jugando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jugando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 400 < x < 490 and 10 < y < 40:
                    modo_ia = not modo_ia
                    mensaje = "Modo IA: " + ("Activado" if modo_ia else "Desactivado")
                    colores_elegidos = []
                    intento_actual = 0
                    intentos_anteriores = []
                    pistas_anteriores = []
                    combinaciones_posibles = generar_todas_combinaciones()
                elif not modo_ia and intento_actual < intentos:
                    if y > alto - 50:
                        indice_color = x // (ancho // 4)
                        if indice_color < 4 and len(colores_elegidos) < 4:
                            color = colores[indice_color]
                            if color not in colores_elegidos:
                                colores_elegidos.append(color)
                    elif 300 < x < 380 and 10 < y < 40 and len(colores_elegidos) == 4:
                        correctos, incorrectos = calcular_pista(codigo_secreto, colores_elegidos)
                        intentos_anteriores.append(colores_elegidos)
                        pistas_anteriores.append((correctos, incorrectos))
                        mensaje = f"Colores correctos: {correctos}, Colores incorrectos: {incorrectos}"
                        if correctos == 4:
                            mensaje += " Ganaste!"
                            jugando = False
                        elif intento_actual == intentos - 1:
                            mensaje += " Perdiste!"
                            jugando = False
                        else:
                            intento_actual += 1
                            colores_elegidos = []

        if modo_ia and intento_actual < intentos:
            colores_elegidos = siguiente_intento_ia(combinaciones_posibles, intentos_anteriores)
            correctos, incorrectos = calcular_pista(codigo_secreto, colores_elegidos)
            intentos_anteriores.append(colores_elegidos)
            pistas_anteriores.append((correctos, incorrectos))
            combinaciones_posibles = eliminar_inconsistentes(combinaciones_posibles, colores_elegidos, (correctos, incorrectos))
            mensaje = f"IA - Colores correctos: {correctos}, Colores incorrectos: {incorrectos}"
            if correctos == 4:
                mensaje += " La IA gano!"
                jugando = False
            elif intento_actual == intentos - 1:
                mensaje += " La IA perdio"
                jugando = False
            intento_actual += 1
            pygame.time.wait(1000)

        pantalla.fill(GRIS)

        for i, color in enumerate(colores):
            pygame.draw.circle(pantalla, color, (ancho // 8 + i * ancho // 4, alto - 25), tamaño_circulo // 2)

        pygame.draw.rect(pantalla, VERDE, (300, 10, 80, 30))
        pygame.draw.rect(pantalla, AZUL, (400, 10, 90, 30))
        fuente = pygame.font.Font(None, 24)
        texto = fuente.render("Verificar", True, NEGRO)
        pantalla.blit(texto, (305, 15))
        texto = fuente.render("Modo IA", True, NEGRO)
        pantalla.blit(texto, (410, 15))

        if mensaje:
            lineas = mensaje.split(". ")
            for i, linea in enumerate(lineas):
                texto_mensaje = fuente.render(linea, True, NEGRO)
                pantalla.blit(texto_mensaje, (10, alto - 80 + i * 20))

        for i, (intento, pista) in enumerate(zip(intentos_anteriores, pistas_anteriores)):
            dibujar_circulos(50 + i * 50, intento)
            dibujar_pistas(50 + i * 50, pista[0], pista[1])

        dibujar_circulos(50 + intento_actual * 50, colores_elegidos)

        pygame.display.flip()

    dibujar_circulos(alto - 100, codigo_secreto)
    pygame.display.flip()
    pygame.time.wait(3000)

juego_mastermind()
pygame.quit()