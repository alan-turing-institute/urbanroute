# Use an official Python runtime as a parent image
FROM python:3.8

# set working directory
WORKDIR /app

# copy source code
COPY urbanroute /app/urbanroute

# Install any needed packages specified in setup.py
RUN pip install urbanroute

# copy entrypoint
COPY entrypoints/air_pollution_shortest_path.py /app

# run the entrypoint
RUN python air_pollution_shortest_path.py
