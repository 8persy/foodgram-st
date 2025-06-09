# Foodgram - социальная сеть для готовки))

Проект представляет собой сайт, на котором вы можете делиться своими рецептами и подсматривать новые у других пользователей.
Вы можете добавить рецепт, подписаться на понравившегося пользователя, добавить блюдо в избранное или корзину и скачать полный список нужных ингредиентов.


## Запуск проекта

### Требования для запуска с Docker
- Docker
- Docker Compose

### 1. Клонирование репозитория
```bash
git clone https://github.com/8persy/foodgram-st.git
cd foodgram-st
```

### 2. Настройка окружения
Создайте файл .env в корне проекта с переменными окружения, которые можете взять в .env.example


### 3. Запуск контейнеров
```bash
cd infra
```
```bash
docker-compose up --build
```

### 4. Применение миграций
```bash
docker exec -it web python manage.py migrate
```

### 5. Заполнение базы данных
```bash
cp D:\dev\foodgram-st\backend\data\ingredients.json infra-web-1:/app/
```

```bash
docker exec -it infra-web-1 python manage.py loaddata /app/ingredients.json 
```