from supabase import create_client, Client
from config.settings import Config

class SupabaseClient:
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_SERVICE_KEY
            )
            print("✅ Supabase client initialized")
        return cls._instance
    
    @property
    def client(self) -> Client:
        return self._client

# Singleton instance
supabase_client = SupabaseClient().client
