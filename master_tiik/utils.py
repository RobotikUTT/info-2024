from math import sin, cos, asin, acos, sqrt, pi
from typing import Tuple, List

import numpy as np
from scipy.optimize import minimize


class Line:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __call__(self, x, y):
        return self.a * x + self.b * y + self.c

    def distance_to_point(self, x, y):
        return abs(self.a * x + self.b * x + self.c) / sqrt(self.a ** 2 + self.b ** 2)

    @staticmethod
    def from_points(x0, y0, x1, y1):
        a = y1 - y0
        b = x0 - x1
        c = -a * x0 - b * y0
        return Line(a, b, c)

    def intersection(self, other):
        det = self.a * other.b - other.a * self.b
        if det == 0:
            return None
        x = (self.b * other.c - other.b * self.c) / det
        y = (other.a * self.c - self.a * other.c) / det
        return x, y

    def __str__(self):
        return f"{self.a}x + {self.b}y + {self.c} = 0"

    def __repr__(self):
        return str(self)


class Circle:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def __call__(self, x, y):
        return (x - self.x) ** 2 + (y - self.y) ** 2 - self.r ** 2

    def intersects_with_line(self, line):
        return abs(line(self.x, self.y)) / sqrt(line.a ** 2 + line.b ** 2) < self.r - 0.0001

    def __str__(self):
        return f"(x - {self.x})² + (y - {self.y})² = {self.r}²"

    def __repr__(self):
        return str(self)

    def contains_point(self, x, y):
        return (x - self.x) ** 2 + (y - self.y) ** 2 < self.r ** 2 + 0.0001


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __abs__(self):
        return sqrt(self.x ** 2 + self.y ** 2)
        
    def __truediv__(self, other):
        return Point(self.x / other, self.y / other)
        
    def __mul__(self, other):
        return Point(self.x * other, self.y * other)


def find_path(a: Tuple[float, float], b: Tuple[float, float], circles_to_avoid: List[Circle]):
    from useful_class import Path
    if a[0] == b[0] and a[1] == b[1]:
        return Path([])
    line = Line.from_points(a[0], a[1], b[0], b[1])
    path1_from_a = path1_from_b = path2_from_a = path2_from_b = line
    done = False
    while not done:
        done = True
        for circle in circles_to_avoid:
            if circle.intersects_with_line(path1_from_a):
                path1_from_a = tangent_lines(circle, *a)[0]
                done = False
            if circle.intersects_with_line(path1_from_b):
                path1_from_b = tangent_lines(circle, *b)[1]
                done = False
            if circle.intersects_with_line(path2_from_a):
                path2_from_a = tangent_lines(circle, *a)[1]
                done = False
            if circle.intersects_with_line(path2_from_b):
                path2_from_b = tangent_lines(circle, *b)[0]
                done = False
    if path1_from_a == line:
        return Path([a, b])
    keypoint_for_path1 = path1_from_a.intersection(path1_from_b)
    keypoint_for_path2 = path2_from_a.intersection(path2_from_b)
    path1 = Path([a, keypoint_for_path1, b])
    path2 = Path([a, keypoint_for_path2, b])
    if path1.length < path2.length:
        return path1
    return path2


def tangent_lines(circle: Circle, x0, y0):
    x_c = circle.x
    y_c = circle.y
    r = circle.r
    d = sqrt((x_c - x0) ** 2 + (y_c - y0) ** 2)
    theta_0 = acos((x_c - x0) / d)
    if y_c < y0:
        theta_0 = 2 * pi - theta_0
    theta = asin(r / d)
    x1 = d * cos(theta_0 + theta) + x0
    y1 = d * sin(theta_0 + theta) + y0
    x2 = d * cos(theta_0 - theta) + x0
    y2 = d * sin(theta_0 - theta) + y0
    return Line.from_points(x0, y0, x1, y1), Line.from_points(x0, y0, x2, y2)


# From ChatGPT

def fit_circle_to_points(points):
    """
    Fit a circle to a set of points using least squares circle fitting.
    """
    def dist_point_to_circle(point, center, radius):
        """
        Calculate the distance between a point and a circle's boundary (distance between point and center minus the radius).
        """
        return np.abs(np.linalg.norm(point - center) - radius)

    def objective_function(params, points):
        """
        Objective function for least squares circle fitting.
        """
        center = params[:2]
        radius = params[2]
        distances = np.array([dist_point_to_circle(point, center, radius) for point in points])
        return np.sum(distances ** 2)
    # Initial guess for the center and radius
    initial_guess = np.mean(points, axis=0).tolist() + [np.max(np.linalg.norm(points - np.mean(points, axis=0)))]

    # Minimize the objective function
    result = minimize(objective_function, initial_guess, args=(points,), method='Nelder-Mead')

    # Extract the optimized parameters
    return Circle(*result.x)


def mean(*values):
    if len(values) == 1:
        values = list(values[0])
        return sum(values) / len(values)
    return sum(values) / len(values)


if __name__ == '__main__':
    print(find_path((0, 0), (10, 10), [Circle(5, 5, 5), Circle(6, -2, 2.1)]))
