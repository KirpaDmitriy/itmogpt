# Разработка
## Структура кода
Приложение состоит из 3ёх компонент:
- `runtime` - бэкенд, который в режиме реального времени отвечает на запросы пользователя
- - `yandexgpt.py` - основной код
- `indexer` - бэкенд, который в асинхронном относительно пользовательского контура запросов индексирует данные источников для использованя их в RAG
- - `yandexgpt.py` - основной код
- `front` - фронтенд, который ходит в нужные ручки бэкенда и компонует ответ пользователю
- - `main.py` - основной код

## Развёртывание
Приложение развёртывается в Яндекс Облаке. Ресурсы создаются через Terraform (TODO: прикрепить конфиг). Запуск приложений происходит в рамках докер-контейнеров.
Сборка контейнеров:
- для `runtime` = `cd runtime; docker build -t myapp-runtime .`
- для `front` = `cd front; docker build -t myapp-front .`

Запуск контейнера `runtime` требует наличия в переменных среды двух секретов: `YA_CATALOG_ID` и `YA_API_KEY`.

## Команды запуска
Старт фронта: `cd front; uvicorn frontback:app --reload --host 0.0.0.0 --port 8081`

## Источники
- https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart - Terraform в Яндекс Облаке
- https://kubernetes.io/ru/docs/tasks/tools/install-kubectl/ - установка cli для Кубер
- https://yandex.cloud/ru/docs/cli/operations/install-cli - установка cli для Яндекс Облака
- https://yandex.cloud/ru/docs/cli/quickstart#install - дока про начало работы с cli Яндекс Облака
- https://yandex.cloud/ru/docs/container-registry/tutorials/run-docker-on-vm/console#create-image - Docker в Я Облаке
- https://yandex.cloud/ru/docs/tutorials/infrastructure-management/run-docker-on-vm/terraform - Docker + Terraform в Я Облаке
- https://yandex.cloud/ru/docs/container-registry/quickstart/ - куда нажать, чтобы образ попал в Яндексовое registry
