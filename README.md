#Сервис для запуска кода в docker контейнере

-------------
***python>3.9***

***docker >=20.0***

### Как запустить?
1. Склонировать репозиторий `git clone https://github.com/petrshirin/code-executor-backend.git`
2. Создать виртуальное окружение и активировать его 
`python3 -m venv /path/to/new/virtual/environment`
3. Установить зависимости `pip install -r requirements.txt`
4. создать файл .env `cat .env.example > .env`
5. Отредактировать файл executor/container/requirement.txt 
зависимостями которые необходимы для запуска кода в контейнере
6. Собрать docker-контейнер, для запуска кода и изменить настройку `DEFAULT_IMAGE`
7. Запустить приложение `docker-compose up -d`

[Пример запросов к сервису](https://www.getpostman.com/collections/139a1f0e23ff0d41a7c2)