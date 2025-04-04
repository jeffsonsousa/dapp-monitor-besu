# Imagem base
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Copia o script e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY exporter.py .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "exporter:app"]

