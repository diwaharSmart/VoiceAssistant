import websockets
import asyncio
import json

class AssemblyAIWebSocket:
    def __init__(self, api_key, sample_rate=16000, on_final_transcript=None,on_partial_transcript=None):
        self.api_key = api_key
        self.url = f'wss://api.assemblyai.com/v2/realtime/ws?sample_rate={sample_rate}&language_code=es'
        self.ws = None
        self.on_final_transcript = on_final_transcript  # Callback for final transcripts
        self.on_partial_transcript = on_partial_transcript  # Callback for on_partial_transcript

    async def connect(self):
        """Establish WebSocket connection."""
        try:
            self.ws = await websockets.connect(
                self.url,
                extra_headers={'Authorization': self.api_key}
            )
            print("WebSocket connection established")
            asyncio.create_task(self._receive_final_transcriptions())
        except Exception as e:
            print(f"Failed to connect to AssemblyAI: {e}")

    async def _receive_final_transcriptions(self):
        """Listen for final transcriptions from AssemblyAI and pass them to the callback."""
        try:
            while self.ws:
                message = await self.ws.recv()
                transcription = json.loads(message)
                # Check if the transcription is final
                if transcription.get("message_type") == "PartialTranscript":
                    if len(transcription.get("text", ""))>2:
                        print(transcription.get("text", ""))
                        if self.on_partial_transcript:
                            await self.on_partial_transcript()

                if transcription.get("message_type") == "FinalTranscript":
                    final_text = transcription.get("text", "")
                    print(f"Final Transcript: {final_text}")
                    # Call the callback if defined
                    
                    if self.on_final_transcript:
                        await self.on_final_transcript(final_text)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed with error: {e}")
        except Exception as e:
            print(f"Error receiving transcription: {e}")

    async def send_audio_byte_to_assembly_ai(self, audio_bytes):
        """Send externally received audio data to AssemblyAI."""
        try:
            if self.ws is None:
                print("WebSocket is not connected. Call `connect()` first.")
                return
            await self.ws.send(audio_bytes)
            # print("Audio bytes sent to AssemblyAI.")
        except websockets.ConnectionClosed as e:
            print(f"Connection closed while sending data: {e}")
        except Exception as e:
            print(f"Error sending audio data: {e}")

    async def close(self):
        """Close the WebSocket connection."""
        if self.ws:
            await self.ws.close()
            print("WebSocket connection closed.")