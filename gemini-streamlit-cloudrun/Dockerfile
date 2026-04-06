# Base image: official Python 3.13 slim variant.
# "slim" strips out compilers, docs, and other non-runtime extras,
# making the final image significantly smaller than the full python:3.13 image.
FROM python:3.13-slim

# Tell Docker (and Cloud Run) that the container listens on port 8080.
# EXPOSE is metadata only — it does NOT actually open the port.
# Cloud Run routes HTTPS traffic to this port by default.
EXPOSE 8080

# Set the working directory inside the container.
# All subsequent COPY, RUN, and ENTRYPOINT paths are relative to /app.
# The directory is created automatically if it doesn't exist.
WORKDIR /app

# Copy everything from the build context (your local project folder)
# into /app inside the container.
# This includes app.py, requirements.txt, and any other project files.
COPY . ./

# Install Python dependencies listed in requirements.txt.
# --no-cache-dir: don't store the pip download cache inside the image,
#                 keeping the image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run when the container starts.
# Starts the Streamlit app with:
#   --server.port=8080    → match the EXPOSE port above (required by Cloud Run)
#   --server.address=0.0.0.0 → listen on all network interfaces, not just localhost,
#                              so the container is reachable from outside
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
