# recipeapi
API que provê informações sobre receitas gastronômicas. As informções acerca da receitas são: nome da receita, tempo de preparo, preço, link para a receita, usuário que cadastrou a receita, as _tags_, que são sugestões de qual periodo fazer o seu consumo, e os ingredientes que compõe a receita.

## Endpoints

- Usuário: 
```
api/user/create - criar usuário
api/user/token - criar token de acesso
api/user/me - lista os dados do usuário logado
```

- Receita: .
```
api/recipe/recipes - cria, lista, lista por ID, atualiza (ID) e deleta (ID)
```

- Tags:
```
api/recipe/tags - cria, lista, lista por ID, atualiza (ID) e deleta (ID)
```

-  Ingredientes:
```
api/recipe/ingredients - cria, lista, lista por ID, atualiza (ID) e deleta (ID)
```

## Executar 

OBS: necessário ter `Docker` e `Docker Compose` instalados na sua máquina.

Execute os seguintes comando:

- Criar imagem docker:
```
docker-compose build 
```

- Executat as migrations:
```
docker-compose run --rm api python manage.py makemigrations 
docker-compose run --rm api python manage.py migrate 
```

- Criar superusuário (Opcional):
```
docker-compose run --rm api python manage.py createsuperuser
```

- Executar aplicação:
```
docker-compose up
```

- Parar aplicação:
```
docker-compose down
```

- Executar testes:
```
docker-compose run --rm api python manage.py test
```

# Frameworks e Bibliotecas
- <a href="https://www.djangoproject.com/" target="_blank">Django</a>
- <a href="https://www.django-rest-framework.org/" target="_blank">Django REST</a>
- <a href="https://www.docker.com/get-started/" target="_blank">Docker</a>
- <a href="https://docs.docker.com/compose/install/" target="_blank">Docker Compose</a>