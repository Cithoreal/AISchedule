import os
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
from datasets import load_dataset
from pydub import AudioSegment

device = "cpu"
torch_dtype = torch.float32

model_id = "openai/whisper-large-v3"
directory = "/home/Cithoreal/Nextcloud/Documents/Audio Journals/"
unprocessed = directory + "Unprocessed/"
processed = directory + "Processed/"
transcription_directory = directory + "Transcriptions/Unprocessed/"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=30,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)

dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")

def convert_m4a_to_mp3(input_file, output_file):
    audio = AudioSegment.from_file(input_file, "m4a")
    audio.export(output_file, format="mp3")
    os.remove(input_file)


#Transcribe the audio file and write the transcription to a text file with the same name
def transcribe_audio(file_name):
    print(file_name)
    #Get the name of the file without the extension and use it to name the transcription file
    result = pipe(unprocessed + file_name)  
    with open(transcription_directory + file_name[:-4] + ".txt", "w") as f:
        f.write(result["text"])

#Loop through each file in the directory and transcribe it, when finished move the file to the processed folder
for filename in os.listdir(unprocessed):
    if filename.endswith(".m4a"):
        #Convert the m4a file to an mp3 file
        convert_m4a_to_mp3(unprocessed + filename, unprocessed + filename[:-4] + ".mp3")
        #Get date and timestamp from the file name and use it to name the transcription file
    if filename.endswith(".mp3") or filename.endswith(".wav") or filename.endswith(".flac"):
        transcribe_audio(filename)
        os.rename(unprocessed + filename, processed + filename)
    else:
        continue
