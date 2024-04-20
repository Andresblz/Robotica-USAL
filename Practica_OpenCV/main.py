import cv2
import numpy as np

target_distance = 30

def searchRedSquare(image):
    x = y = z = None
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0: 
        if existQR(image): # Comprobar si hay cuadrados negros en la imagen para retroceder o decir que no hay QR
            z = -1
    else:
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

            if len(approx) == 4: 
                x, y, w, h = cv2.boundingRect(cnt)
                ratio = float(w) / h
                if ratio >= 0.9 and ratio <= 1.1: # Si es un cuadrado
                    cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)
                    x, y = position(image, approx, len(approx))
                    if existQR(image):
                        z = calculateDistance(approx)
                else: # Si es un rectangulo
                    # con el ratio y rect comprobamos si es vertical (true) u horizontal (false)
                    ratio = float(w) / h
                    cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)
                    rect = True if ratio >= 0.9 and ratio <= 1.1 else False

                    if existQR(image):
                        x, y = searchQRPosition(image, rect) # Comprobamos donde está la mayor parte del QR y decimos que retroceda
                        z = -1
                    else:
                        x, y = position(image, approx, len(approx)) # No hay QR, buscamos solo la posición del rectangulo
            elif len(approx) == 6: # Está cortada en una esquina
                cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)
                x, y = position(image, approx, len(approx))
            elif len(approx) == 8: # Esta cortado en un lateral
                cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)
                x, y = position(image, approx, len(approx))
    
    showResults(x, y, z)

def existQR(image):
    contours = searchContoursQR(image)
    
    if len(contours) > 0:
        return True
    
    return False

def searchQRPosition(image, rect):
    height, width, _ = image.shape
    x = y = None
    contours = searchContoursQR(image)

    left_area = right_area = top_area = bottom_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        if x + w < width / 2:
            left_area += area
        elif x > width / 2:
            right_area += area
        if y + h < height / 2:
            top_area += area
        elif y > height / 2:
            bottom_area += area

    if rect:
        x = -1 if left_area > right_area else 1
    else:
        y = -1 if bottom_area > top_area else 1

    return x, y

def searchContoursQR(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])
    mask = cv2.inRange(hsv, lower_black, upper_black)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def position(image, approx, type):
    height, width, _ = image.shape
    halfHeight = height / 2
    halfWidth = width / 2
    x = y = 0

    if type == 4: # El cuadrado
        xapprox = (approx[0][0][0] + approx [2][0][0]) / 2 
        yapprox = (approx[0][0][1] + approx [1][0][1]) / 2

        if (halfHeight + 5) < yapprox and (halfHeight - 5) < yapprox:
            y = -1
        elif (halfHeight + 5) > yapprox and (halfHeight - 5) > yapprox:
            y = 1

        if (halfWidth + 5) < xapprox and (halfWidth - 5) < xapprox:
            x = 1
        elif (halfWidth + 5) > xapprox and (halfWidth - 5) > xapprox:
            x = -1

    elif type == 6: # Cortado por la esquina
        firstX = approx[0][0][0]
        firstY = approx[0][0][1]
        secondX = approx[3][0][0]
        secondY = approx[3][0][1]

        if firstY == 0 and secondX == 0:
            x = -1
            y = 1
        elif firstY == 0 and secondX == width-1:
            x = 1
            y = 1
        elif firstX == 0 and secondY == height-1:
            x = -1
            y = -1
        elif firstX == width-1 and secondY == height-1: 
            x = 1
            y = -1
    else: # Cortado en un lateral
        move = (approx[0][0][0])

        if move == 0: # Si la x de 0 vale 0 entramos aquí y comparamos los puntos 6 y 7
            x = -1
            yapprox = (approx[7][0][1] + approx[6][0][1]) / 2
            if (halfHeight + 5) < yapprox and (halfHeight - 5) < yapprox:
                y = -1
            elif (halfHeight + 5) > yapprox and (halfHeight - 5) > yapprox:
                y = 1
        else:   # Si la x de 0 vale 1 entramos aquí y comparamos los puntos 0 y 1
            x = 1
            yapprox = (approx[0][0][1] + approx[1][0][1]) / 2
            if (halfHeight + 5) < yapprox and (halfHeight - 5) < yapprox:
                y = -1
            elif (halfHeight + 5) > yapprox and (halfHeight - 5) > yapprox:
                print(yapprox)
                y = 1

    return x, y

def calculateDistance(square):
    z = None

    moments = cv2.moments(square)
    radius = int(np.sqrt(moments["mu20"] / moments["m00"]))
    distance = (target_distance * radius) / 25

    # A la target_distance le damos un +- 5 de error para alejarse o acercarse
    z = -1 if distance > target_distance + 5 else (1 if distance < target_distance - 5 else 0)
    return z

def showResults(x, y, z):
    movement = ""

    if x == None and y == None and z == None:
        movement = "No se ha encontrado ningún QR."
    elif (x == None or x == 0) and (y == None or y == 0) and z == -1:
        movement = "Retroceder."
    elif x == 0 or x == None and y == 0 or y == None and z == 0:
        movement = "OK. Quieto."
    else:
        movement = "Mover"
        if x == -1:
            movement += " a la izquierda"
        elif x == 1:
            movement += " a la derecha"

        if y != 0 and z != None:
            movement += ","
        elif y != 0 and z == None:
            movement += " y"

        if y == -1:
            movement += " abajo"
        elif y == 1:
            movement += " arriba"

        if z == -1:
            movement += " y retroceder"
        elif z == 1:
            movement += " y avanzar"

        movement += "."

    print(movement)
    return

def main():
    total_images = 18
    for i in range(1, total_images):
        image_path = "Practica_OpenCV/entrada" + str(i) + ".jpg"
        try:
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: No se pudo cargar la imagen {image_path}")
                continue

            searchRedSquare(image)

            cv2.imshow("Red Shapes", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()