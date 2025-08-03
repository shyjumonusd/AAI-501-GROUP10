# route_simulation_instrument_cluster.py
# Route Simulation with Instrument Cluster UI
# Author : Nankandiyil Shyjumon <snankandiyil@sandiego.edu>
# Location: Bengaluru, Karnataka, India

# Description:
# This code simulates a driving route within Bengaluru using OpenStreetMap data
# and visualizes it with a dual-panel UI:
# - Left Panel: Route map with animated car icon
# - Right Panel: Speed dial instrument cluster showing speed, ETA, fuel cost, and traffic conditions
# 
# Features:
# - Downloads or loads pre-saved road network data using OSMnx
# - Computes shortest driving path between two coordinates
# - Estimates travel time, fuel cost, and traffic conditions based on weekday
# - Displays route on a map with animated car movement
# - Renders a stylized polar speedometer with contextual driving info
# 
# Data set:
# - Downloads and caches road network data in: data/osmnx_data/
# - Graph file: bengaluru_drive_network.graphml

import os
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import contextily as ctx
import matplotlib.animation as animation
import numpy as np
import datetime

# Define the place and file paths
PLACE_NAME = "Bengaluru, Karnataka, India"
DATA_PATH = "data/osmnx_data/"
GRAPH_FILE = "bengaluru_drive_network.graphml"

def get_bengaluru_graph():
    graph_filepath = os.path.join(DATA_PATH, GRAPH_FILE)
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    if os.path.exists(graph_filepath):
        print("Loading road network data from local file...")
        G = ox.load_graphml(graph_filepath)
    else:
        print("Local graph file not found. Downloading data for Bengaluru...")
        G = ox.graph_from_place(PLACE_NAME, network_type="drive")
        ox.save_graphml(G, filepath=graph_filepath)
        print(f"Data for Bengaluru downloaded and saved to: {graph_filepath}")
    return G

def plot_optimal_path(start_coords, end_coords, graph):
    print(f"\nCalculating route from {start_coords} to {end_coords}")
    
    orig_node = ox.distance.nearest_nodes(graph, start_coords[1], start_coords[0])
    dest_node = ox.distance.nearest_nodes(graph, end_coords[1], end_coords[0])

    try:
        route_nodes = ox.shortest_path(graph, orig_node, dest_node, weight="length")
        if not route_nodes:
            print("No path found.")
            return

        route_length_m = sum(graph.get_edge_data(route_nodes[i], route_nodes[i+1])[0]['length']
                             for i in range(len(route_nodes) - 1))
        route_length_km = route_length_m / 1000

        today = datetime.datetime.now().weekday()
        traffic_condition = "🚦 Heavy Traffic" if today < 5 else "🛣️ Moderate Traffic"
        avg_speed_kmh = 25 if today < 5 else 35
        time_taken_minutes = (route_length_km / avg_speed_kmh) * 60
        fuel_efficiency_kml = 15
        fuel_price_per_liter = 110
        estimated_fuel_cost = (route_length_km / fuel_efficiency_kml) * fuel_price_per_liter
        weather_condition = "🌤️ Partly Cloudy"

        route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route_nodes]
        lats, lons = zip(*route_coords)

        fig = plt.figure(figsize=(16, 8))
        ax_map = fig.add_subplot(121)
        ax_ui = fig.add_subplot(122, polar=True)

        # --- Map Plot ---
        ax_map.plot(lons, lats, color='red', linewidth=3, label='Route')
        ax_map.scatter(start_coords[1], start_coords[0], c='green', s=100, label='Start')
        ax_map.scatter(end_coords[1], end_coords[0], c='blue', s=100, label='Destination')
        ctx.add_basemap(ax_map, crs=graph.graph['crs'], source=ctx.providers.CartoDB.Positron)
        ax_map.set_title("🗺️ Route Map")
        ax_map.legend()

        # --- Speed Dial UI (Oval Simulation) ---
        ax_ui.set_theta_zero_location("W")
        ax_ui.set_theta_direction(-1)
        ax_ui.set_facecolor("#0f0f0f")
        ax_ui.grid(False)
        ax_ui.set_yticklabels([])
        ax_ui.set_xticklabels([])
        ax_ui.set_aspect(0.8)  # Simulate oval shape

        max_speed = 120
        tick_interval = 10
        for speed in range(0, max_speed + tick_interval, tick_interval):
            angle_deg = 180 - (speed / max_speed) * 180
            angle_rad = np.deg2rad(angle_deg)
            ax_ui.plot([angle_rad, angle_rad], [0.8, 1.0], color="white", lw=2)
            ax_ui.text(angle_rad, 1.1, f"{speed}", color="white", ha="center", va="center", fontsize=10)

        speed_angle_deg = 180 - (avg_speed_kmh / max_speed) * 180
        speed_angle_rad = np.deg2rad(speed_angle_deg)
        ax_ui.plot([speed_angle_rad, speed_angle_rad], [0, 0.9], color="red", lw=3)

        center_text = (
            f"Speed: {avg_speed_kmh} km/h\n"
            f"Distance: {route_length_km:.1f} km | ETA: {time_taken_minutes:.0f} min\n"
            f"Fuel Cost: ₹{estimated_fuel_cost:.0f}\n"
            f"Traffic: {traffic_condition}"
        )
        ax_ui.text(0, 0, center_text, ha="center", va="center", fontsize=12, color="white", fontweight='bold')
        ax_ui.set_title("🚗 Speed Dial", fontsize=14, color="white", pad=20)

        # --- Car Icon Animation ---
        car_icon = ax_map.text(lons[0], lats[0], "🚗", fontsize=14, ha='center', va='center')

        def animate(i):
            if i < len(lons):
                car_icon.set_position((lons[i], lats[i]))
            return car_icon,

        ani = animation.FuncAnimation(fig, animate, frames=len(lons), interval=200, blit=True)

        plt.tight_layout()
        plt.show()

    except nx.NetworkXNoPath:
        print("No path found between the specified locations.")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    bengaluru_graph = get_bengaluru_graph()
    start_point = (12.9788, 77.5999)  # Near M. Chinnaswamy Stadium
    end_point = (12.9304, 77.6784)    # Near Bellandur
    plot_optimal_path(start_point, end_point, bengaluru_graph)
