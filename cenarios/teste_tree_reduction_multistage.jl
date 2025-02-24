using Clustering, Distances, Random

# Step 1: Define the tree structure
tree = Dict(
    1 => [2, 3, 4],  # Node 1 has children 2, 3, 4
    2 => [5, 6, 7],  # Node 2 has children 5, 6, 7
    3 => [8, 9, 10], # Node 3 has children 8, 9, 10
    4 => [11, 12, 13] # Node 4 has children 11, 12, 13
)

# Step 2: Generate random data for each node
Random.seed!(123)
node_data = Dict(
    i => rand(5) for i in 1:13  # Each node has a 5-dimensional vector
)

# Step 3: Cluster leaf nodes (Stage 3)
leaf_nodes = [5, 6, 7, 8, 9, 10, 11, 12, 13]
leaf_data = hcat([node_data[i] for i in leaf_nodes]...)'
k_leaf = 4  # Number of clusters for leaf nodes
result_leaf = kmeans(leaf_data, k_leaf)
representative_leaf = result_leaf.centers'
cluster_assignments_leaf = result_leaf.assignments

# Step 4: Replace leaf nodes with representative nodes
reduced_tree = Dict()
reduced_tree[1] = [2, 3, 4]
reduced_tree[2] = [6, 14]  # Node 14 represents the cluster of Nodes 5 and 7
reduced_tree[3] = [8, 9, 10]
reduced_tree[4] = [11, 12, 13]

# Step 5: Cluster intermediate nodes (Stage 2)
intermediate_nodes = [2, 3, 4]
intermediate_data = hcat([node_data[i] for i in intermediate_nodes]...)'
k_intermediate = 2  # Number of clusters for intermediate nodes
result_intermediate = kmeans(intermediate_data, k_intermediate)
representative_intermediate = result_intermediate.centers'
cluster_assignments_intermediate = result_intermediate.assignments

# Step 6: Replace intermediate nodes with representative nodes
reduced_tree[1] = [15, 16]  # Nodes 15 and 16 represent clusters of Nodes 2, 3, 4

# Step 7: Output the reduced tree
println("Reduced Tree:")
for (parent, children) in reduced_tree
    println("Node $parent -> ", children)
end