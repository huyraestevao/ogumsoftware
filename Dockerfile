# 1. Usar a imagem oficial do FEniCS, que ja inclui dolfinx, gmsh e todas as suas dependencias de sistema.
FROM dolfinx/dolfinx:v0.8.0

# 2. Definir o diretorio de trabalho dentro do container.
WORKDIR /app

# 3. Copiar os ficheiros de requisitos para aproveitar o cache do Docker.
COPY requirements.txt requirements-dev.txt ./

# 4. Instalar as nossas dependencias Python (o dolfinx JA ESTA na imagem).
#    Usamos python3, que e o comando padrao nesta imagem.
RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && python3 -m pip install --no-cache-dir -r requirements-dev.txt

# 5. Copiar o codigo da nossa aplicacao para o container.
COPY . .

# 6. Instalar o nosso pacote 'ogum' localmente para que possa ser importado.
RUN python3 -m pip install --no-cache-dir -e .

# 7. Expor as portas para a aplicacao Voila e para a API.
EXPOSE 8866
EXPOSE 8000
