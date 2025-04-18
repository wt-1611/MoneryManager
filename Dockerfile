FROM docker.io/library/python:3.13
ENV TZ=Asia/Shanghai
LABEL author="tian"
LABEL version="1.0.2"
COPY . /PythonProject
WORKDIR /PythonProject/rec
RUN cd /PythonProject && \
    pip3 install -r requirements.txt && chmod +x rec/entrypoint.sh
CMD ["./entrypoint.sh"]
