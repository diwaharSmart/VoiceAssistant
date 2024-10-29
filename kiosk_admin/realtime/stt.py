import asyncio
import websockets
import aiohttp

class RealTimeTranscriber:
    def __init__(self, assembly_api_key):
        self.api_key = assembly_api_key
        self.assembly_url = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
        self.session = aiohttp.ClientSession()
        self.ws = websockets.connect(
            self.assembly_url,
            extra_headers={"Authorization": self.api_key},
        )

    async def stream_audio(self, audio_generator):
        async for audio_data in audio_generator:
            await self.ws.send(audio_data)
            response = await self.ws.recv()
            print("Received text:", response)
            yield response
        
