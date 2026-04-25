import threading

class KillSwitch:
    def __init__(self, agent):
        self.agent = agent
        self.engaged = False
        self._triggered = False
        self.lock = threading.Lock()

    def trigger(self):
        with self.lock:
            self.engaged = True
            self._triggered = True
        print("[KillSwitch] ENGAGED - Agent terminating...")

    def reset(self):
        with self.lock:
            self.engaged = False
        print("[KillSwitch] Reset - Kill switch deactivated")

    def is_triggered(self):
        with self.lock:
            return self._triggered

    def force_terminate(self):
        self.trigger()
        print("[KillSwitch] Force terminate complete.")