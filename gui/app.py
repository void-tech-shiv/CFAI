import customtkinter as ctk
import tkinter as tk
from models.user import User
from models.location import TouristGraph
from gui.auth_frame import AuthFrame
from gui.dashboard_frame import DashboardFrame
from gui.stats_frame import StatsFrame

class TouristRouteApp(ctk.CTk):
    """
    Main application shell orchestrating frames, transitions, tabs, and styling themes.
    """
    def __init__(self):
        super().__init__()
        
        # Configure Main Window
        self.title("AI Tourist Route Planner - Academic Edition")
        self.geometry("1100x720")
        self.minsize(1050, 680)
        
        # Set Dark Mode default theme (Obsidian styling)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State variables
        self.current_user = None
        self.graph = TouristGraph()
        
        # Core Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        self.auth_frame = None
        self.main_app_frame = None
        
        # Start by showing the login page
        self.show_auth_screen()

    def show_auth_screen(self):
        """Displays login/registration frame."""
        if self.main_app_frame:
            self.main_app_frame.destroy()
            
        self.auth_frame = AuthFrame(self.container, on_login_success=self.on_login_success)
        self.auth_frame.pack(fill="both", expand=True)

    def on_login_success(self, user):
        """Callback executed on successful user login."""
        self.current_user = user
        self.auth_frame.destroy()
        
        # Setup main dashboard shell
        self.setup_main_application()

    def setup_main_application(self):
        """Creates tabbed main workspace after registration or login."""
        self.main_app_frame = ctk.CTkFrame(self.container, fg_color="#121212")
        self.main_app_frame.pack(fill="both", expand=True)
        
        # 1. TOP HEADER NAVIGATION BAR
        self.header = ctk.CTkFrame(self.main_app_frame, height=50, fg_color="#1e1e24", border_color="#2e2e3f", border_width=1, corner_radius=0)
        self.header.pack(fill="x", side="top")
        
        # Header title
        self.logo_lbl = ctk.CTkLabel(
            self.header, 
            text="✨ RAJASTHAN TOURIST AI ROUTER", 
            text_color="#00f0ff", 
            font=ctk.CTkFont(family="Inter", size=15, weight="bold")
        )
        self.logo_lbl.pack(side="left", padx=15, pady=10)
        
        # Logged-in user badge
        self.user_lbl = ctk.CTkLabel(
            self.header, 
            text=f"👤 Tourist: {self.current_user.username}", 
            text_color="#cbd5e0", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.user_lbl.pack(side="left", padx=20, pady=10)

        # Log Out Button
        self.logout_btn = ctk.CTkButton(
            self.header, 
            text="LOG OUT", 
            command=self.handle_logout, 
            fg_color="transparent", 
            hover_color="#ff5252", 
            text_color="#a0aec0", 
            width=80,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.logout_btn.pack(side="right", padx=15, pady=10)

        # Dark Mode/Light Mode toggle switch
        self.theme_switch_var = ctk.StringVar(value="dark")
        self.theme_switch = ctk.CTkSwitch(
            self.header, 
            text="Dark Theme", 
            command=self.toggle_theme, 
            variable=self.theme_switch_var, 
            onvalue="dark", 
            offvalue="light",
            text_color="#a0aec0"
        )
        self.theme_switch.pack(side="right", padx=15, pady=10)
        
        # 2. MAIN TABBED DISPLAY WINDOW
        self.tab_view = ctk.CTkTabview(
            self.main_app_frame, 
            fg_color="#121212", 
            segmented_button_fg_color="#1e1e24",
            segmented_button_selected_color="#2ec4b6",
            segmented_button_selected_hover_color="#00adb5",
            segmented_button_unselected_color="#12121a",
            segmented_button_unselected_hover_color="#20202e",
            text_color="#fff"
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tab_view.add("MAP RUNNER & DASHBOARD")
        self.tab_view.add("ALGORITHM SPEED ANALYSIS")
        self.tab_view.add("SEARCH HISTORY LOG")
        
        # Embed frames inside respective tabs
        # Tab 1: Map Planning Dashboard
        self.dashboard_tab = DashboardFrame(self.tab_view.tab("MAP RUNNER & DASHBOARD"), self.graph, self.current_user)
        self.dashboard_tab.pack(fill="both", expand=True)
        
        # Hook up route computation triggers to auto-update analysis comparisons in Tab 2
        original_pipeline_func = self.dashboard_tab.execute_ai_pipeline
        
        def pipeline_wrapper():
            # Run original A* routing
            original_pipeline_func()
            
            # Immediately run BFS, DFS, UCS, A* search comparisons using the same inputs to populate Tab 2
            start_name = self.dashboard_tab.start_dropdown.get()
            goal_name = self.dashboard_tab.goal_dropdown.get()
            
            start_id = next(loc.id for loc in self.graph.get_all_locations() if loc.name == start_name)
            goal_id = next(loc.id for loc in self.graph.get_all_locations() if loc.name == goal_name)
            
            if start_id != goal_id:
                # Capture weights
                weights = {
                    "distance": self.dashboard_tab.w_dist_slider.get(),
                    "cost": self.dashboard_tab.w_cost_slider.get(),
                    "time": self.dashboard_tab.w_traffic_slider.get(),
                    "rating": self.dashboard_tab.w_rating_slider.get()
                }
                
                # Fetch search executions metrics with distinct, diverse native optimization metrics
                bfs_res = self.dashboard_tab.searcher.bfs(start_id, goal_id)
                dfs_res = self.dashboard_tab.searcher.dfs(start_id, goal_id)
                ucs_res = self.dashboard_tab.searcher.ucs(start_id, goal_id, metric_type="cost", utility_weights=weights)
                astar_res = self.dashboard_tab.searcher.a_star(start_id, goal_id, metric_type="utility", heuristic_type="euclidean", utility_weights=weights)
                
                comparison_metrics = {
                    "BFS": bfs_res,
                    "DFS": dfs_res,
                    "UCS": ucs_res,
                    "A* Search": astar_res
                }
                
                # Update analytics canvas
                self.stats_tab.update_analytics(comparison_metrics)
                
                # Update search log tab
                self.update_history_log()
                
        self.dashboard_tab.plan_btn.configure(command=pipeline_wrapper)
        
        # Tab 2: Analytics graphs
        self.stats_tab = StatsFrame(self.tab_view.tab("ALGORITHM SPEED ANALYSIS"))
        self.stats_tab.pack(fill="both", expand=True)
        
        # Tab 3: Search history log list
        self.history_frame = ctk.CTkFrame(self.tab_view.tab("SEARCH HISTORY LOG"), fg_color="#1e1e24", border_color="#2e2e3f", border_width=1, corner_radius=15)
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            self.history_frame, 
            text="Saved Trip Searches (Stored Locally)", 
            text_color="#00f0ff", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, pady=10, padx=15, sticky="w")

        self.history_listbox = tk.Listbox(
            self.history_frame, 
            bg="#12121a", 
            fg="#cbd5e0", 
            font=("Consolas", 10), 
            selectbackground="#2ec4b6",
            selectforeground="#121212", 
            relief="flat",
            borderwidth=0
        )
        self.history_listbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))
        
        self.update_history_log()

    def update_history_log(self):
        """Reloads historical search logs into history log view listbox."""
        if not hasattr(self, 'history_listbox') or not self.current_user:
            return
            
        self.history_listbox.delete(0, tk.END)
        # Load user history
        history = self.current_user.search_history
        if not history:
            self.history_listbox.insert(tk.END, " No searches found yet. Plan a trip route on the map tab to get started!")
            return
            
        for index, item in enumerate(reversed(history)):
            self.history_listbox.insert(
                tk.END, 
                f" [{index + 1}] FROM: {item['start']}  -->  TO: {item['destination']}  |  "
                f"ALG: {item['algorithm']}  |  DIST: {item['distance']:.1f}km  |  "
                f"COST: ₹{item['cost']:.1f}"
            )

    def toggle_theme(self):
        """Switches theme between dark mode (obsidian) and light mode."""
        theme = self.theme_switch_var.get()
        if theme == "dark":
            ctk.set_appearance_mode("dark")
            self.header.configure(fg_color="#1e1e24")
            self.main_app_frame.configure(fg_color="#121212")
        else:
            ctk.set_appearance_mode("light")
            self.header.configure(fg_color="#e2e8f0")
            self.main_app_frame.configure(fg_color="#f7fafc")

    def handle_logout(self):
        """Resets credentials and goes back to authentication page."""
        self.current_user = None
        self.show_auth_screen()
