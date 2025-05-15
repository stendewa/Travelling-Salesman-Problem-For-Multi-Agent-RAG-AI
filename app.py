from flask import Flask, render_template, request
import pickle
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load data and models
df = pd.read_csv("optimized_transport_data.csv")
with open("random_forest_model.pkl", "rb") as f:
    rf_model = pickle.load(f)
with open("aco_model.pkl", "rb") as f:
    pheromones, heuristic, edge_weights, G = pickle.load(f)

# Constants
NUM_ANTS, NUM_ITERATIONS, EVAPORATION_RATE, Q = 10, 50, 0.5, 1.0
vehicle_load_capacity = {'SUV': 600, 'Truck': 5000, 'Saloon': 400, 'Coupe': 300, 'Hybrid': 500}

# ACO functions
def construct_solution(start, end):
    path, current, cost = [start], start, 0
    while current != end:
        neighbors = [n for n in G.neighbors(current) if n not in path]
        if not neighbors:
            return path, float('inf')
        probs = []
        for neighbor in neighbors:
            edge = (current, neighbor) if (current, neighbor) in pheromones else (neighbor, current)
            tau = pheromones[edge]
            eta = heuristic[edge]
            probs.append(tau * eta)
        probs = np.array(probs) / sum(probs)
        next_city = np.random.choice(neighbors, p=probs)
        cost += edge_weights.get((current, next_city), edge_weights.get((next_city, current), float('inf')))
        path.append(next_city)
        current = next_city
    return path, cost

def ant_colony_optimization(start, end):
    best_path, best_cost = None, float('inf')
    for _ in range(NUM_ITERATIONS):
        paths, costs = [], []
        for _ in range(NUM_ANTS):
            p, c = construct_solution(start, end)
            paths.append(p)
            costs.append(c)
            if c < best_cost:
                best_path, best_cost = p, c
        update_pheromones(paths, costs)
    return best_path, best_cost

def update_pheromones(paths, costs):
    for edge in pheromones:
        pheromones[edge] *= (1 - EVAPORATION_RATE)
    for path, cost in zip(paths, costs):
        for i in range(len(path) - 1):
            edge = (path[i], path[i+1]) if (path[i], path[i+1]) in pheromones else (path[i+1], path[i])
            pheromones[edge] += Q / cost

def calculate_total_distance_from_path(path):
    total = 0
    for i in range(len(path)-1):
        rows = df[(df['City of Origin'] == path[i]) & (df['Destination City'] == path[i+1])]
        if rows.empty:
            rows = df[(df['City of Origin'] == path[i+1]) & (df['Destination City'] == path[i])]
        if not rows.empty:
            total += rows['Distance (km)'].mean()
    return total

def predict_vehicle(total_distance, load_weight):
    fuel_eff = df.groupby("Vehicle Type")["Fuel Consumption (L/100km)"].mean()
    est_fuel = total_distance * fuel_eff / 100
    features = np.array([[total_distance, load_weight, est_fuel.mean(), 0, 0]])
    return rf_model.predict(features)[0]

def plot_path(path):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(6,5))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=1500)
    if path:
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode()

@app.route('/', methods=['GET', 'POST'])
def index():
    context = {}
    if request.method == 'POST':
        start = request.form['start']
        end = request.form['end']
        weight = float(request.form['weight'])

        # ML path: shortest
        try:
            ml_path = nx.shortest_path(G, source=start, target=end, weight='weight')
            ml_distance = calculate_total_distance_from_path(ml_path)
            ml_vehicle = predict_vehicle(ml_distance, weight)
            ml_plot = plot_path(ml_path)
        except:
            ml_path, ml_distance, ml_vehicle, ml_plot = [], 0, 'N/A', None

        # ACO path
        aco_path, _ = ant_colony_optimization(start, end)
        aco_distance = calculate_total_distance_from_path(aco_path)
        aco_vehicle = predict_vehicle(aco_distance, weight)
        aco_plot = plot_path(aco_path)

        context = {
            'start': start, 'end': end, 'weight': weight,
            'ml_path': " → ".join(ml_path),
            'ml_vehicle': ml_vehicle,
            'ml_distance': f"{ml_distance:.2f} km",
            'ml_plot': ml_plot,
            'aco_path': " → ".join(aco_path),
            'aco_vehicle': aco_vehicle,
            'aco_distance': f"{aco_distance:.2f} km",
            'aco_plot': aco_plot
        }
    return render_template("index.html", **context)

if __name__ == '__main__':
    app.run(debug=True)
