FROM python:3.8.10

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y ffmpeg && pip uninstall youtube_dl -y && pip install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl

CMD [ "python3", "main.py"]