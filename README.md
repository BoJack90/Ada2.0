# Ada 2.0

Nowoczesna aplikacja fullstack z FastAPI (backend) i Next.js (frontend), PostgreSQL, Redis i Celery uruchamiana w kontenerach Docker.

## Stack Technologiczny

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Baza danych**: PostgreSQL 15
- **Cache/Broker**: Redis 7
- **Kolejki**: Celery

### Frontend
- **Framework**: Next.js 14+ (React)
- **Język**: TypeScript
- **Styling**: Tailwind CSS
- **UI**: Shadcn/ui components
- **Animacje**: Framer Motion
- **Stan**: React Query
- **Ikony**: Lucide React

### Infrastruktura
- **Konteneryzacja**: Docker + Docker Compose
- **Wszystkie serwisy w kontenerach**

## Struktura Projektu

```
Ada2.0/
├── app/                    # Główna aplikacja
│   ├── api/               # Endpointy API
│   ├── core/              # Konfiguracja
│   ├── db/                # Modele bazy danych
│   ├── services/          # Logika biznesowa
│   ├── tasks/             # Zadania Celery
│   └── main.py            # Punkt wejścia
├── docker/                # Pliki Docker
├── migrations/            # Migracje bazy danych
├── tests/                 # Testy
├── docker-compose.yml     # Orchestracja kontenerów
├── Dockerfile            # Definicja kontenera
├── requirements.txt      # Zależności Python
└── rules.md              # Zasady projektowe
```

## Szybki Start

1. **Klonowanie i przejście do katalogu**:
   ```bash
   cd Ada2.0
   ```

2. **Uruchomienie całego stacku**:
   ```bash
   docker-compose up --build
   ```

3. **Sprawdzenie czy wszystko działa**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Dokumentacja API: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/v1/health

## Dostępne Serwisy

- **Frontend (Next.js)**: `http://localhost:3000`
- **Backend API (FastAPI)**: `http://localhost:8000`
- **Dokumentacja API**: `http://localhost:8000/docs`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **Celery Worker**: działający w tle
- **Celery Beat**: scheduler w tle

## Główne Funkcje Frontend

- 🎨 **Nowoczesny UI** z Tailwind CSS i animacjami
- 📊 **Dashboard** z statusem API i zarządzaniem zadaniami
- 📅 **Kalendarz** z możliwością dodawania wydarzeń
- 📄 **Zarządzanie dokumentami** z uplodem i podglądem
- ⚡ **Loading states** i animacje dla lepszego UX
- 📱 **Responsive design** dla wszystkich urządzeń

## Endpointy API

### Frontend
- **Główna aplikacja**: http://localhost:3000
- **Dashboard**: http://localhost:3000 (domyślna strona)
- **Zadania**: http://localhost:3000 (zakładka Tasks)
- **Dokumenty**: http://localhost:3000 (zakładka Documents)  
- **Kalendarz**: http://localhost:3000 (zakładka Calendar)

### Backend API
- `GET /` - Strona główna API
- `GET /docs` - Dokumentacja Swagger
- `GET /api/v1/health` - Status aplikacji
- `GET /api/v1/health/db` - Status bazy danych
- `GET /api/v1/health/redis` - Status Redis
- `POST /api/v1/health/celery` - Test Celery

## Rozwój

### Lokalne uruchomienie w trybie deweloperskim:
```bash
docker-compose up
```

### Zatrzymanie:
```bash
docker-compose down
```

### Przebudowanie kontenerów:
```bash
docker-compose up --build
```

### Sprawdzenie logów:
```bash
docker-compose logs -f [service_name]
```

## Ważne Pliki

- `rules.md` - **Bardzo ważny plik z zasadami projektu**
- `.env` - Zmienne środowiskowe (nie commitować!)
- `docker-compose.yml` - Konfiguracja wszystkich serwisów

## Dalszy Rozwój

Projekt jest tworzony etapami. Sprawdź `rules.md` dla aktualnego stanu i zasad rozwoju.

---
**Aktualizacja**: 2025-07-09
