FROM python
WORKDIR /app
COPY src /app
RUN pip install --no-cache-dir -r requirements.txt --root-user-action ignore
CMD ["python", "app.py"]
