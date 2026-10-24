from time import monotonic


class SessionLockController:
    def __init__(self, timeout_seconds=900, lock_on_minimize=False):
        self.timeout_seconds = max(1, int(timeout_seconds))
        self.lock_on_minimize = bool(lock_on_minimize)
        self.last_activity = monotonic()
        self.locked = False

    def record_activity(self):
        if not self.locked:
            self.last_activity = monotonic()

    def check_timeout(self, now=None):
        if not self.locked and (now or monotonic()) - self.last_activity >= self.timeout_seconds:
            self.locked = True
        return self.locked

    def handle_minimized(self):
        if self.lock_on_minimize:
            self.locked = True
        return self.locked

    def unlock(self, authenticated):
        if self.locked and authenticated:
            self.locked = False
            self.record_activity()
            return True
        return not self.locked

    def lock(self):
        self.locked = True
