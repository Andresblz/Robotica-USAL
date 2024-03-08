import cv2
import numpy as np

total_images = 7
target_distance = 30  
angulo_tolerancia = 10

def searchRedSquare(image):
    """
    Function to search for red shapes in an image, clasify and draw contours around them.

    Parameters:
    image : A NumPy array representing the image.
        Input image in BGR color format.

    Returns: 
    """

    # Convert the image from BGR color space to HSV (Hue, Saturation, Value) / HSB (Hue, Saturation, Brightness) color space
    # ---
    # HSV color model is often used in computer vision and image processing 
    # tasks because it separates the color information from the brightness 
    # information, making it easier to work with color-based segmentation and 
    # analysis. (https://docs.opencv.org/4.x/frame.jpg)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper bounds for red color in HSV
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])

    # Create a mask to filter out red regions in the image
    mask = cv2.inRange(hsv, lower_red, upper_red)

    # Find contours in the mask image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if contours were found
    if len(contours) == 0: # No contours
        result = searchQR(image)

        if result is None:
            showResults(None, None, None)
        else:
            showResults(None, None, -1)
    else:
        # Iterate through each contour found in the image
        for cnt in contours:
            # Calculate the area of the contour
            area = cv2.contourArea(cnt)

            # Approximate the contour to a simpler polygon with fewer vertices
            approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)

            # Check if the contour is a quadrilateral (4 vertices) and its area is above a threshold
            if len(approx) == 4 and area > 1000:
                # Get the bounding rectangle of the contour
                x, y, w, h = cv2.boundingRect(cnt)

                # Calculate the aspect ratio of the bounding rectangle
                ratio = float(w) / h

                # Check if the aspect ratio indicates a square
                if ratio >= 0.9 and ratio <= 1.1:
                    # Square
                    # Comprobar si hay más información además del rojo
                    #   Si hay más información el cuadrado está completo
                    #   Si no hay más información está cortado en una de las esquinas 
                    #   (localizar que esquina y hacer el desplazamiento hacia arriba/abajo izquierda/derecha)
                    # Draw contours around the detected square in green color
                    cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)

                    square = approx
                    shape = "square"

                    return square, shape
                else:
                    # Rectangle
                    # Draw contours around the detected rectangle in red color
                    cv2.drawContours(image, [approx], 0, (0, 255, 0), 3)

            elif len(approx) == 6:
                # Cortado en una esquina
                print("Esto cortado en una esquina")
            elif len(approx) == 8:
                # Cortado en un lateral
                print("Estoy cortado")

    return

def searchQR(image):

    return

def calculateDistanceAndOrientation(image, square):
    """
    Calculates the distance and orientation of a square relative to the center of an image.

    Args:
        image: A NumPy array representing the image.
        square: A NumPy array representing the contour of a square found in the image.

    Returns:
        A tuple containing two elements:
            - distance (float): The calculated distance of the square's center from the image center.
            - angle (float): The calculated orientation of the square in degrees, with 0 degrees 
                             pointing to the right and increasing counter-clockwise.
    """

    # Calculate moments of the square contour
    moments = cv2.moments(square)

    # Calculate the centroid (center) of the square based on moments
    centro_x = int(moments["m10"] / moments["m00"])
    centro_y = int(moments["m01"] / moments["m00"])

    # Calculate the radius of the circle that can be inscribed inside the square
    radius = int(np.sqrt(moments["mu20"] / moments["m00"]))

    # Calculate the distance of the square's center from the image center
    # Use a target distance and scale it based on the inscribed circle radius
    distance = (target_distance * radius) / 25

    # Calculate the orientation of the square relative to the image center
    # Use arctangent2 to handle both positive and negative coordinates
    angle = np.arctan2(centro_y - image.shape[0] / 2, centro_x - image.shape[1] / 2)
    # Convert the angle from radians to degrees
    angle = np.rad2deg(angle)

    return distance, angle


def showResults(x, y, z):
    movement = ""

    if x is None and y is None and z is None:
        movement = "No QR found on the image."
    elif x is None and y is None and z is -1:
        movement = "Retroceder."
    else:
        # Movimiento en x
        if x is -1:
            movement = "Mover a la izquierda"
        # Avanzar / Retroceder

        # Izquierda / Derecha y/o Arriba / Abajo


    print(movement)
    return

def main():
    for i in range(1, total_images, 1):
        image_path = "Practica_OpenCV/entrada" + str(i) + ".jpg"
        image = cv2.imread(image_path)

        searchRedSquare(image)

        cv2.imshow("Red Shapes", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()