FROM python:3.10.13-bookworm
LABEL authors="chris"

WORKDIR /tmp

RUN mkdir dcm

COPY assets dcm/assets
COPY src dcm/src
COPY test dcm/test
COPY main.py dcm/
COPY setup.py dcm/

WORKDIR /tmp/dcm
RUN python setup.py egg_info
RUN pip install -r *.egg-info/requires.txt
RUN rm -rf *.egg-info/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
