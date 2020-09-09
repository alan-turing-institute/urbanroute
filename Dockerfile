# Use an official Python runtime as a parent image
FROM python:3.8

WORKDIR /app

# copy source code
COPY $CLEANAIR /app/cleanair
COPY routex /app/routex
COPY urbanroute /app/urbanroute
COPY entrypoints /app/entrypoints

# Install any needed packages specified in setup.py
# TODO get the below line to work to install cleanair
RUN pip install "git+https://github.com/alan-turing-institute/clean-air-infrastructure.git/#egg=pkg&subdirectory=containers/cleanair"
RUN pip install /app/routex
RUN pip install /app/urbanroute

# run the entrypoint
ENTRYPOINT [ "python", "entrypoints/main.py" ]
