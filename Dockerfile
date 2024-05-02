FROM python

COPY requirements.txt ./
COPY report-app.py ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python","report-app.py"]
