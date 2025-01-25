import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans

# Assuming 'X' is your data (e.g., a 2D array or DataFrame with your data points)
# X = ...
X, y = make_blobs(n_samples=300, centers=3, cluster_std=0.60, random_state=42)

# Plot the dataset to visualize the clusters
plt.figure(figsize=(8, 6))
plt.scatter(X[:, 0], X[:, 1], c='blue', marker='o', edgecolors='k')
plt.title("Generated Dataset with 3 Clusters")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.savefig('data.png', format='png')



# Parameters for random normal data
mean = 0
std_dev = 1
size = 300  # Number of samples (data points)

# Generate a 2D random normal vector (size=300, 1 feature)
X = np.random.normal(loc=mean, scale=std_dev, size=(size, 1))

# List to store the inertia values for each k
inertia = []

# Try a range of k values (from 1 to 10)
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    inertia.append(kmeans.inertia_)

# Plotting the Elbow graph
plt.figure(figsize=(8, 6))
plt.plot(range(1, 11), inertia, marker='o')
plt.title('Elbow Method For Optimal k')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.savefig('elbow_method.png', format='png')
