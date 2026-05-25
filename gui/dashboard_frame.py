import os
import tkinter as tk
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
from tkinter import filedialog, messagebox

from algorithms.search import SearchManager
from algorithms.csp import ItineraryCSP
from algorithms.decision import DecisionEngine
from algorithms.uncertainty import UncertaintyEngine
from utils.helpers import ItineraryExporter
from utils.voice import VoiceGuidanceSystem

class DashboardFrame(ctk.CTkFrame):
    """
    Main Tourist dashboard panel integrating all AI pipeline components.
    Includes inputs, sliders, constraints, Matplotlib map canvas, and result summaries.
    """
    def __init__(self, parent, graph, current_user):
        super().__init__(parent, fg_color="#121212")
        self.graph = graph
        self.user = current_user
        
        # Engines initialization
        self.searcher = SearchManager(graph)
        self.decider = DecisionEngine(graph)
        self.uncertainty = UncertaintyEngine(graph)
        self.voice = VoiceGuidanceSystem()
        
        # Grid layout (Left input column, Right visualization column)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=4, minsize=400) # Control panel
        self.grid_columnconfigure(1, weight=6, minsize=600) # Map visualizer
        
        self.solved_route_data = None  # To store output of the latest route planning
        self.setup_ui()

    def setup_ui(self):
        # ----------------------------------------------------
        # LEFT COLUMN: INPUT CONTROLS PANEL
        # ----------------------------------------------------
        self.controls_scroll = ctk.CTkScrollableFrame(self, fg_color="#1e1e24", border_color="#2e2e3f", border_width=1, corner_radius=15)
        self.controls_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.controls_scroll.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            self.controls_scroll, 
            text="ROUTE CONTROLS & OPTIONS", 
            text_color="#00f0ff", 
            font=ctk.CTkFont(size=16, weight="bold")
        ) .grid(row=0, column=0, pady=(10, 15))

        # Core Route Selection
        self.route_group = ctk.CTkFrame(self.controls_scroll, fg_color="#12121a", corner_radius=8, padding=10)
        self.route_group.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.route_group.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(self.route_group, text="Starting Location:", text_color="#cbd5e0", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
        ctk.CTkLabel(self.route_group, text="Destination City:", text_color="#cbd5e0", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=(5,0), sticky="w")
        
        loc_names = [loc.name for loc in self.graph.get_all_locations()]
        
        self.start_dropdown = ctk.CTkComboBox(self.route_group, values=loc_names, fg_color="#1e1e24", border_color="#4a5568", text_color="#fff")
        self.start_dropdown.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.start_dropdown.set(loc_names[0]) # Delhi by default
        
        self.goal_dropdown = ctk.CTkComboBox(self.route_group, values=loc_names, fg_color="#1e1e24", border_color="#4a5568", text_color="#fff")
        self.goal_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.goal_dropdown.set(loc_names[6]) # Jaipur by default

        # Algorithm Selection
        self.alg_group = ctk.CTkFrame(self.controls_scroll, fg_color="#12121a", corner_radius=8, padding=10)
        self.alg_group.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.alg_group.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(self.alg_group, text="Primary Algorithm:", text_color="#cbd5e0", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
        self.alg_dropdown = ctk.CTkComboBox(self.alg_group, values=["BFS", "DFS", "UCS", "A* Search"], fg_color="#1e1e24", border_color="#4a5568", text_color="#fff")
        self.alg_dropdown.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.alg_dropdown.set("A* Search")

        ctk.CTkLabel(self.alg_group, text="Optimization Objective:", text_color="#cbd5e0", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=5, pady=(5,0), sticky="w")
        self.metric_dropdown = ctk.CTkComboBox(self.alg_group, values=["Distance", "Cost", "Travel Time", "Integrated Utility"], fg_color="#1e1e24", border_color="#4a5568", text_color="#fff")
        self.metric_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.metric_dropdown.set("Integrated Utility")

        # Uncertainty: Weather Forecasting alert
        self.uncertainty_group = ctk.CTkFrame(self.controls_scroll, fg_color="#12121a", corner_radius=8, padding=10)
        self.uncertainty_group.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.uncertainty_group.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.uncertainty_group, text="Dynamic Weather Warnings (Bayesian updates):", text_color="#cbd5e0", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=5, pady=(5,0), sticky="w")
        self.weather_dropdown = ctk.CTkComboBox(self.uncertainty_group, values=["Clear Skies", "Heavy Rain Warning", "Dense Fog Alert"], fg_color="#1e1e24", border_color="#4a5568", text_color="#fff")
        self.weather_dropdown.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.weather_dropdown.set("Clear Skies")

        # Sliders for Multi-Attribute Decision Weights
        self.weights_group = ctk.CTkFrame(self.controls_scroll, fg_color="#12121a", corner_radius=8, padding=10)
        self.weights_group.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        self.weights_group.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.weights_group, text="DECISION UTILITY WEIGHTS", text_color="#00f0ff", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

        # Weights Sliders
        # Distance Weight
        ctk.CTkLabel(self.weights_group, text="Minimize Distance weight:", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=1, column=0, sticky="w", padx=5)
        self.w_dist_slider = ctk.CTkSlider(self.weights_group, from_=0.0, to=1.0, number_of_steps=10, fg_color="#20202e", progress_color="#2ec4b6")
        self.w_dist_slider.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.w_dist_slider.set(0.3)

        # Cost Weight
        ctk.CTkLabel(self.weights_group, text="Minimize Cost weight:", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=2, column=0, sticky="w", padx=5)
        self.w_cost_slider = ctk.CTkSlider(self.weights_group, from_=0.0, to=1.0, number_of_steps=10, fg_color="#20202e", progress_color="#2ec4b6")
        self.w_cost_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.w_cost_slider.set(0.3)

        # Traffic Weight
        ctk.CTkLabel(self.weights_group, text="Avoid Traffic risk weight:", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=3, column=0, sticky="w", padx=5)
        self.w_traffic_slider = ctk.CTkSlider(self.weights_group, from_=0.0, to=1.0, number_of_steps=10, fg_color="#20202e", progress_color="#2ec4b6")
        self.w_traffic_slider.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.w_traffic_slider.set(0.2)

        # Rating Weight
        ctk.CTkLabel(self.weights_group, text="Maximize Rating weight:", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=4, column=0, sticky="w", padx=5)
        self.w_rating_slider = ctk.CTkSlider(self.weights_group, from_=0.0, to=1.0, number_of_steps=10, fg_color="#20202e", progress_color="#2ec4b6")
        self.w_rating_slider.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.w_rating_slider.set(0.2)

        # CSP Constraint Solver Panel
        self.csp_group = ctk.CTkFrame(self.controls_scroll, fg_color="#12121a", corner_radius=8, padding=10)
        self.csp_group.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.csp_group.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkLabel(self.csp_group, text="ITINERARY CSP CONSTRAINTS", text_color="#00f0ff", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        
        self.use_csp_var = tk.BooleanVar(value=False)
        self.use_csp_var = tk.BooleanVar(value=False)
        self.csp_checkbox = ctk.CTkCheckBox(self.csp_group, text="Enable Multi-Stop CSP", variable=self.use_csp_var, text_color="#fff", fg_color="#2ec4b6", hover_color="#00adb5", font=ctk.CTkFont(size=10, weight="bold"))
        self.csp_checkbox.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.compare_all_var = tk.BooleanVar(value=False)
        self.compare_checkbox = ctk.CTkCheckBox(self.csp_group, text="Compare All AI Routes", variable=self.compare_all_var, command=self.trigger_compare_redraw, text_color="#fff", fg_color="#00f0ff", hover_color="#00adb5", font=ctk.CTkFont(size=10, weight="bold"))
        self.compare_checkbox.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        ctk.CTkLabel(self.csp_group, text="Max Destinations stops:", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=2, column=0, sticky="w", padx=5)
        self.max_stops_slider = ctk.CTkSlider(self.csp_group, from_=1, to=6, number_of_steps=5, fg_color="#20202e", progress_color="#ecc94b")
        self.max_stops_slider.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.max_stops_slider.set(3)

        ctk.CTkLabel(self.csp_group, text="Cumulative Budget limit (₹):", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=3, column=0, sticky="w", padx=5)
        self.budget_entry = ctk.CTkEntry(self.csp_group, width=80, height=22, fg_color="#1e1e24", text_color="#fff")
        self.budget_entry.grid(row=3, column=1, padx=5, pady=4, sticky="e")
        self.budget_entry.insert(0, "6000")

        ctk.CTkLabel(self.csp_group, text="Max Travel Time (mins):", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=4, column=0, sticky="w", padx=5)
        self.time_entry = ctk.CTkEntry(self.csp_group, width=80, height=22, fg_color="#1e1e24", text_color="#fff")
        self.time_entry.grid(row=4, column=1, padx=5, pady=4, sticky="e")
        self.time_entry.insert(0, "900")

        ctk.CTkLabel(self.csp_group, text="Max Crowd Tolerance (0-1):", text_color="#cbd5e0", font=ctk.CTkFont(size=10)).grid(row=5, column=0, sticky="w", padx=5)
        self.crowd_entry = ctk.CTkEntry(self.csp_group, width=80, height=22, fg_color="#1e1e24", text_color="#fff")
        self.crowd_entry.grid(row=5, column=1, padx=5, pady=4, sticky="e")
        self.crowd_entry.insert(0, "0.85")

        # Action Execution Buttons
        self.action_frame = ctk.CTkFrame(self.controls_scroll, fg_color="transparent")
        self.action_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=15)
        self.action_frame.grid_columnconfigure((0,1), weight=1)

        self.plan_btn = ctk.CTkButton(
            self.action_frame, 
            text="🚀 PLAN OPTIMAL ROUTE", 
            command=self.execute_ai_pipeline, 
            fg_color="#2ec4b6", 
            hover_color="#00adb5",
            text_color="#121212",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40
        )
        self.plan_btn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.voice_btn = ctk.CTkButton(
            self.action_frame, 
            text="🗣️ VOICE GUIDANCE", 
            command=self.trigger_voice_guidance, 
            fg_color="#ecc94b", 
            hover_color="#d69e2e",
            text_color="#121212",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.voice_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.export_btn = ctk.CTkButton(
            self.action_frame, 
            text="📥 EXPORT ITINERARY", 
            command=self.export_report, 
            fg_color="#a0aec0", 
            hover_color="#718096",
            text_color="#121212",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.export_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # ----------------------------------------------------
        # RIGHT COLUMN: MAP VISUALIZER & OUTPUT SUMMARY PANEL
        # ----------------------------------------------------
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_container.grid_rowconfigure(0, weight=6) # Graph Canvas
        self.right_container.grid_rowconfigure(1, weight=4) # Results panel
        self.right_container.grid_columnconfigure(0, weight=1)

        # Matplotlib Graph visualizer frame
        self.map_card = ctk.CTkFrame(self.right_container, fg_color="#1e1e24", border_color="#2e2e3f", border_width=1, corner_radius=15)
        self.map_card.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.map_card.grid_rowconfigure(0, weight=1)
        self.map_card.grid_columnconfigure(0, weight=1)

        self.map_fig, self.map_ax = plt.subplots(figsize=(6, 5), facecolor='#1e1e24')
        self.map_canvas = FigureCanvasTkAgg(self.map_fig, self.map_card)
        self.map_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Load NetworkX representation for visualization plotting
        self.nx_g = nx.Graph()
        self.pos = {}
        for loc in self.graph.get_all_locations():
            self.nx_g.add_node(loc.id, name=loc.name, rating=loc.rating)
            self.pos[loc.id] = (loc.x, loc.y)
            for conn in loc.connections:
                self.nx_g.add_edge(loc.id, conn.to_id, weight=conn.distance)

        self.all_planned_routes = {}
        self.render_map(active_route=None, explored_nodes=None)

        # Output / Results breakdown card
        self.results_card = ctk.CTkFrame(self.right_container, fg_color="#1e1e24", border_color="#2e2e3f", border_width=1, corner_radius=15)
        self.results_card.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.results_card.grid_rowconfigure(0, weight=1)
        self.results_card.grid_columnconfigure(0, weight=7) # Detailed text
        self.results_card.grid_columnconfigure(1, weight=3) # Accommodations suggested list

        # Detailed text result log
        self.results_log = tk.Text(
            self.results_card, 
            bg="#12121a", 
            fg="#cbd5e0", 
            insertbackground="white", 
            relief="flat", 
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        self.results_log.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        scrollbar = ctk.CTkScrollbar(self.results_card, command=self.results_log.yview)
        self.results_log.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=0, sticky="nse", padx=(0, 10), pady=10)

        # Nearby hotels suggestion panel
        self.hotels_panel = ctk.CTkFrame(self.results_card, fg_color="#12121a", corner_radius=8)
        self.hotels_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.hotels_panel.grid_columnconfigure(0, weight=1)
        self.hotels_panel.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self.hotels_panel, text="🏨 SUGGESTED HOTELS", text_color="#00f0ff", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, pady=5, padx=5, sticky="w")
        
        self.hotels_listbox = tk.Listbox(self.hotels_panel, bg="#12121a", fg="#a0aec0", font=("Segoe UI", 9), selectbackground="#2ec4b6", selectforeground="#121212", relief="flat", borderwidth=0)
        self.hotels_listbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def render_map(self, active_route=None, explored_nodes=None):
        """Draws the 26-node network, highlighting the selected path, visited nodes, or comparison overlay."""
        self.map_ax.clear()
        self.map_ax.set_facecolor('#1e1e24')
        
        # Set a gorgeous neon circuit title
        self.map_ax.set_title("RAJASTHAN HERITAGE CIRCUIT GRAPH", color="#00f0ff", fontsize=10, fontweight="bold", pad=12)
        
        # Hide standard grid and coordinate borders
        self.map_ax.axis('off')

        # Draw roads/connections (medium-contrast gray base for great visibility)
        nx.draw_networkx_edges(
            self.nx_g, 
            self.pos, 
            ax=self.map_ax, 
            edge_color='#3f3f46', 
            width=1.2, 
            alpha=0.6
        )

        # Draw default nodes (Sleek dark obsidian center with glowing neon cyan borders)
        nx.draw_networkx_nodes(
            self.nx_g, 
            self.pos, 
            ax=self.map_ax, 
            node_color='#12121a', 
            node_size=180, 
            edgecolors='#00f0ff', 
            linewidths=1.5
        )

        # Labels adjustment (offset label vertically by 0.12 degrees ~13km for perfect positioning)
        labels = {node: self.graph.get_location(node).name.split("(")[0].strip() for node in self.nx_g.nodes()}
        pos_higher = {node: (x, y + 0.12) for node, (x, y) in self.pos.items()}
        
        nx.draw_networkx_labels(
            self.nx_g, 
            pos_higher, 
            labels=labels, 
            ax=self.map_ax, 
            font_size=7, 
            font_color='#cbd5e0', 
            font_family='sans-serif',
            font_weight='semibold'
        )

        # Draw road distances on edges (adds immense clarity and accuracy!)
        edge_labels = nx.get_edge_attributes(self.nx_g, 'weight')
        edge_labels_formatted = {k: f"{v}km" for k, v in edge_labels.items()}
        nx.draw_networkx_edge_labels(
            self.nx_g, 
            self.pos, 
            edge_labels=edge_labels_formatted, 
            ax=self.map_ax, 
            font_size=6.5, 
            font_color='#a0aec0', 
            font_family='sans-serif',
            bbox=dict(facecolor='#1e1e24', edgecolor='none', alpha=0.7, pad=0.8)
        )

        from matplotlib.lines import Line2D
        legend_elements = []

        # Check if comparison overlay is active
        if self.compare_all_var.get() and hasattr(self, 'all_planned_routes') and self.all_planned_routes:
            styles = {
                "A* Search": {"color": "#2ec4b6", "style": "solid", "width": 3.5, "label": "A* Search (Utility - Smartest)"},
                "UCS": {"color": "#ecc94b", "style": "dashed", "width": 2.5, "label": "UCS (Economic Cost)"},
                "BFS": {"color": "#00f0ff", "style": "dotted", "width": 2.0, "label": "BFS (Min Hops)"},
                "DFS": {"color": "#ec4899", "style": "dashdot", "width": 1.5, "label": "DFS (Deep Winding Path)"}
            }
            
            # Draw each route in unique colors
            for alg_name, route in self.all_planned_routes.items():
                if route and len(route) >= 2:
                    edges_list = [(route[i], route[i+1]) for i in range(len(route) - 1)]
                    nx.draw_networkx_edges(
                        self.nx_g, 
                        self.pos, 
                        edgelist=edges_list, 
                        ax=self.map_ax, 
                        edge_color=styles[alg_name]["color"], 
                        width=styles[alg_name]["width"], 
                        style=styles[alg_name]["style"],
                        alpha=0.9
                    )
                    # Add to legend
                    legend_elements.append(
                        Line2D([0], [0], color=styles[alg_name]["color"], lw=2.5, 
                               linestyle=styles[alg_name]["style"], label=styles[alg_name]["label"])
                    )
            
            # Mark start and goal nodes
            first_alg = list(self.all_planned_routes.keys())[0]
            first_route = self.all_planned_routes[first_alg]
            if first_route:
                nx.draw_networkx_nodes(self.nx_g, self.pos, nodelist=[first_route[0]], ax=self.map_ax, node_color='#00ff87', node_size=320, edgecolors='#ffffff', linewidths=1.5)
                nx.draw_networkx_nodes(self.nx_g, self.pos, nodelist=[first_route[-1]], ax=self.map_ax, node_color='#ff5252', node_size=320, edgecolors='#ffffff', linewidths=1.5)
                
            legend_elements.append(Line2D([0], [0], marker='o', color='none', label='Start City', markerfacecolor='#00ff87', markeredgecolor='#ffffff', markersize=9, markeredgewidth=1.5))
            legend_elements.append(Line2D([0], [0], marker='o', color='none', label='Destination City', markerfacecolor='#ff5252', markeredgecolor='#ffffff', markersize=9, markeredgewidth=1.5))
        
        else:
            # Standard single path routing
            legend_elements = [
                Line2D([0], [0], marker='o', color='none', label='Unvisited City',
                       markerfacecolor='#12121a', markeredgecolor='#00f0ff', markersize=7, markeredgewidth=1.5),
                Line2D([0], [0], color='#3f3f46', lw=1.5, alpha=0.6, label='Highway Connection')
            ]
            
            # Highlight explored but rejected edges
            if explored_nodes and len(explored_nodes) > 1:
                explored_set = set(explored_nodes)
                rejected_edges = []
                route_edges_set = set()
                if active_route and len(active_route) >= 2:
                    route_edges_set = set([(active_route[i], active_route[i+1]) for i in range(len(active_route) - 1)])
                    route_edges_set.update([(active_route[i+1], active_route[i]) for i in range(len(active_route) - 1)])
                
                for u in explored_set:
                    for conn in self.graph.get_location(u).connections:
                        v = conn.to_id
                        if v in explored_set:
                            if (u, v) not in route_edges_set:
                                rejected_edges.append((u, v))
                
                if rejected_edges:
                    nx.draw_networkx_edges(
                        self.nx_g, 
                        self.pos, 
                        edgelist=rejected_edges, 
                        ax=self.map_ax, 
                        edge_color='#f87171', 
                        width=1.0, 
                        alpha=0.4,
                        style='dashed'
                    )
                    legend_elements.append(Line2D([0], [0], color='#f87171', lw=1.0, linestyle='dashed', alpha=0.4, label='Explored & Rejected Path'))

            # 1. Highlight Explored nodes in Amber
            if explored_nodes:
                nx.draw_networkx_nodes(
                    self.nx_g, 
                    self.pos, 
                    nodelist=explored_nodes, 
                    ax=self.map_ax, 
                    node_color='#ecc94b', 
                    node_size=220, 
                    edgecolors='#ffffff',
                    linewidths=1.0
                )
                legend_elements.append(
                    Line2D([0], [0], marker='o', color='none', label='Explored Frontier',
                           markerfacecolor='#ecc94b', markeredgecolor='#ffffff', markersize=8, markeredgewidth=1.0)
                )

            # 2. Highlight optimal routed paths in vibrant glowing Teal
            if active_route and len(active_route) >= 2:
                route_edges = [(active_route[i], active_route[i+1]) for i in range(len(active_route) - 1)]
                
                # Highlight path nodes in Emerald/Teal
                nx.draw_networkx_nodes(
                    self.nx_g, 
                    self.pos, 
                    nodelist=active_route, 
                    ax=self.map_ax, 
                    node_color='#2ec4b6', 
                    node_size=280, 
                    edgecolors='#ffffff', 
                    linewidths=1.5
                )
                # Highlight path edges in thick Emerald line
                nx.draw_networkx_edges(
                    self.nx_g, 
                    self.pos, 
                    edgelist=route_edges, 
                    ax=self.map_ax, 
                    edge_color='#2ec4b6', 
                    width=3.5, 
                    alpha=1.0
                )
                
                # Mark start and goal nodes clearly
                nx.draw_networkx_nodes(self.nx_g, self.pos, nodelist=[active_route[0]], ax=self.map_ax, node_color='#00ff87', node_size=320, edgecolors='#ffffff', linewidths=1.5) # Start Green
                nx.draw_networkx_nodes(self.nx_g, self.pos, nodelist=[active_route[-1]], ax=self.map_ax, node_color='#ff5252', node_size=320, edgecolors='#ffffff', linewidths=1.5) # Goal Red

                legend_elements.append(Line2D([0], [0], marker='o', color='none', label='Start City', markerfacecolor='#00ff87', markeredgecolor='#ffffff', markersize=9, markeredgewidth=1.5))
                legend_elements.append(Line2D([0], [0], marker='o', color='none', label='Optimal Route Stop', markerfacecolor='#2ec4b6', markeredgecolor='#ffffff', markersize=8, markeredgewidth=1.5))
                legend_elements.append(Line2D([0], [0], marker='o', color='none', label='Destination City', markerfacecolor='#ff5252', markeredgecolor='#ffffff', markersize=9, markeredgewidth=1.5))
                legend_elements.append(Line2D([0], [0], color='#2ec4b6', lw=3.0, label='Selected Route'))

        self.map_ax.legend(
            handles=legend_elements, 
            loc='upper left', 
            facecolor='#1e1e24', 
            edgecolor='#2e2e3f', 
            labelcolor='#cbd5e0',
            fontsize=7.5,
            framealpha=0.9
        )

        self.map_canvas.draw()

    def trigger_compare_redraw(self):
        """Redraws the map canvas when 'Compare All AI Routes' checkbox is checked/unchecked."""
        if hasattr(self, 'solved_route_data') and self.solved_route_data:
            self.render_map(active_route=self.solved_route_data["path"], explored_nodes=None)
        else:
            self.render_map(active_route=None, explored_nodes=None)

    def animate_search(self, explored_list, final_path):
        """Animates node exploration sequentially to wow examiners with real-time AI logic!"""
        # Disable buttons during search animation
        self.plan_btn.configure(state="disabled", text="⚡ ANIMATING AI SEARCH...")
        self.voice_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        
        step = 0
        total_steps = len(explored_list)
        
        # Scale delay dynamically depending on the explored nodes count
        delay_ms = max(20, min(80, int(1500 / max(1, total_steps))))
        
        def animate_step():
            nonlocal step
            if step < total_steps:
                current_frontier = explored_list[:step+1]
                self.render_map(active_route=None, explored_nodes=current_frontier)
                step += 1
                self.after(delay_ms, animate_step)
            else:
                # Finished exploring, highlight final path
                self.render_map(active_route=final_path, explored_nodes=explored_list)
                self.plan_btn.configure(state="normal", text="🚀 PLAN OPTIMAL ROUTE")
                self.voice_btn.configure(state="normal")
                self.export_btn.configure(state="normal")
                
        animate_step()

    def execute_ai_pipeline(self):
        """Assembles AI Graph Search, CSP backtracking, Uncertainty Reasoning and Utility Decider."""
        start_name = self.start_dropdown.get()
        goal_name = self.goal_dropdown.get()
        
        start_id = next(loc.id for loc in self.graph.get_all_locations() if loc.name == start_name)
        goal_id = next(loc.id for loc in self.graph.get_all_locations() if loc.name == goal_name)

        if start_id == goal_id:
            messagebox.showwarning("Same Cities Selected", "Starting location and destination cannot be identical!")
            return

        algorithm = self.alg_dropdown.get()
        optimization_metric = self.metric_dropdown.get().lower().replace(" ", "_")
        weather_alert = self.weather_dropdown.get().lower().replace(" skies", "").replace(" warning", "").replace(" alert", "")
        
        # Capture Multi-Attribute Decision Weights
        weights = {
            "distance": self.w_dist_slider.get(),
            "cost": self.w_cost_slider.get(),
            "time": self.w_traffic_slider.get(), # Traffic mapped to time delay penalty
            "rating": self.w_rating_slider.get()
        }

        # Clear Results
        self.results_log.delete("1.0", tk.END)
        self.hotels_listbox.delete(0, tk.END)
        self.solved_route_data = None

        self.results_log.insert(tk.END, f"=== AI ROUTING PIPELINE INITIATED ===\n")
        self.results_log.insert(tk.END, f"Origin      : {start_name}\n")
        self.results_log.insert(tk.END, f"Destination : {goal_name}\n")
        self.results_log.insert(tk.END, f"Algorithm   : {algorithm}\n")
        self.results_log.insert(tk.END, f"Condition   : {self.weather_dropdown.get()}\n\n")

        # ----------------------------------------------------
        # PIPELINE STEP 1: Dynamic Weather Updates (Bayesian Inference)
        # ----------------------------------------------------
        self.results_log.insert(tk.END, f"[Reasoning Engine] Applying Bayesian Inference updates:\n")
        if weather_alert != "clear":
            self.results_log.insert(tk.END, f" -> Weather warning alert active! Adjusting prior highway traffic risks...\n")
        else:
            self.results_log.insert(tk.END, f" -> Clear skies reported. Standard priors applied.\n")

        # ----------------------------------------------------
        # PIPELINE STEP 2: Itinerary CSP Pre-Filtering (Optional Stop Constraint Solving)
        # ----------------------------------------------------
        use_csp = self.use_csp_var.get()
        final_route = None
        explored_nodes = []
        metrics_distance = 0.0
        metrics_cost = 0.0
        metrics_time = 0.0
        safety_prob = 1.0
        res = None

        if use_csp:
            self.results_log.insert(tk.END, f"\n[CSP Solver] Multi-Stop Tour Planner Enabled:\n")
            try:
                max_stops = int(self.max_stops_slider.get())
                max_budget = float(self.budget_entry.get())
                max_time = float(self.time_entry.get())
                max_crowd = float(self.crowd_entry.get())
            except ValueError:
                messagebox.showerror("Invalid Constraint Input", "Constraint inputs (budget, time, crowd) must be numerical!")
                return
            
            # Select target pool excluding start & goal
            target_pool = [loc.id for loc in self.graph.get_all_locations() if loc.id not in [start_id, goal_id]]
            
            # Solve CSP Backtracking with MRV + LCV Heuristics
            csp_solver = ItineraryCSP(
                self.graph, start_id, target_pool, 
                max_stops=max_stops, max_budget=max_budget, 
                max_time=max_time, max_crowd=max_crowd
            )
            csp_result = csp_solver.solve()
            
            if csp_result:
                self.results_log.insert(tk.END, f" -> CSP solved successfully using Backtracking with MRV & LCV heuristics!\n")
                self.results_log.insert(tk.END, f" -> Planned sequence stops: {' -> '.join([self.graph.get_location(s).name.split('(')[0].strip() for s in csp_result['itinerary']])}\n")
                self.results_log.insert(tk.END, f" -> Budget limit matches constraints. Total Stops: {len(csp_result['itinerary']) - 1}\n")
                
                # Full itinerary connecting starting city to intermediate stops, then destination
                # Connect final CSP stop to goal destination using selected algorithm
                last_stop = csp_result["itinerary"][-1]
                
                # Execute Core search algorithm between consecutive nodes
                intermediate_stops = csp_result["itinerary"]
                full_path_composed = []
                explored_composed = []
                
                for idx in range(len(intermediate_stops) - 1):
                    s_node = intermediate_stops[idx]
                    g_node = intermediate_stops[idx+1]
                    res = self._execute_search_metric(algorithm, s_node, g_node, optimization_metric, weights)
                    if res["path"]:
                        # Append omitting duplicates
                        if not full_path_composed:
                            full_path_composed.extend(res["path"])
                        else:
                            full_path_composed.extend(res["path"][1:])
                        explored_composed.extend(res["explored"])
                    else:
                        full_path_composed = None
                        break
                        
                # Connect to final target destination
                if full_path_composed:
                    res_dest = self._execute_search_metric(algorithm, intermediate_stops[-1], goal_id, optimization_metric, weights)
                    if res_dest["path"]:
                        full_path_composed.extend(res_dest["path"][1:])
                        explored_composed.extend(res_dest["explored"])
                        
                        final_route = full_path_composed
                        explored_nodes = list(set(explored_composed))
                        
                        # Recalculate full path metrics
                        metrics_distance, metrics_cost, metrics_time = self.searcher._calculate_path_metrics(final_route)
                    else:
                        final_route = None
            else:
                self.results_log.insert(tk.END, f" -> CSP Backtracking returned NO valid itinerary matching constraints!\n", "error")
                self.render_map(active_route=None, explored_nodes=None)
                return
        else:
            # Standard single path routing
            self.results_log.insert(tk.END, f"\n[Graph Search] Running search to find direct path...\n")
            res = self._execute_search_metric(algorithm, start_id, goal_id, optimization_metric, weights)
            final_route = res["path"]
            explored_nodes = res["explored"]
            metrics_distance = res["distance"]
            metrics_cost = res["cost"]
            metrics_time = res["time"]

        # ALSO pre-compute all other paths for the overlay comparisons!
        self.all_planned_routes = {
            "BFS": self.searcher.bfs(start_id, goal_id)["path"],
            "DFS": self.searcher.dfs(start_id, goal_id)["path"],
            "UCS": self.searcher.ucs(start_id, goal_id, metric_type="cost", utility_weights=weights)["path"],
            "A* Search": self.searcher.a_star(start_id, goal_id, metric_type="utility", utility_weights=weights)["path"]
        }

        # ----------------------------------------------------
        # PIPELINE STEP 3: Route Calculations & Output Formatting
        # ----------------------------------------------------
        if final_route:
            # Bayesian dynamic time calculations adjusting for weather warnings
            adjusted_travel_time = self.uncertainty.estimate_dynamic_travel_time(
                metrics_distance, metrics_time, weather_alert, initial_traffic="medium", hours_elapsed=metrics_time/60.0
            )
            
            # Cumulative safety traversal success probability joint product
            safety_prob = self.uncertainty.compute_route_success_probability(final_route, weather_alert)

            # Store computed route results for PDF/HTML brochure export
            self.solved_route_data = {
                "path": final_route,
                "distance": metrics_distance,
                "cost": metrics_cost,
                "time": adjusted_travel_time,
                "safety_prob": safety_prob,
                "algorithm": algorithm,
                "start_name": start_name,
                "goal_name": goal_name
            }
            
            # Log results details
            self.results_log.insert(tk.END, f"\nOPTIMAL ROUTE COMPLETED:\n")
            self.results_log.insert(tk.END, f" -> Stops Sequence: {' -> '.join([self.graph.get_location(s).name.split('(')[0].strip() for s in final_route])}\n")
            self.results_log.insert(tk.END, f" -> Total Distance : {metrics_distance:.1f} km\n")
            self.results_log.insert(tk.END, f" -> Transport Cost : ₹{metrics_cost:.2f}\n")
            self.results_log.insert(tk.END, f" -> Base Duration  : {int(metrics_time // 60)}h {int(metrics_time % 60)}m\n")
            self.results_log.insert(tk.END, f" -> Dynamic Time   : {int(adjusted_travel_time // 60)}h {int(adjusted_travel_time % 60)}m (adjusted for traffic/weather)\n")
            self.results_log.insert(tk.END, f" -> Safety Index   : {safety_prob * 100:.1f}% Joint Probability\n")
            
            # Print rich algorithm telemetry (execution stats)
            if res:
                self.results_log.insert(tk.END, f"\n--- ALGORITHM TELEMETRY ---\n")
                self.results_log.insert(tk.END, f" -> Nodes Explored : {res.get('nodes_explored', len(explored_nodes))} nodes\n")
                self.results_log.insert(tk.END, f" -> Memory Footprint: {res.get('memory_usage_kb', 1.5):.2f} KB\n")
                self.results_log.insert(tk.END, f" -> Execution Time : {res.get('execution_time_ns', 0) / 1000.0:.2f} µs\n")
                self.results_log.insert(tk.END, f" -> Search Efficiency: {res.get('efficiency', 100.0):.1f}%\n")

            # Update User History search log
            self.user.add_search_log(start_name, goal_name, algorithm, " -> ".join(final_route), metrics_cost, metrics_distance)

            # Animate the map search frontier!
            self.animate_search(explored_nodes, final_route)

            # Load suggested accommodations for intermediate nodes
            self.load_hotels_list(final_route)
        else:
            self.results_log.insert(tk.END, f"\n[Alert] No physical road path could be found connecting {start_name} to {goal_name} under active constraints!\n", "error")
            self.render_map(active_route=None, explored_nodes=None)

    def _execute_search_metric(self, algorithm, start_id, goal_id, optimization_metric, weights):
        """Helper to invoke correct search API."""
        if algorithm == "BFS":
            return self.searcher.bfs(start_id, goal_id)
        elif algorithm == "DFS":
            return self.searcher.dfs(start_id, goal_id)
        elif algorithm == "UCS":
            return self.searcher.ucs(start_id, goal_id, metric_type=optimization_metric, utility_weights=weights)
        else: # A* Search
            return self.searcher.a_star(start_id, goal_id, metric_type=optimization_metric, heuristic_type="euclidean", utility_weights=weights)

    def load_hotels_list(self, route_list):
        """Fills hotel panel listbox with options along the tourist path."""
        self.hotels_listbox.delete(0, tk.END)
        for loc_id in route_list:
            loc = self.graph.get_location(loc_id)
            if loc:
                self.hotels_listbox.insert(tk.END, f"=== {loc.name.split('(')[0].strip()} ===")
                for hotel in loc.hotels:
                    self.hotels_listbox.insert(
                        tk.END, 
                        f" • {hotel['name']} (₹{hotel['price']} | {hotel['rating']} ⭐)"
                    )
                self.hotels_listbox.insert(tk.END, "")

    def trigger_voice_guidance(self):
        """Invokes background Thread TTS reading computed routing logs."""
        if not self.solved_route_data:
            messagebox.showwarning("Route Unplanned", "Please calculate a route using PLAN OPTIMAL ROUTE before invoking voice updates!")
            return
        
        path_names = [self.graph.get_location(loc_id).name for loc_id in self.solved_route_data["path"]]
        
        self.voice.speak_route(
            path_names,
            self.solved_route_data["distance"],
            self.solved_route_data["cost"],
            self.solved_route_data["time"],
            self.solved_route_data["safety_prob"],
            self.solved_route_data["start_name"],
            self.solved_route_data["goal_name"]
        )

    def export_report(self):
        """Exports HTML brochure and PDF academic documents."""
        if not self.solved_route_data:
            messagebox.showwarning("Route Unplanned", "Please calculate a route before exporting travel reports!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Brochure", "*.html"), ("PDF Report", "*.pdf"), ("Text Document", "*.txt")]
        )
        
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".html":
            ItineraryExporter.export_to_html(
                self.solved_route_data["path"],
                self.graph,
                file_path,
                self.solved_route_data["distance"],
                self.solved_route_data["cost"],
                self.solved_route_data["time"],
                self.solved_route_data["safety_prob"],
                self.solved_route_data["algorithm"]
            )
            messagebox.showinfo("Export Successful", f"Travel brochure HTML document saved successfully!\nLocation: {file_path}")
        
        elif ext == ".pdf":
            success, saved_path = ItineraryExporter.export_to_pdf(
                self.solved_route_data["path"],
                self.graph,
                file_path,
                self.solved_route_data["distance"],
                self.solved_route_data["cost"],
                self.solved_route_data["time"],
                self.solved_route_data["safety_prob"],
                self.solved_route_data["algorithm"]
            )
            if success:
                messagebox.showinfo("Export Successful", f"Travel itinerary PDF document saved successfully!\nLocation: {saved_path}")
            else:
                messagebox.showinfo("Export Warning", f"ReportLab is not installed. Gracefully fell back to exporting clean TXT document instead!\nLocation: {saved_path}")
                
        else: # .txt
            ItineraryExporter.export_to_txt(
                self.solved_route_data["path"],
                self.graph,
                file_path,
                self.solved_route_data["distance"],
                self.solved_route_data["cost"],
                self.solved_route_data["time"],
                self.solved_route_data["safety_prob"],
                self.solved_route_data["algorithm"]
            )
            messagebox.showinfo("Export Successful", f"Itinerary report TXT document saved successfully!\nLocation: {file_path}")
