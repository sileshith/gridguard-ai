FROM eclipse-temurin:21-jdk-jammy AS java
FROM python:3.11-slim-bookworm
COPY --from=java /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="/opt/java/openjdk/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/work/src
RUN apt-get update && apt-get install -y --no-install-recommends procps && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY pyproject.toml ./
COPY src ./src
RUN python -m pip install --no-cache-dir '.[test,plots,report]'
COPY . .
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]
