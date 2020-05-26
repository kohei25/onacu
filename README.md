## サーバーの立ち上げ方

通常: docker-compose up
requirement.txtに追記したとき: docker-compose up --build
デバック（ipdbを使う）時: docker-compose run --rm --service-ports web

## Djangoコマンドの扱い方

Django: django-admin startapp app  
Docker: docker-compose run --rm web django-admin startapp app

Django: python manage.py makemigrations
Docker: docker-compose run --rm web python manage.py makemigrations

NOTE: ```-rm```オプションをつけないとPCに使用済みコンテナが溢れ、容量を圧迫します

## Dockerコマンド  

コンテナをすべて停止する  
docker stop $(docker ps -q)