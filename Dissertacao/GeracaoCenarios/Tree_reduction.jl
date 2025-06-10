using Clustering, Distances, Random
# Step 1: Generate initial scenarios (example: random time series)
Random.seed!(123)  # For reproducibility
n_scenarios = 100  # Number of scenarios
n_time_steps = 10  # Number of time steps
scenarios = [rand(n_time_steps) for _ in 1:n_scenarios]  # Random scenarios

# Step 2: Convert scenarios to a matrix (each row is a scenario)
scenario_matrix = hcat(scenarios...)'

# Step 3: Choose the number of clusters (k)
k = 10  # Number of clusters (reduced scenarios)

# Step 4: Perform k-means clustering
result = kmeans(scenario_matrix, k; maxiter=200, display=:iter)

# Step 5: Get the centroids (representative scenarios)
representative_scenarios = result.centers'

# Step 6: Assign scenarios to clusters
cluster_assignments = result.assignments

# Step 7: Compute probabilities for the reduced tree
cluster_probabilities = [sum(cluster_assignments .== i) / n_scenarios for i in 1:k]

# Step 8: Output the results
println("Representative Scenarios:")
println(representative_scenarios)
println("Cluster Probabilities:")
println(cluster_probabilities)