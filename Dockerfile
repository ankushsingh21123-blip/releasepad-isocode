FROM node:22-alpine AS webbuild
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY vite.config.ts ./
COPY web ./web
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 releasepad && mkdir /data && chown releasepad:releasepad /data
COPY api ./api
COPY run_server.py ./run_server.py
COPY --from=webbuild /build/static ./static
ENV RELEASEPAD_DB=/data/releasepad.sqlite
ENV PORT=4182
USER releasepad
EXPOSE 4182
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:'+__import__('os').environ.get('PORT','4182')+'/api/health',timeout=3)"
CMD ["python", "run_server.py"]
