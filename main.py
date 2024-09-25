import argparse

import requests


def parse_arguments():
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument(
		'--id',
		help="exact service ID (e.g., instagram, openai)"
	)
	group.add_argument(
		'--name',
		help="name of the service to search for (e.g., Instagram, Google)"
	)
	parser.add_argument(
		'--limit',
		help="limit of the given prices (default: 10)",
		default=10, type=int
	)
	parser.add_argument(
		'--lang',
		help="language for queries and results (default: en)",
		default='en',
		choices=('fr', 'de', 'ru', 'en', 'zh')
	)
	return parser.parse_args()


def fetch_countries_data(lang: str) -> dict:
	response = requests.get('https://onlinesim.io/api/getNumbersStats.php', {
		'country': 'all', 'lang': lang
	})
	response.raise_for_status()
	return response.json()


def find_target_service(countries: dict, id: str, name: str):
	checked_services: list[str] = []
	for country in countries.values():
		for service in country['services'].values():
			service_id: str = service['slug']
			service_name: str = service['service']

			if service_id in checked_services:
				continue
			checked_services.append(service_id)

			if id and service_id == id:
				return ('service_' + service_id, service_name)
			
			if name and name.lower() in service_name.lower():
				if input(
					f"🔍 found service {service_name}, is that right? (y/n) "
				).lower().startswith('y'):
					return ('service_' + service_id, service_name)
	
	return None


def collect_prices(countries: dict, target_service: tuple):
	prices: list[tuple] = []
	for country in countries.values():
		try:
			service = country['services'][target_service[0]]
			if country['enabled'] and service['count'] > 0:
				prices.append((
					country['locale_name'],
					float(service['price']),
					int(service['count'])
				))
		except KeyError:
			continue
	return sorted(prices, key=lambda item: item[1])


def display_prices(prices: list[tuple], limit: int, service_name: str):
	print(f"✅ showing prices for {service_name}:\n")
	for name, price, count in prices[:limit]:
		print(f"{name:20} {price:10}$ {count:15} available")


def main():
	args = parse_arguments()
	countries = fetch_countries_data(args.lang)
	
	target_service = find_target_service(countries, args.id, args.name)
	if target_service is None:
		print("⛔ can't find the right service")
		return
	
	prices = collect_prices(countries, target_service)
	display_prices(prices, args.limit, target_service[1])


if __name__ == '__main__':
	main()
