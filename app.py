from flask import Flask, render_template, request
import pickle
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# ✅ Initialize Flask App
app = Flask(__name__)

# ✅ Load dataset
df = pd.read_csv('optimized_transport_data.csv')

# ✅ Load trained Random Forest model
with open('random_forest_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# ✅ Load trained ACO model
try:
    with open('aco_model.pkl', 'rb') as aco_file:
        aco_data = pickle.load(aco_file)
        pheromones, heuristic, edge_weights, G = aco_data  # Ensure correct unpacking
except Exception as e:
    print(f"⚠️ Error loading ACO model: {e}")
    pheromones, heuristic, edge_weights, G = {}, {}, {}, nx.Graph()  # Fallback empty graph

# ✅ ACO Parameters
NUM_ANTS = 10
NUM_ITERATIONS = 100
EVAPORATION_RATE = 0.5
Q = 1.0

def find_best_route(start, destination):
    """Finds the best route using ACO."""
    if start not in G or destination not in G:
        return None, None  # Handle missing nodes
    
    best_path, best_cost = None, float('inf')

    for _ in range(NUM_ITERATIONS):
        paths, costs = [], []
        for _ in range(NUM_ANTS):
            path, cost = construct_solution(start, destination)
            paths.append(path)
            costs.append(cost)
            if cost < best_cost:
                best_path, best_cost = path, cost
        update_pheromones(paths, costs)

    if best_cost == float('inf'):
        return None, None  # No valid route found
    
    total_distance = df.loc[(df["City of Origin"] == start) & (df["Destination City"] == destination), "Distance (km)"].unique()
    return best_path, total_distance

def construct_solution(start, end):
    """Constructs a path using ACO selection probabilities."""
    path, current_city, total_cost = [start], start, 0

    while current_city != end:
        neighbors = [n for n in G.neighbors(current_city) if n not in path]
        if not neighbors:
            return path, float('inf')  # Dead-end

        probabilities = []
        for neighbor in neighbors:
            edge = (current_city, neighbor) if (current_city, neighbor) in pheromones else (neighbor, current_city)
            tau, eta = pheromones.get(edge, 1) ** 1, heuristic.get(edge, 1) ** 2
            probabilities.append(tau * eta)

        probabilities = np.array(probabilities) / sum(probabilities)
        next_city = np.random.choice(neighbors, p=probabilities)

        path.append(next_city)
        total_cost += edge_weights.get((current_city, next_city), edge_weights.get((next_city, current_city), float('inf')))
        current_city = next_city

    return path, total_cost

def update_pheromones(paths, costs):
    """Updates pheromone levels based on paths taken."""
    global pheromones
    for edge in pheromones:
        pheromones[edge] *= (1 - EVAPORATION_RATE)
    for path, cost in zip(paths, costs):
        for i in range(len(path) - 1):
            edge = (path[i], path[i+1]) if (path[i], path[i+1]) in pheromones else (path[i+1], path[i])
            pheromones[edge] += Q / cost

def predict_best_vehicle(total_distance, load_weight):
    """
    Predicts the best vehicle type using all five required features.
    Estimates the missing values using averages from the training dataset.
    """
    # Use dataset averages or heuristics
    avg_speed = df["Speed (km/h)"].mean()
    avg_fuel = df["Fuel Consumption (L/100km)"].mean()
    avg_travel_time = total_distance / avg_speed  # time = distance / speed

    # Construct full feature set
    features = np.array([[avg_speed, avg_fuel, avg_travel_time, total_distance, load_weight]])

    # Make prediction
    best_vehicle = model.predict(features)[0]

    return best_vehicle

def plot_route(best_path):
    """Plots the best route and returns the base64 image string."""
    plt.figure(figsize=(8,6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=1500, font_size=10)
    path_edges = [(best_path[i], best_path[i+1]) for i in range(len(best_path)-1)]
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start = request.form['start']
        destination = request.form['destination']
        try:
            load_weight = float(request.form['load_weight'])
        except ValueError:
            return render_template('index.html', error="Invalid load weight. Please enter a number.")

        best_path, total_distance = find_best_route(start, destination)
        if not best_path:
            return render_template('index.html', error="No valid route found!")

        best_vehicle = predict_best_vehicle(total_distance, load_weight)
        plot_url = plot_route(best_path)

        return render_template('index.html', 
                               start=start, 
                               destination=destination,
                               load_weight=load_weight,
                               best_path=" → ".join(best_path),
                               total_distance=total_distance,
                               best_vehicle=best_vehicle,
                               plot_url=plot_url)

    return render_template('index.html')

if __name__ == '__main__':
    app.run()
