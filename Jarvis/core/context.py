class ExecutionContext:

    def __init__(self):
        self.dev_mode: bool = False

    def grant(self, perm):
        self.permissions.add(perm)

    def revoke(self, perm):
        self.permissions.discard(perm)

    def has(self, perm):
        return perm in self.permissions
        