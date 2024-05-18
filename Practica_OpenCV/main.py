import cv2
import numpy as np

TARGET_DISTANCE = 30

def searchRedSquare(image):
    """
    Search for a red square in the given image and determine movements based on its presence and position.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        None
    """
    x = y = z = None
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        if existQR(image):
            z = -1
    else:
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

            if len(approx) == 4:  # Square or rectangle
                x, y, z = handleQuadrilateral(image, approx, cnt)
            elif len(approx) in [6, 8]:  # Cut shapes
                x, y = position(image, approx)
                z = None  # Distance calculation is not provided for cut shapes

    showResults(x, y, z)

def existQR(image):
    """
    Check if a QR code exists in the given image.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        bool: True if a QR code is found, False otherwise.
    """
    return len(searchContoursQR(image)) > 0

def handleQuadrilateral(image, approx, cnt):
    """
    Handle the case when a quadrilateral shape (either a square or a rectangle) is detected.

    Args:
        image (numpy.ndarray): The input image.
        approx (numpy.ndarray): The approximation of the contour.
        cnt (numpy.ndarray): The contour.

    Returns:
        Tuple[int, int, int]: The x, y, and z coordinates indicating the movement direction.
    """
    x, y, z = None, None, None
    x, y, w, h = cv2.boundingRect(cnt)
    ratio = float(w) / h
    if 0.9 <= ratio <= 1.1:  # Square
        x, y = position(image, approx)
        if existQR(image):
            z = calculateDistance(approx)
    else:  # Rectangle
        orientation = 1 if w > h else 0 # Horizontal = 1 | Vertical = 0
        if existQR(image):
            x, y = searchQRPosition(image, orientation)
            z = -1
        else:
            x, y = position(image, approx)

    return x, y, z

def searchQRPosition(image, orientation):
    """
    Search for the position of a QR code relative to the given orientation.

    Args:
        image (numpy.ndarray): The input image.
        orientation (int): The orientation of the QR code (0 for vertical, 1 for horizontal).

    Returns:
        Tuple[int, int]: The x and y coordinates indicating the movement direction.
    """
    height, width, _ = image.shape
    contours = searchContoursQR(image)
    areas = [0, 0, 0, 0]  # left, right, top, bottom

    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        if x + w < width / 2:
            areas[0] += area
        elif x > width / 2:
            areas[1] += area
        if y + h < height / 2:
            areas[2] += area
        elif y > height / 2:
            areas[3] += area

    if orientation == 0:  # Vertical
        return (-1 if areas[0] > areas[1] else 1), None
    else:  # Horizontal
        return None, (-1 if areas[3] > areas[2] else 1)

def searchContoursQR(image):
    """
    Search for contours of QR codes in the image.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        List[numpy.ndarray]: List of contours of QR codes.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])
    mask = cv2.inRange(hsv, lower_black, upper_black)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def position(image, approx):
    """
    Determine the position based on the type of contour.

    Args:
        image (numpy.ndarray): The input image.
        approx (numpy.ndarray): The approximated contour.

    Returns:
        Tuple[int, int]: x and y position.
    """
    height, width, _ = image.shape
    half_height, half_width = height / 2, width / 2
    x = y = 0

    if len(approx) == 4:  # Square
        x, y = getSquarePosition(approx, half_width, half_height)
    elif len(approx) == 6:  # Cut corner
        x, y = getCutCornerPosition(approx, width, height)
    elif len(approx) == 8:  # Cut side
        x, y = getCutSidePosition(approx, half_height)

    return x, y

def getSquarePosition(approx, half_width, half_height):
    """
    Calculate the position for a square shape.

    Args:
        approx (numpy.ndarray): The approximated contour.
        half_width (float): Half of the width of the image.
        half_height (float): Half of the height of the image.

    Returns:
        Tuple[int, int]: x and y position.
    """
    x_approx = (approx[0][0][0] + approx[2][0][0]) / 2
    y_approx = (approx[0][0][1] + approx[1][0][1]) / 2
    x = -1 if x_approx < half_width - 5 else (1 if x_approx > half_width + 5 else 0)
    y = -1 if y_approx < half_height - 5 else (1 if y_approx > half_height + 5 else 0)
    return x, y

def getCutCornerPosition(approx, width, height):
    """
    Calculate the position for a corner cut shape.

    Args:
        approx (numpy.ndarray): The approximated contour.
        width (int): Width of the image.
        height (int): Height of the image.

    Returns:
        Tuple[int, int]: x and y position.
    """
    firstX, firstY = approx[0][0]
    secondX, secondY = approx[3][0]
    if firstY == 0 and secondX == 0:
        return -1, 1
    elif firstY == 0 and secondX == width - 1:
        return 1, 1
    elif firstX == 0 and secondY == height - 1:
        return -1, -1
    elif firstX == width - 1 and secondY == height - 1:
        return 1, -1
    return 0, 0

def getCutSidePosition(approx, half_height):
    """
    Calculate the position for a side cut shape.

    Args:
        approx (numpy.ndarray): The approximated contour.
        half_height (float): Half of the image height.

    Returns:
        Tuple[int, int]: x and y position.
    """
    move = approx[0][0][0]
    if move == 0:
        y_approx = (approx[7][0][1] + approx[6][0][1]) / 2
        y = -1 if y_approx < half_height - 5 else (1 if y_approx > half_height + 5 else 0)
        return -1, y
    else:
        y_approx = (approx[0][0][1] + approx[1][0][1]) / 2
        y = -1 if y_approx < half_height - 5 else (1 if y_approx > half_height + 5 else 0)
        return 1, y

def calculateDistance(square):
    """
    Calculate the distance based on the size of a square.

    Args:
        square (numpy.ndarray): The contour representing the square.

    Returns:
        int: Distance evaluation (-1 if too far, 0 if within acceptable range, 1 if too close).
    """
    moments = cv2.moments(square)
    radius = int(np.sqrt(moments["mu20"] / moments["m00"]))
    distance = (TARGET_DISTANCE * radius) / 25
    return -1 if distance > TARGET_DISTANCE + 5 else (1 if distance < TARGET_DISTANCE - 5 else 0)

def showResults(x, y, z):
    """
    Display the movement instructions based on the detected features.

    Args:
        x (int or None): Movement in the x-axis (-1 for left, 0 for no movement, 1 for right).
        y (int or None): Movement in the y-axis (-1 for down, 0 for no movement, 1 for up).
        z (int or None): Movement in the z-axis (-1 for backward, 0 for no movement, 1 for forward).
    """
    if x is None and y is None and z is None:
        movement = "No se ha encontrado ningún QR."
    elif (x in [None, 0]) and (y in [None, 0]) and z == -1:
        movement = "Retroceder."
    elif (x in [None, 0]) and (y in [None, 0]) and z == 0:
        movement = "OK. Quieto."
    else:
        movement = "Mover"
        if x == -1:
            movement += " a la izquierda"
        elif x == 1:
            movement += " a la derecha"

        if x not in [None, 0] and y not in [None, 0] and z not in [None, 0]:
            movement += ","
        elif y != 0 and z is None:
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

def main():
    """
    Main function to process a set of images, detect red squares, and display results.
    """
    total_images = 18
    for i in range(1, total_images):
        image_path = f"Practica_OpenCV/data/entrada{i}.jpg"
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: No se pudo cargar la imagen {image_path}")
            continue

        try:
            searchRedSquare(image)
            cv2.imshow("Red Shapes", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()