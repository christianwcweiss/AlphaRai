# syntax=docker/dockerfile:1
FROM docker
COPY --from=docker/buildx-bin:latest /buildx /usr/libexec/docker/cli-plugins/docker-buildx
RUN docker buildx version

FROM public.ecr.aws/sam/build-python3.11:latest

ARG requirements_filter
VOLUME /mnt
WORKDIR /tmp

RUN if [ -n "$http_proxy" ]; then \
    git clone https://github.com/bryanpkc/corkscrew.git \
    && cd corkscrew \
    && git -c advice.detachedHead=false checkout -m master \
    && autoreconf --install \
    && ./configure \
    && make \
    && make install; \
    fi

COPY requirements.txt /tmp/

RUN grep -Ev "$requirements_filter" requirements.txt > pypi_requirements.txt || true
RUN grep -E "$requirements_filter" requirements.txt > git_requirements.txt || true

RUN python -m pip install -r pypi_requirements.txt --target /tmp/python/
RUN --mount=type=ssh python -m pip install -r git_requirements.txt --target /tmp/python/

#RUN python -m compileall -b /tmp/python/  TODO: CDHX-33213 uncomment this line
RUN find /tmp/python/ -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
#RUN find /tmp/python/ -type f -a -name '*.py' -print0 | xargs -0 rm -f  TODO: CDHX-33213 uncomment this line
RUN zip -X -q -r1 /tmp/dependencies.zip python
RUN chmod 666 /tmp/dependencies.zip

ENTRYPOINT ["mv", "/tmp/dependencies.zip", "/mnt/dependencies.zip"]
