FROM cnstark/pytorch:1.10.1-py3.9.12-cuda11.1.1-devel-ubuntu20.04

# Install installation dependencies
RUN apt-get update -y && \
    apt-get install -y vim wget git zip htop screen build-essential

RUN git clone https://github.com/sarmientoj24/youtube_summarizer.git /app/youtube_summarizer

WORKDIR /app/youtube_summarizer
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt
RUN python setup_whisper.py
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]