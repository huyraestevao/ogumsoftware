FROM python:3.11-slim

# Instala dependências do sistema, incluindo gmsh
RUN apt-get update && apt-get install -y gmsh && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas os ficheiros de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt requirements-dev.txt ./

# Instala as dependências Python
RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -r requirements-dev.txt

# Copia o resto da aplicação
COPY . .

# Instala o pacote local 'ogum'
RUN pip install -e .

# Expõe as portas para a aplicação e para a API
EXPOSE 8866
EXPOSE 8000
