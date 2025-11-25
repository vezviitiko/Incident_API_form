import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_create_incident():
    # Тест создания инцидента
    data = {
        "description": "Самокат не в сети",
        "source": "operator"
    }

    response = requests.post(f"{BASE_URL}/incidents/", json=data)
    print("Создание инцидента:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print("-" * 50)
    return response.json()["id"]


def test_get_incidents(status=None):
    # Тест получения инцидентов
    url = f"{BASE_URL}/incidents/"
    if status:
        url += f"?status={status}"

    response = requests.get(url)
    print(f"Получение инцидентов (статус: {status}):")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print("-" * 50)


def test_update_incident(incident_id, new_status):
    # Тест обновления статуса инцидента
    data = {
        "status": new_status
    }

    response = requests.patch(f"{BASE_URL}/incidents/{incident_id}", json=data)
    print(f"Обновление инцидента {incident_id}:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)


def test_get_single_incident(incident_id):
    # Тест получения одного инцидента
    response = requests.get(f"{BASE_URL}/incidents/{incident_id}")
    print(f"Получение инцидента {incident_id}:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)


if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ ИНЦИДЕНТОВ ===\n")

    incident1_id = test_create_incident()

    data = {
        "description": "Точка не отвечает на запросы",
        "source": "monitoring"
    }
    requests.post(f"{BASE_URL}/incidents/", json=data)

    # Получаем все инциденты
    test_get_incidents()

    # Получаем только новые инциденты
    test_get_incidents("new")

    # Обновляем статус первого инцидента
    test_update_incident(incident1_id, "in_progress")

    # Проверяем обновленный инцидент
    test_get_single_incident(incident1_id)

    # Пробуем обновить несуществующий инцидент
    test_update_incident(999, "resolved")

    # Получаем инциденты в работе
    test_get_incidents("in_progress")
