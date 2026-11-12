# multi stage so that changing the code doesnt do a cache miss
FROM node:24-slim AS assets
WORKDIR /build/static
COPY hanfor/static/package*.json ./
RUN npm install
COPY hanfor/ /build/
RUN npm run build

FROM python:3.13-slim
WORKDIR /app
COPY hanfor/requirements.txt ./
COPY hanfor/lib_pea/requirements.txt lib_pea/
RUN pip install --no-cache-dir -r requirements.txt \
 && pysmt-install --z3 --confirm-agreement
# always install before copying to not cause a cache miss and reinstall every time
COPY hanfor/ ./
COPY --from=assets /build/static/dist ./static/dist
# add your config files here
COPY hanfor/config.dist.py config.py
COPY hanfor/configuration/ai_config.dist.py configuration/ai_config.py
COPY hanfor/configuration/threading_config.dist.py configuration/threading_config.py
COPY hanfor/configuration/ultimate_config.dist.py configuration/ultimate_config.py

# run the entrypoint 
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENV HANFOR_HOST=0.0.0.0 HANFOR_PORT=5000
EXPOSE 5000
VOLUME /app/data
ENTRYPOINT ["/entrypoint.sh"]
