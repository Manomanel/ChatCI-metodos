# ChatCI-metodos

Link para o diagrama de classe, abrir no draw.io: https://drive.google.com/file/d/14rqQwKb_EIY5hPhdn_KsxWgvO0g6wprm/view?usp=sharing

Link para o diagrama dos casos de uso: https://miro.com/welcomeonboard/RlIzY3lCNGZUNEVYVzcvYXhWSm4wR1pEWkRXSFBrNmc3czVPcThvUllnYjVFTUQ3bmx5TWJQWUM5R2pJR205eitEL1d2RWdzclIxMHI4bW55VjFyREsybjJVaHFsMkNGZ1FQNHJ3THoyYU5ZM0pUNm5zcnpwRGFsU0pvdHhVK3BBd044SHFHaVlWYWk0d3NxeHNmeG9BPT0hdjE=?share_link_id=518628768916

### Rodando o Projeto ChatCI

Sistema de chat com Flask + PostgreSQL, voltado para ambientes educacionais. Utiliza Docker para facilitar a execução.

⚙️ Execução Rápida
Pré-requisitos: Docker, Docker Compose.

git clone <url-do-repositorio>
cd ChatCI-metodos
docker-compose up --build -d

Acesse:
Aplicação: http://localhost:5001

Parar containers:
docker-compose down (para os serviços)
docker-compose down -v (remove também os volumes)