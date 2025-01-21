import pandas as pd
import numpy as np
from scipy.linalg import solve
import random
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from scipy.stats import mstats
from pointers import Point

class KmeansGevazp:
    def __init__(self,numero_clusters, matrizRuidos):
        self.numero_clusters = numero_clusters
        self.matrizRuidos = matrizRuidos
        self.matrizRuidos = np.array([[0.696051, -0.0484017, 0.478469, -0.0435582, 0.735658, 1.07746], [-0.27065,0.105135,-0.88329, 1.57596,-0.279789, -0.380387   ]])
        self.kmeans_gevazp()

    def kmeans_gevazp(self):
        ##Metodo GEVAZP
        if self.numero_clusters == 1:
            matrizRuidosAgregados = np.zeros((self.numero_clusters, self.matrizRuidos.shape[1]))
            matrizRuidosAgregados[0, :] = matrizRuidos[0, :]
            probablidadesClustersVector = [1.0]
        numeroRuidos = self.matrizRuidos.shape[1]  # Number of rows in matrizRuidos
        k = self.numero_clusters  # Default number of centroids
        m = 1.001  # Fuzzifier
        iterations = 20  # Max number of iterations
        dataCount = 0  # Number of points divided by dimension
        numberCount = 0  # Total numbers read
        probabilidade = [0] * k
        matrizRuidosAgregados = np.zeros((self.numero_clusters, self.matrizRuidos.shape[1]))
        #X = np.zeros((self.numero_clusters, self.matrizRuidos.shape[1]))
        # Initialize probabilities vector
        probablidadesClustersVector = []
        maxOnDim = [0.0] * self.matrizRuidos.shape[0]
        minOnDim = [9.99e+20] * self.matrizRuidos.shape[0]
        self.centroid = []
        self.oldCentroid = []
        
        dataCount = 0
        newItem = 0
        items = []
        #Point(dimensions)
        # Iterate through matrizRuidos
        for i in range(self.matrizRuidos.shape[1]):  # Iterate over rows
            item = Point(self.matrizRuidos.shape[0])
            item.coord = self.matrizRuidos[:,i]
            items.append(item)
            print(item.coord)

        for dim in range(0,self.matrizRuidos.shape[0]):
            print("dim: ", dim)
            maxOnDim[dim] = max(self.matrizRuidos[dim,:])
            minOnDim[dim] = min(self.matrizRuidos[dim,:])
            data_inic_old = Point(self.matrizRuidos.shape[0])
            data_inic_old.coord = [0.0]*self.matrizRuidos.shape[0]
            self.oldCentroid.append(data_inic_old)

        print("items: ", items)
        print("maxOnDim: ", maxOnDim)
        print("minOnDim: ", minOnDim)

        flagClusterVazio = 1
        while flagClusterVazio == 1:
            for i in range(k):
                random_row = self.random_index(0, numeroRuidos - 1)
                data = Point(self.matrizRuidos.shape[0])
                data.coord = self.matrizRuidos[:, random_row]
                self.centroidcentroid.append(data)
                print(self.centroidcentroid)
            data1 = Point(self.matrizRuidos.shape[0])
            data1.coord = [-0.0484017, -0.279789]
            self.centroidcentroid[0] = data1
            data2 = Point(self.matrizRuidos.shape[0])
            data2.coord = [0.478469, -0.380387]
            self.centroidcentroid[1] = data2
            data3 = Point(self.matrizRuidos.shape[0])
            data3.coord = [-0.0484017, 1.57596]
            self.centroidcentroid[2] = data3
            print(self.centroidcentroid)
            ##CALCULA WEIGHTS
            self.calculate_weights(m, numeroRuidos, k)
            ### FIM CALCULATE WEIGHTS
            exit(1)
            for i in range(dataCount):
                for j in range(k):
                    if round(items[i]["weightCentroids"][j]) == 1.0:
                        probabilidade[j] += 1

            # Check if there are empty clusters
            flagClusterVazio = 0
            for j in range(k):
                if probabilidade[j] == 0:
                    flagClusterVazio = 1


        # Main loop for running iterations
        for i in range(iterations):
            # Logging iterations
            print(f"Iteration {i + 1} of {iterations}")

            # Calculate new centroids
            if calculate_new_centroids(m, dataCount, k, self.matrizRuidos.shape[0]):
                # Exit if the function signals completion
                break

            # Calculate weights
            calculate_weights(m, dataCount, k)
        # Iterate centroids (k = number of centroids)
        for j in range(k):
            menorDistancia = 99999.9
            for i in range(dataCount):
                # Iterate all centroids
                if np.round(items[i]["weightCentroids"][j]) == 1.0:
                    sumW = items[i]["point"].dist(self.centroidcentroid[j])  # Calculate distance
                    if sumW < menorDistancia:
                        # Update matrizRuidosAgregados with the values of the closest point
                        for ii in range(self.matrizRuidos.shape[1]):
                            matrizRuidosAgregados[j, ii] = self.matrizRuidos[i, ii]
                        menorDistancia = sumW
        for i in range(numeroClusters):
            # Add the normalized probability for the current cluster
            probablidadesClustersVector.append(probabilidade[i] / numeroRuidos)
        

        dpMedioGerado = 0
        for i in range(matrizRuidosAgregados.shape[1]):
            # Initialize accumulator
            if probablidadesClustersVector[i] > 0:
                weighted_values = []
                weights = []

                # Collect the weighted values for column i
                for j in range(matrizRuidosAgregados.shape[0]):
                    weighted_values.append(matrizRuidosAgregados[j, i])
                    weights.append(probablidadesClustersVector[j])

                # Calculate weighted variance
                weighted_variance = mstats.tstd(weighted_values, weights=weights)**2

                # Update dpMedioGerado
                dpMedioGerado += 1.0 / np.sqrt(weighted_variance)

        # Average dpMedioGerado across all dimensions
        dpMedioGerado /= float(matrizRuidosAgregados.shape[1])

        # Correct standard deviation for aggregated noise
        self.matrizRuidosAgregados *= dpMedioGerado


    def random_index(self, lower, upper):
        """Generate a random integer between lower and upper (inclusive)."""
        return np.random.randint(lower, upper + 1)


    def calculate_new_centroids(self, m, numeroRuidos, k, dimensions):

        # Iterate centroids (k = number of centroids)
        for i in range(k):
            self.oldCentroid[i].coord = self.centroid[i].coord
            ################PAREI AQUI PARA CONTINUAR O CALCULO DOS CENTROIDES
            exit(1)
            pSum = Point([0.0] * self.matrizRuidos.shape[0])  # Initialize pSum
            count = 0.0
            for j in range(numeroRuidos):
                # Sum the weighted vector of item j to centroid i
                weight = items[j]["weightCentroids"][i] ** m
                pW = items[j]["point"] * weight  # Weighted vector
                pSum = pSum + pW
                count += weight

            # Calculate new coordinates of centroid i
            if count > 0:
                centroid[i] = pSum / count

            # Calculate movement of the centroid
            movement = centroid[i].dist(self.oldCentroid[i])

            # Uncomment these for debugging
            # print(f"New Centroid {i}: {centroid[i].coord}")
            # print(f"Centroid moved: {movement}")
        return 0

    def calculate_weights(self, m,dataCount,k):
        sumW = 0.0  # Sum of weights
        menorDistancia = float('inf') 
        clusterMaisProximo = 0 
        for i in range(dataCount):
            menorDistancia = float('inf')  # Reset for each point
            clusterMaisProximo = 0  # Reset for each point

            # Iterate over all centroids to find the closest one
            for j in range(k):
                # Calculate distance between point `i` and centroid `j`
                sumW = np.linalg.norm(np.array(items[i]["coord"]) - np.array(centroid[j]["coord"]))
                
                # Update the closest cluster if the distance is smaller
                if sumW < menorDistancia:
                    clusterMaisProximo = j
                    menorDistancia = sumW

            # Assign weight of 1.0 to the closest centroid and 0.0 to others
            for j in range(k):
                items[i]["weightCentroids"][j] = 1.0 if j == clusterMaisProximo else 0.0
