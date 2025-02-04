from aiohttp import ClientSession

class HTTPSessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.session = ClientSession()
        return cls._instance

    async def close(self):
        await self.session.close()