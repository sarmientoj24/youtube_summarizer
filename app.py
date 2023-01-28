import os
import re

import streamlit as st
import whisper

from summarizer import generate_summary
from youtube import YoutubeDownloader

# Variables
REGEX = "^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$"
DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloads")
DEFAULT_THUMB = os.path.join(os.getcwd(), "assets", "default-thumb.png")
MAX_DURATION = 720
WHISPER_MODEL = "medium.en"
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), ".cache")


# Functions
def transcribe_audio(model, filename, verbose=False, fp16=True, language="en"):
    result = model.transcribe(filename, verbose=verbose, fp16=fp16, language=language)
    return result["text"]


@st.cache()
def load_application_model(model_name=WHISPER_MODEL):
    model = whisper.load_model(model_name, download_root=DOWNLOAD_DIR)
    return model


# Load whisper model
model = load_application_model()

# UI
st.title("Youtube Summarizer")
st.header("Summarize Youtube Audio")
st.text("By James Andrew")
st.info("Maximum Video Length is 12 mins (for now). Please do not spam.", icon="🤖")

url = st.text_input("Youtube URL", "")
summary = st.selectbox("Length of Summary", ("Short", "Long"))

# Submit
if st.button("Submit"):
    # Get Length of summary
    if summary == "Short":
        tokens = 80
    else:
        tokens = 120

    if url and re.match(REGEX, url):
        # Youtube Retrieval
        ytd = YoutubeDownloader(url, DOWNLOAD_PATH)

        if ytd.duration > MAX_DURATION:
            st.error("Exceeded 12 minutes! Please submit a shorter video.")

        else:
            title = ytd.title
            ecode1, thumbnail = ytd.get_video_thumbnail()
            thumbnail = (
                thumbnail
                if ecode1 == 0 and os.path.isfile(thumbnail)
                else DEFAULT_THUMB
            )

            # Display info
            st.header(title)
            st.image(thumbnail, width=480)

            # Dowloading
            with st.spinner("Downloading and converting to audio..."):
                ecode2, audio_path = ytd.download_video_to_mp3()

            if ecode2 != 0:
                st.error(
                    "Failed on encoding! Either resumbit or select a different video. Sorry!"
                )
            else:
                # Transcribe Audio
                with st.spinner("Transcribing audio. May take a minute..."):
                    transcription = transcribe_audio(model, audio_path)

                # Summarize
                with st.spinner("Summarizing..."):
                    summarized_text = generate_summary(transcription, max_length=tokens)

                st.header("Summary")
                st.markdown(summarized_text)
    else:
        st.warning("Please add a valid Youtube Link!")
