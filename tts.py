import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

# Check if CUDA is available, otherwise use CPU
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Load ParlerTTS model and tokenizer
model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-large-v1").to(device)
tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-large-v1")

# Define the prompt (what to say) and the description (how to say it)
prompt = "Hey, how are you doing today?"
description = "A female speaker delivers a slightly expressive and animated speech with a moderate speed and pitch. The recording is of very high quality, with the speaker's voice sounding clear and very close up."

# Tokenize the description and prompt
input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
prompt_input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

# Generate the audio output
generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)

# Convert the generated output to a NumPy array and save as a .wav file
audio_arr = generation.cpu().numpy().squeeze()
sf.write("parler_tts_out.wav", audio_arr, model.config.sampling_rate)

print(f"Audio file saved as 'parler_tts_out.wav'")
