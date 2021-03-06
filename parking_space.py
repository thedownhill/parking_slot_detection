import numpy as np
import descartes
import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString
from copy import deepcopy

height = 56.7
width = 23.25
space_bw_cars_ratio = 2


def point_in_rectangle(point, rectangle):
    AB = (rectangle[0], rectangle[1])
    BC = (rectangle[1], rectangle[2])
    AM = (rectangle[0], point)
    BM = (rectangle[1], point)
    dotABAM = np.dot(AB, AM)
    dotABAB = np.dot(AB, AB)
    dotBCBM = np.dot(BC, BM)
    dotBCBC = np.dot(BC, BC)
    return 0 <= dotABAM <= dotABAB and 0 <= dotBCBM <= dotBCBC


def vector_in_polygon(vector, polygon, draw=False):
    vector = LineString(vector)
    polygon = Polygon(polygon)

    # Drawing function
    if draw:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(*np.array(vector).T, color='blue', linewidth=3, solid_capstyle='round')
        ax.add_patch(descartes.PolygonPatch(polygon, fc='blue', alpha=0.5))
        ax.axis('equal')
        plt.show()

    return vector.intersects(polygon)


def vector_intersection(vector, cars, draw=False):
    """
    :param vector: [point_begin, point_end]
    :param cars: [[[x0, y0], .., [x4, y4]], ...]
    :return:  True/Flase, Car coords
        - If True: coords of parking space
        - If False: coords of car that is in the way
    """
    left_vector = deepcopy(vector)  # left right points - for the corners of the car
    right_vector = deepcopy(vector)
    left_vector[1][0] -= width  # / 2
    right_vector[1][0] += width  # / 2

    for car in cars:
        if vector_in_polygon(vector, car.copy(), draw):
            return False, car
        if vector_in_polygon(left_vector, car.copy(), draw):
            return False, car
        if vector_in_polygon(right_vector, car.copy(), draw):
            return False, car

    # Calculating place for parking
    y_middle = (vector[1][1] + vector[0][1]) / 2
    x_middle = (vector[1][0] + vector[0][0]) / 2
    tl = [x_middle - width / 2, y_middle + height / 2]
    tr = [x_middle + width / 2, y_middle + height / 2]
    bl = [x_middle - width / 2, y_middle - height / 2]
    br = [x_middle + width / 2, y_middle - height / 2]

    return True, np.array([tl, tr, br, bl, tl])


def find_parking_space(cars, shape):
    # since we park only on the right hand side (in city)
    # we search for a car that is closest to us and on the right side
    shifted_cars = list()
    free_slots = list()
    for car in cars:
        car[:, 0] -= shape // 2
        if all([x > 0 for x in car[:, 0]]):
            shifted_cars.append(car)
    min_y = 10000
    start_car = None
    for shifted_car in shifted_cars:
        shifted_car = np.array(shifted_car)
        if shifted_car[:, 1].min() < min_y:
            min_y = shifted_car[:, 1].max()
            start_car = shifted_car

    while True:
        y = start_car[:, 1].max()
        if y + height * 1.5 > shape:
            break
        x = start_car[:-1, 0].sum() / 4
        vector = [[x, y], [x, y + height * space_bw_cars_ratio]]
        is_slot_free, start_car = vector_intersection(vector, [x for x in shifted_cars if not np.array_equal(x, start_car)], draw=False)
        if is_slot_free:
            start_car[:, 0] += shape // 2
            free_slots.append(start_car)
            if len(free_slots) == 2:
                break
    return free_slots


if __name__ == '__main__':
    rec = [[[0, 0],
           [0, 2],
           [1, 2],
           [1, 0],
           [0, 0]],

           [[1, 5],
            [0, 5],
            [0, 7],
            [1, 7],
            [1, 5]]]

    vector = [[0.5, 2.1], [0.5, 4]]
    print(rec[0])
    # print(vector_in_polygon(vector, rec[0]))
    print(vector_intersection(vector, rec, width=1, height=2))
