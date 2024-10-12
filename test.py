import asyncio
import websockets
import base64
import sounddevice as sd
import queue

def audio_callback(indata, frames, time, status, audio_queue):
    if status:
        print(status)
    audio_bytes = indata.tobytes()
    # Base64-encode the audio data
    encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
    # Put the encoded audio in the thread-safe queue
    audio_queue.put(encoded_audio)

async def send_audio(uri):
    audio_queue = queue.Queue()  # Thread-safe queue for the callback
    async_audio_queue = asyncio.Queue()  # Async queue for asyncio tasks

    async def websocket_handler(websocket):
        while True:
            # Wait until audio is put into the asyncio queue
            encoded_audio = await async_audio_queue.get()
            if encoded_audio is None:
                break
            print(encoded_audio)
            await websocket.send(encoded_audio)

    # Continuously move data from thread-safe queue to async queue
    async def queue_transfer():
        while True:
            encoded_audio = await asyncio.to_thread(audio_queue.get)
            await async_audio_queue.put(encoded_audio)

    # Configure audio stream
    sample_rate = 24000
    channels = 1
    dtype = 'int16'
    chunk_duration = 1  # in seconds

    async with websockets.connect(uri) as websocket:
        # Start the audio stream in a separate thread
        with sd.InputStream(samplerate=sample_rate, channels=channels, dtype=dtype,
                            callback=lambda indata, frames, time, status: audio_callback(indata, frames, time, status, audio_queue),
                            blocksize=int(sample_rate * chunk_duration)):
            print("Start speaking...")

            # Start background tasks for handling audio and websocket
            websocket_task = asyncio.create_task(websocket_handler(websocket))
            queue_transfer_task = asyncio.create_task(queue_transfer())
            
            await asyncio.Future()  # Keep running until interrupted

            # Signal the websocket handler and queue transfer to stop
            await async_audio_queue.put(None)
            await websocket_task
            queue_transfer_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(send_audio('ws://192.168.1.9:8765'))
    except KeyboardInterrupt:
        print("Client interrupted.")
