import threading

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

class VoiceGuidanceSystem:
    """
    Offline Text-to-Speech (TTS) Voice Guidance system for routing recommendations.
    Uses a separate thread for non-blocking GUI execution.
    """
    def __init__(self):
        self.engine = None
        self.enabled = True
        
        if TTS_AVAILABLE:
            try:
                # Initialize engine in main or thread
                self.engine = pyttsx3.init()
                # Set speaking rate (words per minute)
                self.engine.setProperty('rate', 150)
                # Set volume (0.0 to 1.0)
                self.engine.setProperty('volume', 0.9)
            except Exception as e:
                print(f"Failed to initialize voice engine: {e}")
                self.engine = None

    def speak(self, text):
        """Speaks the text in a background thread to prevent GUI freezing."""
        if not self.enabled or not self.engine:
            print(f"[Voice System (Disabled)]: {text}")
            return
            
        def _speak_thread():
            try:
                # Re-initialize engine inside the thread to prevent COM multi-threading errors on Windows
                local_engine = pyttsx3.init()
                local_engine.setProperty('rate', 150)
                local_engine.setProperty('volume', 0.9)
                local_engine.say(text)
                local_engine.runAndWait()
            except Exception as e:
                print(f"Error in TTS background thread: {e}")
                
        threading.Thread(target=_speak_thread, daemon=True).start()

    def speak_route(self, path, distance, cost, time_mins, success_prob, start_name, goal_name):
        """Generates a standard tourist routing voice message."""
        stops_count = len(path)
        stops_str = ", then ".join([name.split("(")[0].strip() for name in path[1:]])
        
        message = (
            f"Welcome to the Tourist Route Planner. "
            f"We have computed your optimal route from {start_name.split('(')[0]} to {goal_name.split('(')[0]}. "
            f"The selected route goes through {stops_str}. "
            f"The total physical travel distance is {int(distance)} kilometers. "
            f"The estimated base travel time is {int(time_mins // 60)} hours and {int(time_mins % 60)} minutes. "
            f"The total estimated cost is {int(cost)} rupees. "
            f"The calculated route traversal safety index is {int(success_prob * 100)} percent. "
            f"Have a safe and happy journey!"
        )
        self.speak(message)
