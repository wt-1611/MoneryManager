FROM docker.io/library/python:3.13
LABEL author="tian"
LABEL version="1.0.0"
COPY . /PythonProject
RUN cd /PythonProject && \
    pip3 install -r requirements.txt  -i https://pypi.mirrors.ustc.edu.cn/simple/
WORKDIR /PythonProject/rec
CMD ["python3" ,"manage.py", "runserver" ,"0.0.0.0:8000"]
