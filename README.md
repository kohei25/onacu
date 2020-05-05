## サーバーの立ち上げ方

NG: docker-compose run --rm web python3 manage.py mig  
OK: docker-compose up

## Djangoコマンドの扱い方

Django: django-admin startapp app  
Docker: docker-compose run --rm web django-admin startapp app

NOTE: ```-rm```オプションをつけないとPCに使用済みコンテナが溢れ、容量を圧迫します