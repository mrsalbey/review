# Основные endpoint'ы API.

[OpenAPI specification](https://ostracon.ru/api/v1/redoc/)

[API documentation](https://ostracon.ru/api/v1/swagger/)

## 1. Регистрация пользователя на примере Postman.

<img width="868" height="734" alt="image" src="https://github.com/user-attachments/assets/a2ec9305-0202-4cb0-8a64-b9fb62bf0e73" />

## 2. Авторизация. Получение токена.

<img width="861" height="735" alt="image" src="https://github.com/user-attachments/assets/bffb2c3d-4e9b-4d38-ba57-b1eaffac662e" />

## 3. Использование токена (при каждом обращении к API).
  В данном случае, список зарегистрированных пользователей.

<img width="864" height="737" alt="image" src="https://github.com/user-attachments/assets/b7b81903-f696-4087-878b-c48b89ce815b" />

## Записать uuid конфигурации (project_id) в базу данных.

<img width="858" height="736" alt="image" src="https://github.com/user-attachments/assets/b75a2678-d9c6-4903-b095-d5f345242443" />

### Пример json для записи review нового студента (ID + Имя). 
  Произойдет дополнительно запись студента в базу данных.
```json
{
  "project_id": "5fcb03a1-2e90-4b5c-9f22-7a24d195d8e0",
  "student": {
    "id": "77a88b2d-9f5c-4a0a-81e8-5c0a7d5e8c1f",
    "name": "Мария Сидорова"
  },
  "category": {
    "slug": "diplom"
  }
}
```

### Пример json для записи review существующего студента (только ID).
```json
{
  "project_id": "4ebb05c1-0e60-4ab2-b0c9-fe89c533d89d",
  "student": {
    "id": "77a88b2d-9f5c-4a0a-81e8-5c0a7d5e8c1f"
  },
  "category": {
    "slug": "sprint"
  }
}
```

## Получить список review

<img width="859" height="740" alt="image" src="https://github.com/user-attachments/assets/095deab1-1b6f-4ec6-aa2a-748e156518d0" />

## Поиск review по точному соответствию uuid

<img width="860" height="737" alt="image" src="https://github.com/user-attachments/assets/83c31711-0e63-40bf-a528-c74765f855b2" />

## Список категорий проектов
  Доступен без токена.

<img width="861" height="740" alt="image" src="https://github.com/user-attachments/assets/04ab0135-da4b-49b5-b056-9d9afd7c6072" />


