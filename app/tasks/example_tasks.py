from .celery_app import celery_app
import time
from datetime import datetime

@celery_app.task
def test_celery_task(message: str):
    """Przykładowe zadanie Celery do testowania"""
    print(f"Zadanie uruchomione: {message} o {datetime.now()}")
    time.sleep(2)  # Symulacja długotrwałego procesu
    return f"Zadanie zakończone: {message}"

@celery_app.task
def long_running_task(duration: int = 10):
    """Długotrwałe zadanie do testowania"""
    for i in range(duration):
        print(f"Krok {i + 1}/{duration}")
        time.sleep(1)
    return f"Zadanie zakończone po {duration} sekundach"

@celery_app.task
def process_data_task(data: dict):
    """Zadanie do przetwarzania danych"""
    print(f"Przetwarzanie danych: {data}")
    # Tutaj można dodać logikę przetwarzania
    time.sleep(5)
    return {
        "status": "completed",
        "processed_data": data,
        "timestamp": datetime.now().isoformat()
    }
