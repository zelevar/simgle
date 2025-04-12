from typing import Any, Literal, Optional

import requests

Language = Literal["fr", "de", "ru", "en", "zh"]
PriceInfo = tuple[str, float, int]  # country, price, count
ServiceInfo = tuple[str, str]  # id, name


def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def fetch_countries(language: Language) -> dict[str, Any]:
    response = requests.get(
        "https://onlinesim.io/api/getNumbersStats.php",
        {"country": "all", "lang": language},
    )
    response.raise_for_status()
    return response.json()


def find_service(
    countries: dict[str, Any], id: Optional[str], name: Optional[str]
) -> Optional[ServiceInfo]:
    checked_services: list[str] = []
    for country in countries.values():
        country_services: dict[str, Any] = country["services"]

        for service in country_services.values():
            service_id: str = service["slug"]
            service_name: str = service["service"]
            if service_id in checked_services:
                continue

            checked_services.append(service_id)

            if id and service_id == id:
                return ("service_" + service_id, service_name)

            if name and name.lower() in service_name.lower():
                continue_prompt = input(
                    f"Found service {bold(service_name)}, continue? (y/n) "
                )

                if not continue_prompt or continue_prompt.lower().startswith("y"):
                    return ("service_" + service_id, service_name)

    return None


def get_country_prices(countries: dict[str, Any], service_id: str) -> list[PriceInfo]:
    prices: list[PriceInfo] = []
    for country in countries.values():
        try:
            country_service = country["services"][service_id]
            if country["enabled"] and country_service["count"] > 0:
                prices.append(
                    (
                        country["locale_name"],
                        float(country_service["price"]),
                        int(country_service["count"]),
                    )
                )
        except KeyError:
            continue

    return sorted(prices, key=lambda item: item[1])
