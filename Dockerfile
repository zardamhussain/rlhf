FROM python:3.10-bullseye

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "streamlit run main.py"]