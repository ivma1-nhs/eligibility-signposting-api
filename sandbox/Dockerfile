# First Stage: Build Proxy service
FROM python:3.10-alpine AS deps

# Install pipenv and compilation dependencies
RUN pip install pipenv

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM deps AS runtime

# Copy virtual env from python-deps stage
COPY --from=deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    mkdir /home/appuser/app
WORKDIR /home/appuser/app
USER appuser

# Install application into container
COPY app.py __init__.py /home/appuser/app/
# Copy supervisord configuration
COPY supervisord.conf /etc/supervisord.conf
# Install Prism
USER root
RUN apk add --no-cache nodejs npm && \
    npm install -g @stoplight/prism-cli && \
    apk add --no-cache supervisor

# Expose ports
EXPOSE 9000 5000

# Run supervisord
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
