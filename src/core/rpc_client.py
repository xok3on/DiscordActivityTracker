# src/core/rpc_client.py
from pypresence import Presence
import time

class DiscordRPCClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.rpc = None
        self.start_time = time.time()

    def connect(self):
        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            print("[RPC] Успешно подключено к Discord RPC")
        except Exception as e:
            print(f"[RPC] Ошибка подключения: {e}")
            self.rpc = None

    def update_presence(self, details: str, state: str, large_image: str = "chrome"):
        if not self.rpc:
            return
        try:
            self.rpc.update(
                details=details[:128],
                state=state[:128],
                start=self.start_time,
                large_image=large_image
            )
        except Exception as e:
            print(f"[RPC] Ошибка обновления статуса: {e}")
            
