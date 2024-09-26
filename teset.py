import requests
import json


api_key = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwOTA0djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc0MTk4NDM1MywiaWQiOiIwMTkxZWE4My0zNWJkLTdiMzAtODQ1Zi04N2ExYzA3NmY2M2YiLCJpaWQiOjEyNzU0NDc0Mywib2lkIjozOTE3NzEwLCJzIjoxMDI0LCJzaWQiOiI3NWJjMmFkZS0xOWY5LTRjNTctYTVhOC02OWJlYThjODA5YjEiLCJ0IjpmYWxzZSwidWlkIjoxMjc1NDQ3NDN9.u8pon_rG5pr8VuSjMVFraAbbIvFnuAFMC4wNn8I36e1wfqLCpDl7v7O4fHb44D4p1a7Hd-oc9j7oGfGfhK1ttA'
headers = {
    'Authorization': f'Bearer {api_key}'
}


coefficients_url = 'https://supplies-api.wildberries.ru/api/v1/acceptance/coefficients'

response = requests.get(coefficients_url, headers=headers)

if response.status_code == 200:
    coefficients_data = response.json()
    print(coefficients_data)
    

    with open('coefficients.json', 'w', encoding='utf-8') as f:
        json.dump(coefficients_data, f, ensure_ascii=False, indent=4)
    print("Коэффициенты приёмки сохранены в 'coefficients.json'.")
else:
    print(f"Ошибка: {response.status_code}")