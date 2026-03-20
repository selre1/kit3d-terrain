FROM ghcr.io/tum-gis/ctb-quantized-mesh:latest AS ctb-runtime

RUN set -eux; \
  mkdir -p /opt/ctb/bin /opt/ctb/libs /opt/ctb/share; \
  cp /usr/local/bin/ctb-tile /opt/ctb/bin/ctb-tile; \
  ldd /usr/local/bin/ctb-tile \
    | awk '{print $3}' \
    | grep '^/' \
    | grep -Ev '/(libc\.so|libpthread\.so|libdl\.so|librt\.so|libm\.so|libgcc_s\.so|libstdc\+\+\.so|ld-linux-x86-64\.so)' \
    | sort -u \
    | xargs -r -I{} cp -L {} /opt/ctb/libs/; \
  cp -a /usr/share/gdal /opt/ctb/share/; \
  cp -a /usr/share/proj /opt/ctb/share/

FROM python:3.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates tzdata \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ctb-runtime /opt/ctb/bin/ctb-tile /usr/local/bin/ctb-tile-bin
COPY --from=ctb-runtime /opt/ctb/libs/ /opt/ctb/libs/
COPY --from=ctb-runtime /opt/ctb/share/ /opt/ctb/share/

RUN printf '%s\n' \
  '#!/bin/sh' \
  'export LD_LIBRARY_PATH=/opt/ctb/libs${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}' \
  'export GDAL_DATA=/opt/ctb/share/gdal' \
  'export PROJ_LIB=/opt/ctb/share/proj' \
  'exec /usr/local/bin/ctb-tile-bin "$@"' \
  > /usr/local/bin/ctb-tile \
  && chmod +x /usr/local/bin/ctb-tile

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY worker ./worker

RUN mkdir -p /data/assets /data/log/terrain

CMD ["sh", "-c", "celery -A worker.celery_app worker -l info -E -Q ${CELERY_QUEUE} -P prefork --autoscale=${CELERY_AUTOSCALE}"]
