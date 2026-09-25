FROM python:3.12-slim

WORKDIR /srv/diffraction

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests
COPY pyproject.toml .

EXPOSE 8080

# Fixed port: the API is served on 8080.
# Run the test suite inside the container with:
#   docker run --rm <image> python -m pytest tests -v
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
