import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class StatsFrame(ctk.CTkFrame):
    """
    GUI Frame rendering analytical comparison charts of search algorithms.
    Shows dual Matplotlib charts comparing execution speeds (microsecs) and path distances/costs.
    """
    def __init__(self, parent):
        super().__init__(parent, fg_color="#121212")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Style matplotlib globally for dark mode
        plt.style.use('dark_background')
        self.fig, (self.ax_time, self.ax_metrics) = plt.subplots(1, 2, figsize=(10, 5), facecolor='#121212')
        self.fig.subplots_adjust(bottom=0.2, top=0.9, left=0.1, right=0.95, wspace=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        
        # Legend/Table section at the bottom (Expanded for full telemetry!)
        self.table_frame = ctk.CTkFrame(self, fg_color="#1e1e24", border_color="#2e2e3f", border_width=1, corner_radius=10)
        self.table_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 15))
        self.table_frame.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        
        self.setup_table_headers()
 
    def setup_table_headers(self):
        headers = ["Algorithm", "Execution Time (µs)", "Total Distance (km)", "Total Cost (₹)", "Explored Nodes", "Memory Footprint", "Search Efficiency"]
        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.table_frame, 
                text=h, 
                text_color="#00f0ff" if idx == 0 else "#2ec4b6",
                font=ctk.CTkFont(size=11, weight="bold")
            )
            lbl.grid(row=0, column=idx, padx=10, pady=8, sticky="w")
 
    def update_analytics(self, results):
        """
        Refreshes charts with fresh search metrics.
        'results' should be a dict of the form:
        {
          "BFS": {"execution_time_ns": x, "distance": d, "cost": c, ...},
          "DFS": {...},
          ...
        }
        """
        # Clear existing axes
        self.ax_time.clear()
        self.ax_metrics.clear()
        
        # Clear existing table data row widgets (keep headers at row 0)
        for widget in self.table_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
 
        algorithms = ["BFS", "DFS", "UCS", "A* Search"]
        times_us = []
        distances = []
        costs = []
        
        row_idx = 1
        for alg in algorithms:
            data = results.get(alg, {"execution_time_ns": 0.0, "distance": 0.0, "cost": 0.0})
            
            # Convert ns to microseconds for readable charts
            time_us = data["execution_time_ns"] / 1000.0
            times_us.append(time_us)
            
            distances.append(data["distance"])
            costs.append(data["cost"])
            
            # Add metrics to the data table (with rich telemetry)
            ctk.CTkLabel(self.table_frame, text=alg, text_color="#fff", font=ctk.CTkFont(size=11, weight="bold")).grid(row=row_idx, column=0, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{time_us:.2f} µs", text_color="#cbd5e0").grid(row=row_idx, column=1, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{data['distance']:.1f} km", text_color="#cbd5e0").grid(row=row_idx, column=2, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"₹{data['cost']:.1f}", text_color="#cbd5e0").grid(row=row_idx, column=3, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{data.get('nodes_explored', len(data.get('explored', [])))} nodes", text_color="#cbd5e0").grid(row=row_idx, column=4, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{data.get('memory_usage_kb', 0.0):.2f} KB", text_color="#cbd5e0").grid(row=row_idx, column=5, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.table_frame, text=f"{data.get('efficiency', 0.0):.1f}%", text_color="#cbd5e0").grid(row=row_idx, column=6, padx=10, pady=4, sticky="w")
            
            row_idx += 1

        # Plot 1: Execution Time (Lighter cyan color for speed)
        bars_time = self.ax_time.bar(algorithms, times_us, color='#00f0ff', width=0.5, edgecolor='#121212', linewidth=1)
        self.ax_time.set_title("Search Execution Time Speed (Lower is Better)", fontsize=11, color='#00f0ff', pad=10)
        self.ax_time.set_ylabel("Time (Microseconds)", color='#cbd5e0', fontsize=9)
        self.ax_time.tick_params(colors='#a0aec0', labelsize=8)
        self.ax_time.set_facecolor('#1e1e24')
        self.ax_time.grid(axis='y', linestyle='--', alpha=0.3)
        
        # Label bars with values
        for bar in bars_time:
            yval = bar.get_height()
            self.ax_time.text(
                bar.get_x() + bar.get_width()/2.0, 
                yval + max(1, yval*0.05), 
                f"{yval:.1f}µs", 
                ha='center', 
                va='bottom', 
                color='#fff', 
                fontsize=7
            )

        # Plot 2: Distance vs Cost Dual Bar Chart
        x_indices = range(len(algorithms))
        width = 0.35
        
        bars_dist = self.ax_metrics.bar([x - width/2 for x in x_indices], distances, width, label='Distance (km)', color='#2ec4b6')
        
        # Create second y-axis for cost
        ax_cost = self.ax_metrics.twinx()
        bars_cost = ax_cost.bar([x + width/2 for x in x_indices], costs, width, label='Cost (₹)', color='#ecc94b')
        
        self.ax_metrics.set_title("Path Optimization Efficiency Comparison", fontsize=11, color='#2ec4b6', pad=10)
        self.ax_metrics.set_xticks(x_indices)
        self.ax_metrics.set_xticklabels(algorithms)
        self.ax_metrics.set_ylabel("Distance (km)", color='#2ec4b6', fontsize=9)
        ax_cost.set_ylabel("Travel Cost (INR)", color='#ecc94b', fontsize=9)
        
        self.ax_metrics.tick_params(colors='#a0aec0', labelsize=8)
        ax_cost.tick_params(colors='#a0aec0', labelsize=8)
        self.ax_metrics.set_facecolor('#1e1e24')
        
        # Combine legends
        lines = [bars_dist, bars_cost]
        labels = [l.get_label() for l in lines]
        self.ax_metrics.legend(lines, labels, loc='upper left', fontsize=7, facecolor='#12121a')

        # Redraw
        self.canvas.draw()
        self.fig.savefig(os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports", "comparison_chart.png"), dpi=200, facecolor='#121212')
