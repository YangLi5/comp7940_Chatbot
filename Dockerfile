FROM python
COPY chatbot.py /
COPY requirements.txt /
COPY news_file.py /
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=5390207490:AAECUBQcnRAI0HqDMiZSIffn1pq-1H2gtYU
ENV FireBase_url=https://comp7940chatbot33-default-rtdb.asia-southeast1.firebasedatabase.app/
ENV news_api_key=0ce4ef9f1d4f455f9e471dbd7c07e7a4
CMD ["python","chatbot.py"]