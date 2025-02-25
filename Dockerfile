# FROM python:3.10
# RUN useradd -m -u 1000 user
# USER root
# ENV HOME=/home/user \
#     PATH=/home/user/.local/bin:$PATH
# WORKDIR $HOME/app
# COPY --chown=user:user . $HOME/app
# # COPY --chown=user . $HOME/app
# COPY requirements.txt .
# # COPY ./requirements.txt ~/app/requirements.txt

# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt
# # RUN pip install -r requirements.
# # Expose port
# EXPOSE 7860
# # RUN pip install pydantic==2.10.1 chainlit
# # COPY . .

# # Ensure app and .local have proper permissions
# # USER root
# RUN chmod -R 755 /home/user/app
# RUN chmod -R 755 /home/user/.local
# RUN mkdir -p /home/user/app/.files && chown -R user:user /home/user/app/.files


# USER user

# CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]

# # CMD ["chainlit", "run", "app.py", "--port", "7860"]


FROM python:3.10

# Create user with specific UID
RUN useradd -m -u 1000 user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Copy requirements and install dependencies as root
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN pip install pydantic==2.10.1 chainlit


# Copy application files
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /home/user/app/.files && \
    mkdir -p /home/user/.local && \
    chown -R user:user /home/user

COPY chainlit.md .


# Expose port
EXPOSE 7860

# Switch to non-root user
USER user

# Run the application
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860", "--no-cache"]

# CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]