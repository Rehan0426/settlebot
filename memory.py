import time

class SessionMemory:
    def __init__(self, ttl_seconds=3600):
        self.history = []
        self.last_referenced_transaction_id = None
        self.last_referenced_date_range = None
        self.last_updated = time.time()
        self.ttl = ttl_seconds

    def add_turn(self, user_msg, bot_msg):
        self.history.append({"role": "user", "text": user_msg})
        self.history.append({"role": "assistant", "text": bot_msg})
        if len(self.history) > 20:
            self.history = self.history[-20:]
        self.last_updated = time.time()

    def update_slots(self, transaction_id=None, date_range=None):
        if transaction_id:
            self.last_referenced_transaction_id = transaction_id
        if date_range:
            self.last_referenced_date_range = date_range
        self.last_updated = time.time()

class MemoryManager:
    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id):
        now = time.time()
        stale = [sid for sid, sess in self.sessions.items() if now - sess.last_updated > sess.ttl]
        for sid in stale:
            del self.sessions[sid]
            
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory()
        return self.sessions[session_id]

memory_manager = MemoryManager()
