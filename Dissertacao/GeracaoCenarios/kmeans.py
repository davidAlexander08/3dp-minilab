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
            matrizRuidosAgregados[0, :] = self.matrizRuidos[0, :]
            probablidadesClustersVector = [1.0]
        numeroRuidos = self.matrizRuidos.shape[1]  # Number of rows in matrizRuidos
        
        m = 1.001  # Fuzzifier
        iterations = 20  # Max number of iterations
        dataCount = 0  # Number of points divided by dimension
        numberCount = 0  # Total numbers read
        probabilidade = [0] * self.numero_clusters
        matrizRuidosAgregados = np.zeros((self.numero_clusters, self.matrizRuidos.shape[0]))
        #X = np.zeros((self.numero_clusters, self.matrizRuidos.shape[1]))
        # Initialize probabilities vector
        probablidadesClustersVector = []
        maxOnDim = [] 
        minOnDim = [] 
        self.centroid = []
        
        
        dataCount = 0
        newItem = 0
        self.items = []
        #Point(dimensions)
        # Iterate through matrizRuidos
        for i in range(self.matrizRuidos.shape[1]):  # Iterate over rows
            item = Point(self.matrizRuidos.shape[0], self.numero_clusters)
            item.coord = self.matrizRuidos[:,i]
            self.items.append(item)
            print(item.coord)

        for dim in range(0,self.matrizRuidos.shape[0]):
            maxOnDim.append(max(self.matrizRuidos[dim,:]))
            minOnDim.append(min(self.matrizRuidos[dim,:]))

        print("items: ", self.items)
        print("maxOnDim: ", maxOnDim)
        print("minOnDim: ", minOnDim)
        self.centroidcentroid = []
        flagClusterVazio = 1
        while flagClusterVazio == 1:
            for i in range(self.numero_clusters):
                random_row = self.random_index(0, numeroRuidos - 1)
                data = Point(self.matrizRuidos.shape[0], self.numero_clusters)
                data.coord = self.matrizRuidos[:, random_row]
                self.centroidcentroid.append(data)
                #print(self.centroidcentroid)
            data1 = Point(self.matrizRuidos.shape[0])
            data1.coord = [-0.0484017, -0.279789]
            self.centroidcentroid[0] = data1
            data2 = Point(self.matrizRuidos.shape[0], self.numero_clusters)
            data2.coord = [0.478469, -0.380387]
            self.centroidcentroid[1] = data2
            data3 = Point(self.matrizRuidos.shape[0], self.numero_clusters)
            data3.coord = [-0.0484017, 1.57596]
            self.centroidcentroid[2] = data3
            print(self.centroidcentroid)
            self.mapa_centroid = {
                data1:0,
                data2:1,
                data3:2
            }

            ##CALCULA WEIGHTS
            self.calculate_weights(m, numeroRuidos, self.numero_clusters)
            ### FIM CALCULATE WEIGHTS
            
            for i in range(numeroRuidos):
                for j in range(self.numero_clusters):
                    if round(self.items[i].weightCentroids[j]) == 1.0:
                        probabilidade[j] += 1

            # Check if there are empty clusters
            flagClusterVazio = 0
            for j in range(self.numero_clusters):
                if probabilidade[j] == 0:
                    flagClusterVazio = 1


        # Main loop for running iterations
        for i in range(iterations):
            # Logging iterations
            print(f"Iteration {i + 1} of {iterations}")
            self.calculate_new_centroids(m, numeroRuidos, self.numero_clusters, self.matrizRuidos.shape[0])
            self.calculate_weights(m, numeroRuidos, self.numero_clusters)


        print(self.matrizRuidos)
        print(matrizRuidosAgregados)
        # Iterate centroids (k = number of centroids)
        for j in range(self.numero_clusters):
            menorDistancia = 99999.9
            for i in range(numeroRuidos):
                # Iterate all centroids
                if np.round(self.items[i].weightCentroids[j]) == 1.0:
                    sumW = self.items[i].dist(self.centroidcentroid[j])  # Calculate distance
                    if sumW < menorDistancia:
                        for ii in range(self.matrizRuidos.shape[0]):
                            print("j: ", j, " i: ", i , " ii: ", ii)
                            matrizRuidosAgregados[j, ii] = self.matrizRuidos[ii, i]
                        menorDistancia = sumW
        print(matrizRuidosAgregados)
        for i in range(numeroClusters):
            # Add the normalized probability for the current cluster
            probablidadesClustersVector.append(probabilidade[i] / numeroRuidos)
        
        print(matrizRuidosAgregados)
        print(probablidadesClustersVector)
        exit(1)

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


    def calculate_new_centroids(self, m, numeroRuidos, numero_clusters, dimensions):
        self.oldCentroid = []
        for dim in range(0,numero_clusters):
            old_centroid = Point(self.matrizRuidos.shape[0], self.numero_clusters)
            self.oldCentroid.append(old_centroid)
        for i in range(self.numero_clusters):
            self.oldCentroid[i].coord = self.centroidcentroid[i].coord
            pSum = Point(numeroRuidos, self.numero_clusters)  # Initialize pSum
            count = 0.0
            for j in range(0, numeroRuidos):
                valor = (self.items[j].weightCentroids[i]**m)
                for kk in range(0,dimensions):
                    pSum.coord[kk] += valor*self.items[j].coord[kk]
                count += valor
                print("count: " , count )
            # Calculate new coordinates of centroid i
            if count > 0:
                for kk in range(0,dimensions):
                    self.centroidcentroid[i].coord[kk] += (1.0/count)*pSum.coord[kk]

            # Calculate movement of the centroid
            movement = self.centroidcentroid[i].dist(self.oldCentroid[i])
            print(" movement: ", movement)
        return 0

    def calculate_weights(self, m,numeroRuidos,numero_clusters):
        sumW = 0.0  # Sum of weights
        menorDistancia = float('inf') 
        clusterMaisProximo = 0 
        
        for item in self.items:
            menorDistancia = float('inf')  # Reset for each point
            clusterMaisProximo = 0  # Reset for each point
            for centroid in self.centroidcentroid:
                dist = item.dist(centroid)
                
                #print("centroid: ", centroid.coord, " ponto: ", item.coord, " dist: ", dist)
                if dist < menorDistancia:
                    clusterMaisProximo = centroid
                    menorDistancia = dist
                    #print("clusterMaisProximo: ", centroid.coord, " ponto: ", item.coord, " menorDistancia: ", dist)
                
            # Assign weight of 1.0 to the closest centroid and 0.0 to others
            for centroid in self.centroidcentroid:
                if(centroid == clusterMaisProximo):
                    item.weightCentroids[self.mapa_centroid[centroid]] = 1.0
                    #print("clusterMaisProximo: ", centroid.coord, " ponto: ", item.coord, " weight: ", item.weightCentroids)

                    #self.items[i]["weightCentroids"][j] = 1.0 if j == clusterMaisProximo else 0.0
