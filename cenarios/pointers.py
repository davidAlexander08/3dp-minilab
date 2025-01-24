import pandas as pd
import numpy as np
from scipy.linalg import solve
import random
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from scipy.stats import mstats

import math

class Point:
    def __init__(self, dimen=5, numero_clusters = 3):
        # Initialize coordinates with a given dimension (default 5)
        if dimen < 1:
            dimen = 2  # Default to 2 dimensions if less than 1
        self.coord = [0.0] * dimen  # Initialize coordinates to zeros
        self.weightCentroids = [0.0]*numero_clusters

    def dist(self, other):
        sum = 0
        for i in range(len(self.coord)):
            sum += (self.coord[i] - other.coord[i]) ** 2
        return math.sqrt(sum)


    def __mul__(self, m1):
        # Define scalar multiplication for a Point
        prod_point = Point(len(self.coord))
        for i in range(len(self.coord)):
            prod_point.coord[i] = m1 * self.coord[i]
        return prod_point

    def __repr__(self):
        # Define string representation of the Point
        return f"({', '.join(map(str, self.coord))})"