class MemoryPolicy:
    @staticmethod
    def can_write(explicit_user_request: bool) -> bool:
        return explicit_user_request