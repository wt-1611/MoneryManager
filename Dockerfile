FROM docker.io/library/python:3.13
LABEL author="tian"
LABEL version="1.0.0"
COPY . /PythonProject
WORKDIR /PythonProject/rec
RUN cd /PythonProject && \
    pip3 install -r requirements.txt
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@admin.com', 'admin.com')" | python3 manage.py shell
CMD ["./entrypoint.sh"]
