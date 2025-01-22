## Instalation
### Crée la DB
install image docker
```
version: '3.8'
services:
  db:
    image: postgres:latest
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: ecommerce
    ports:
      - "5432:5432"
    volumes:
      - ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```
Copie des fichier sql dans l image postgress
```
docker cp ./sql/DML.sql postgres_db:/tmp/DML.sql
docker cp ./sql/DDL.sql postgres_db:/tmp/DDL.sql
```
Connection a l image docker
```
docker exec -it postgres_db bash
```
Execution des scripts 
```
psql -U admin -d ecommerce -f /tmp/DDL.sqlß
psql -U admin -d ecommerce -f /tmp/DML.sql
```

Connection a la base de donnée
```
psql -h localhost -U admin -d ecommerce
```
### Lancer l api
Créer un environnement virtuel :
```
python -m venv venv
```
Activer l'environnement virtuel :
Sur Windows :
```
venv\\Scripts\\activate
```
Sur macOS/Linux :
```
source venv/bin/activate
```
installer les dépendances
```
pip install -r requirements.txt
```
Démarer le serveur Flask
```
python app.py
``` 
Puis sur http://127.0.0.1:5000/


