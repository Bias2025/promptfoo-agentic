# Dockerfile
FROM node:20-bullseye AS node_base

# Create a python-friendly layer
FROM python:3.11-bullseye

# Install Node (copy from node image)
COPY --from=node_base /usr/local/bin /usr/local/bin
COPY --from=node_base /usr/local/lib /usr/local/lib
COPY --from=node_base /usr/local/include /usr/local/include
COPY --from=node_base /usr/local/share /usr/local/share

# Ensure npm/npx are available
RUN node --version && npm --version

# Create app dir
WORKDIR /app
# Copy python app
COPY streamlit_app.py /app/streamlit_app.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose default Streamlit port
EXPOSE 8501

# Create workspace dir for promptfoo outputs
RUN mkdir -p /app/promptfoo_workspace
VOLUME ["/app/promptfoo_workspace"]

# Start streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.headless=true"]
