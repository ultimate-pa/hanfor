# Main stage for hanfor.
FROM python:3.7-slim
LABEL maintainer="Breee@github"
WORKDIR /usr/src/app

# copy requirements the reduce layersize.
COPY hanfor/requirements.txt /usr/src/app/requirements.txt

# Install required system packages + python requirements + cleanup in one layer (yields smaller docker image).
# If you try to debug the build you should split into single RUN commands ;)
RUN export DEBIAN_FRONTEND=noninteractive && apt-get update \
&& apt-get install -y --no-install-recommends \
build-essential \
# python reqs
&& python3 -m pip install --no-cache-dir -r requirements.txt \
# cleanup
&& apt-get remove -y build-essential \
# Remove f*** python2.7 from the 3.7 image, why is that even a thing.
&& apt-get remove -y python2.7 && rm -rf /usr/lib/python2.7 \
# Purge autoremove, but keep recommends which are important.
&& apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
# delete apt cache
&& rm -rf /var/lib/apt/lists/*

# Copy hanfor + entrypoint.
COPY hanfor /usr/src/app
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Change if you expose Hanfor on another port.
EXPOSE 5000
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]