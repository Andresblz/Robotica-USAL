import tkinter as tk
import math
import random

class Robot:
    def __init__(self, dimensions, wheel_spacing, wheel_diameter, encoder_resolution, canvas_width, canvas_height):
        """
        Initialize the robot.

        Args:
            dimensions (tuple): The dimensions (width, height) of the robot.
            wheel_spacing (float): The distance between the wheels.
            wheel_diameter (float): The diameter of the wheels.
            encoder_resolution (int): The resolution of the encoders.
            canvas_width (int): Width of the canvas.
            canvas_height (int): Height of the canvas.

        Returns:
            None
        """
        self.x = canvas_width / 2
        self.y = canvas_height / 2
        self.theta = 0  # Orientation in radians
        self.dimensions = dimensions
        self.wheel_spacing = wheel_spacing
        self.wheel_diameter = wheel_diameter
        self.encoder_resolution = encoder_resolution
        self.previous_positions = [(self.x, self.y)]
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def move_forward(self, distance_left, distance_right):
        """
        Move the robot forward based on the distances traveled by the left and right wheels.

        Args:
            distance_left (float): Distance traveled by the left wheel.
            distance_right (float): Distance traveled by the right wheel.

        Returns:
            None
        """
        # Simulate non-systematic errors
        if random.random() < 0.1:
            distance_left *= random.uniform(0.9, 1.0)
            distance_right *= random.uniform(0.9, 1.0)

        # Calculate displacement for each wheel
        left_distance = (distance_left / self.encoder_resolution) * self.wheel_diameter * math.pi
        right_distance = (distance_right / self.encoder_resolution) * self.wheel_diameter * math.pi

        # Calculate forward kinematics
        distance = (left_distance + right_distance) / 2
        delta_theta = (right_distance - left_distance) / self.wheel_spacing
        self.theta += delta_theta
        delta_x = distance * math.cos(self.theta)
        delta_y = distance * math.sin(self.theta)

        # Update position if within canvas boundaries
        new_x = self.x + delta_x
        new_y = self.y + delta_y
        if 0 <= new_x < self.canvas_width and 0 <= new_y < self.canvas_height:
            self.x = new_x
            self.y = new_y
            self.previous_positions.append((self.x, self.y))

class Application(tk.Tk):
    def __init__(self):
        """
        Initialize the application and create the GUI.

        Args:
            None

        Returns:
            None
        """
        super().__init__()
        self.title("Tarea Odometría")
        canvas_width = 400
        canvas_height = 400
        self.robot = Robot(dimensions=(100, 50), wheel_spacing=20, wheel_diameter=10, encoder_resolution=100,
                                       canvas_width=canvas_width, canvas_height=canvas_height)
        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        self.canvas.pack()
        self.bind('<KeyPress>', self.key_pressed)
        self.draw_robot()

    def key_pressed(self, event):
        """
        Event handler for key press events.

        Args:
            event (tk.Event): The key press event.

        Returns:
            None
        """
        key = event.char
        if key == 'i':
            self.robot.move_forward(10, 10)
        elif key == 'k':
            self.robot.move_forward(-10, -10)
        elif key == 'j':
            self.robot.move_forward(-10, 10)
        elif key == 'l':
            self.robot.move_forward(10, -10)
        elif key == 'u':
            self.robot.move_forward(10, 3)
        elif key == 'o':
            self.robot.move_forward(3, 10)
        self.draw_robot()

    def draw_robot(self):
        """
        Draw the robot on the canvas.

        Args:
            None

        Returns:
            None
        """
        self.canvas.delete('robot')
        x, y = self.robot.x, self.robot.y
        theta = self.robot.theta
        # Draw trail
        for i in range(len(self.robot.previous_positions) - 1):
            x1, y1 = self.robot.previous_positions[i]
            x2, y2 = self.robot.previous_positions[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill='gray', tag='robot')
        # Draw robot body
        self.canvas.create_rectangle(x - 20, y - 10, x + 20, y + 10, fill='red', tag='robot')
        # Draw orientation
        x_orientation = x + 15 * math.cos(theta)
        y_orientation = y + 15 * math.sin(theta)
        self.canvas.create_line(x, y, x_orientation, y_orientation, fill='white', arrow=tk.LAST, tag='robot')

if __name__ == '__main__':
    app = Application()
    app.mainloop()