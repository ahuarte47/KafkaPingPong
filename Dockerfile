# =============================================================================
# This Dockerfile implements a Container to run the PingPong service.
#
# @Build:
#  docker build -f ./Dockerfile -t pingpong/dummyapp:1.0.0 .
#  docker image rmi pingpong/dummyapp:1.0.0
#
# @Usage:
#  docker run --rm --name pp pingpong/dummyapp:1.0.0 [--service_role=] [--service_impl=] [--bootstrap_server=]
#  -> service_role: Choose between "producer", "validator", "reader"
#  -> service_impl: Choose between "kafka", "confluent", "dummy"
#
# For interactive process:
#  docker run --rm -it --entrypoint "bash" pingpong/dummyapp:1.0.0
#
# @Info:
#  Yes, I am doing bad things, I am sharing the "service.py"
#  file for different needs.
#
#  For doing simple this demo, I implement all logic in one unique
#  "service.py" file that runs in all cases on the same unique Docker
#  image.
#
#  In a real project, each component (e.g. services that send messages,
#  run geoworkflows, write outputs, ...) will have different dependencies,
#  python libraries and probably will run on different Docker images.
#
#  The entrypoint "service.py" accepts settings from two ways, command line
#  parameters and environment variables (The Helm chart configures the
#  application using environment variables).
#
# =============================================================================

FROM python:3.9.12-slim
LABEL maintainer="XYZ <xyz@mycompany.com>"

RUN echo "INFO: This Container provides Python!"

# Copy source code.
WORKDIR /app
COPY ./pingpong /app/pingpong
COPY ./requirements.txt /app

# Clean existing "__pycache__" directories.
RUN find . -name "__pycache__" -type d -prune -exec rm -rf '{}' +

# Install python dependencies.
RUN pip3 install --no-cache-dir --requirement requirements.txt

# Create a non-root user and adds permissions.
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Set entrypoint.
ENTRYPOINT ["python", "-u", "pingpong/service_app.py"]
