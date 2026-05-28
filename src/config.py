import os
from typing import List


def parse_csv(env_value: str) -> List[str]:
    return [item.strip() for item in env_value.split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "supersecret-foodingo-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

CORS_ALLOWED_ORIGINS = parse_csv(os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"))
TRUSTED_HOSTS = parse_csv(os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1"))
ENFORCE_HTTPS = os.getenv("ENFORCE_HTTPS", "false").lower() in ("1", "true", "yes")

# Ensure production secrets are not left at default during deployment.
if os.getenv("ENVIRONMENT", "development").lower() == "production" and SECRET_KEY == "supersecret-foodingo-key":
    raise RuntimeError("Production deployment requires a secure SECRET_KEY environment variable.")
