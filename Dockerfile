FROM ubuntu
WORKDIR /
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /app/venv
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["/app/venv/bin/python", "main.py"]
