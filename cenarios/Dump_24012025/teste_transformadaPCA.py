from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sample wine data (just for illustration)
data = pd.DataFrame({
    'Alcohol': [13.2, 14.3, 12.8, 13.5],
    'Malic_acid': [1.5, 2.0, 1.8, 1.3],
    'Ash': [2.5, 2.6, 2.4, 2.5],
    'Alcalinity': [15.0, 16.0, 14.0, 15.0],
    'Magnesium': [90, 85, 92, 87]
})
print(data)
# Standardize the data
scaler = StandardScaler()
standardized_data = scaler.fit_transform(data)
print("standardized_data: ", standardized_data)
covariance_matrix = np.cov(standardized_data.T)
print("covariance_matrix: ", covariance_matrix)
eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
print("eigenvalues: ", eigenvalues)
print("eigenvectors: ", eigenvectors)
sorted_indices = np.argsort(eigenvalues)[::-1]
print("sorted_indices: ", sorted_indices)
eigenvectors_sorted = eigenvectors[:, sorted_indices]
print("eigenvectors_sorted: ", eigenvectors_sorted)
# Select top 2 components
top_2_components = eigenvectors_sorted[:, :2]
print("top_2_components: ", top_2_components)
transformed_data = standardized_data.dot(top_2_components)
print("transformed_data: ", transformed_data)
plt.scatter(transformed_data[:, 0], transformed_data[:, 1])
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.title('PCA: 2D Projection of Wine Data')
plt.savefig('pca_2d_projection.png', format='png')

df1 = pd.DataFrame(standardized_data)
df2 = pd.DataFrame(transformed_data)

# Save DataFrames to CSV
df1.to_csv('matrix1.csv', index=False, header=False)  # index=False to avoid writing row numbers
df2.to_csv('matrix2.csv', index=False, header=False)  # header=False to avoid writing column names
