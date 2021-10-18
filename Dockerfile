FROM python:3.9
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY . /app

# update SO
RUN apt-get -y update && apt-get -y install nginx

## Install dependencies
RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

# nginx congifuration file
COPY ./nginx_config.txt /etc/nginx/sites-available/omni
RUN ln -s /etc/nginx/sites-available/omni /etc/nginx/sites-enabled/omni

RUN chmod +x /app/entry_point.sh

CMD ["/app/entry_point.sh"]