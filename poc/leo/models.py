"""Liste les modèles disponibles sur le produit IA Infomaniak : python -m leo.models"""

from openai import OpenAI

from .config import settings


def main() -> None:
    client = OpenAI(base_url=settings.base_url, api_key=settings.infomaniak_api_token)
    for model in sorted(client.models.list(), key=lambda m: m.id):
        print(model.id)


if __name__ == "__main__":
    main()
