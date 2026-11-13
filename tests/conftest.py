import os

# Define a chave antes de qualquer import da app, para os testes
# não dependerem do .env local.
os.environ.setdefault("JWT_SECRET_KEY", "chave-apenas-para-testes")