import json
import os
import hashlib

class User:
    """
    OOP class representing a User in the system.
    Handles registration, secure login verification, and profile logging.
    """
    USER_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets", "users.json")

    def __init__(self, username, email, hashed_password, search_history=None):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.search_history = search_history if search_history is not None else []

    @staticmethod
    def _hash_password(password):
        """Hashes the password using SHA-256 for secure local storage."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @classmethod
    def load_all_users(cls):
        """Loads all users from the local JSON database."""
        if not os.path.exists(cls.USER_DB_PATH):
            return {}
        try:
            with open(cls.USER_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                users = {}
                for item in data:
                    users[item['username']] = cls(
                        username=item['username'],
                        email=item['email'],
                        hashed_password=item['password'],
                        search_history=item.get('search_history', [])
                    )
                return users
        except Exception:
            return {}

    @classmethod
    def save_all_users(cls, users_dict):
        """Saves all users back to the local JSON database."""
        data = []
        for user in users_dict.values():
            data.append({
                "username": user.username,
                "email": user.email,
                "password": user.hashed_password,
                "search_history": user.search_history
            })
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(cls.USER_DB_PATH), exist_ok=True)
        with open(cls.USER_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def register(cls, username, email, password):
        """
        Registers a new user.
        Returns (success_status, message).
        """
        username = username.strip()
        email = email.strip()
        if not username or not email or not password:
            return False, "All fields are required!"
        
        users = cls.load_all_users()
        if username in users:
            return False, "Username already exists!"
        
        hashed = cls._hash_password(password)
        new_user = cls(username, email, hashed)
        users[username] = new_user
        cls.save_all_users(users)
        return True, "Registration successful!"

    @classmethod
    def login(cls, username, password):
        """
        Verifies login credentials.
        Returns (success_status, user_obj_or_error_message).
        """
        username = username.strip()
        if not username or not password:
            return False, "Username and password required!"
        
        users = cls.load_all_users()
        if username not in users:
            return False, "Username does not exist!"
        
        user = users[username]
        hashed_attempt = cls._hash_password(password)
        if user.hashed_password == hashed_attempt:
            return True, user
        else:
            return False, "Incorrect password!"

    def add_search_log(self, start, destination, algorithm, path, cost, distance):
        """Saves a search query and its output into the user's history."""
        log_entry = {
            "start": start,
            "destination": destination,
            "algorithm": algorithm,
            "path": path,
            "cost": cost,
            "distance": distance
        }
        self.search_history.append(log_entry)
        
        # Save to database
        users = self.load_all_users()
        if self.username in users:
            users[self.username].search_history = self.search_history
            self.save_all_users(users)
