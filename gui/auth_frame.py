import customtkinter as ctk
from models.user import User

class AuthFrame(ctk.CTkFrame):
    """
    GUI Frame for User Authentication (Login & Registration).
    Uses a beautiful glassmorphism-style modern design.
    """
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="#121212")
        self.on_login_success = on_login_success
        
        # Configure Grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Container for login card
        self.card = ctk.CTkFrame(self, width=420, height=520, fg_color="#1e1e24", border_color="#2ec4b6", border_width=1, corner_radius=15)
        self.card.grid(row=0, column=0, padx=20, pady=20)
        self.card.grid_propagate(False)
        
        # Configure card layout
        self.card.grid_columnconfigure(0, weight=1)
        
        self.mode = "login"  # "login" or "register"
        self.setup_ui()

    def setup_ui(self):
        # Clear card elements first
        for widget in self.card.winfo_children():
            widget.destroy()

        # Logo Title
        self.title_lbl = ctk.CTkLabel(
            self.card, 
            text="ROUTE PLANNER AI", 
            text_color="#00f0ff", 
            font=ctk.CTkFont(family="Inter", size=26, weight="bold")
        )
        self.title_lbl.grid(row=0, column=0, pady=(40, 5))
        
        self.sub_lbl = ctk.CTkLabel(
            self.card, 
            text="Please authenticate to continue", 
            text_color="#a0aec0", 
            font=ctk.CTkFont(size=12)
        )
        self.sub_lbl.grid(row=1, column=0, pady=(0, 30))

        # Username entry
        self.user_entry = ctk.CTkEntry(
            self.card, 
            placeholder_text="Username", 
            width=320, 
            height=40,
            fg_color="#12121a",
            border_color="#4a5568",
            text_color="#fff"
        )
        self.user_entry.grid(row=2, column=0, pady=10)

        # Email entry (shown only in register mode)
        if self.mode == "register":
            self.email_entry = ctk.CTkEntry(
                self.card, 
                placeholder_text="Email Address", 
                width=320, 
                height=40,
                fg_color="#12121a",
                border_color="#4a5568",
                text_color="#fff"
            )
            self.email_entry.grid(row=3, column=0, pady=10)
        
        # Password entry
        self.pass_entry = ctk.CTkEntry(
            self.card, 
            placeholder_text="Password", 
            show="*", 
            width=320, 
            height=40,
            fg_color="#12121a",
            border_color="#4a5568",
            text_color="#fff"
        )
        self.pass_entry.grid(row=4, column=0, pady=10)

        # Status / Feedback label
        self.status_lbl = ctk.CTkLabel(
            self.card, 
            text="", 
            text_color="#ff5252", 
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.status_lbl.grid(row=5, column=0, pady=5)

        # Primary Action Button
        action_btn_text = "SIGN IN" if self.mode == "login" else "REGISTER NOW"
        self.action_btn = ctk.CTkButton(
            self.card, 
            text=action_btn_text, 
            command=self.handle_auth_action, 
            width=320, 
            height=45,
            fg_color="#2ec4b6",
            hover_color="#00adb5",
            text_color="#121212",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        self.action_btn.grid(row=6, column=0, pady=(15, 10))

        # Switch Mode Link
        switch_text = "New tourist? Register here." if self.mode == "login" else "Already have an account? Sign in."
        self.switch_btn = ctk.CTkButton(
            self.card, 
            text=switch_text, 
            command=self.toggle_mode, 
            fg_color="transparent", 
            hover_color="#20202e", 
            text_color="#a0aec0",
            font=ctk.CTkFont(size=12, underline=True)
        )
        self.switch_btn.grid(row=7, column=0, pady=(5, 20))

    def toggle_mode(self):
        """Switches between login and registration layouts."""
        self.mode = "register" if self.mode == "login" else "login"
        self.setup_ui()

    def handle_auth_action(self):
        """Processes sign in or registration credentials offline."""
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        
        self.status_lbl.configure(text="")
        
        if self.mode == "login":
            success, result = User.login(username, password)
            if success:
                self.on_login_success(result)  # Pass authenticated User object back
            else:
                self.status_lbl.configure(text=result, text_color="#ff5252")
        else:
            email = self.email_entry.get().strip()
            if not email:
                self.status_lbl.configure(text="Email is required!", text_color="#ff5252")
                return
            success, message = User.register(username, email, password)
            if success:
                self.status_lbl.configure(text="Registered! Redirecting to Sign In...", text_color="#2ec4b6")
                self.after(1500, self.auto_switch_to_login)
            else:
                self.status_lbl.configure(text=message, text_color="#ff5252")

    def auto_switch_to_login(self):
        self.mode = "login"
        self.setup_ui()
