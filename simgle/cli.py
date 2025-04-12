import sys
from argparse import ArgumentParser, Namespace
from typing import Optional

from simgle.utils import Language, fetch_countries, find_service, get_country_prices


def parse_arguments() -> Namespace:
    parser = ArgumentParser("simgle")

    service_group = parser.add_mutually_exclusive_group(required=True)
    service_group.add_argument("--id", help="exact service ID (e.g. instagram, openai)")
    service_group.add_argument(
        "--name", help="name of the service to search for (e.g. Instagram, Google)"
    )

    parser.add_argument(
        "--limit", help="limit of the given prices (default: 10)", default=10, type=int
    )
    parser.add_argument(
        "--lang",
        help="language for queries and results (default: en)",
        default="en",
        choices=("fr", "de", "ru", "en", "zh"),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    target_id: Optional[str] = args.id
    target_name: Optional[str] = args.name
    limit: int = args.limit
    language: Language = args.lang

    countries = fetch_countries(language)
    service = find_service(countries, target_id, target_name)
    if not service:
        print("Couldn't find the required service")
        sys.exit(0)

    prices = get_country_prices(countries, service[0])

    for country, price, count in prices[:limit]:
        print(f"{country:20} {price:10}$ {count:15} available")


if __name__ == "__main__":
    main()
