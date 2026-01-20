FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y curl gdal-bin just unzip p7zip-full
RUN curl -L -o /tmp/wbt.zip https://www.whiteboxgeo.com/WBT_Linux/WhiteboxTools_linux_amd64.zip \
    && unzip /tmp/wbt.zip -d /tmp/wbt\
    && mv /tmp/wbt/WhiteboxTools_linux_amd64/WBT /opt\
    && chmod +x /opt/WBT/whitebox_tools\
    && rm -rf /tmp/wbt.zip /tmp/wbt
RUN uv sync

ENV PATH="/opt/WBT:${PATH}"

CMD ["just", "garonne"]
