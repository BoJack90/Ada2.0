# Advanced Content Generation System - Przewodnik

## Przegląd

Nowy system generowania treści w Ada 2.0 wykorzystuje zaawansowane techniki AI, w tym:
- **Deep Reasoning** - wieloetapowe rozumowanie dla lepszego zrozumienia kontekstu
- **Chain-of-Thought** - analiza krok po kroku dla wysokiej jakości wyników
- **External Research** - integracja z Tavily i RAGFlow dla aktualnych danych
- **Industry Intelligence** - automatyczna analiza branży i konkurencji

## Główne komponenty

### 1. Deep Reasoning Engine (`app/core/deep_reasoning.py`)

System wieloetapowego rozumowania, który:
- Analizuje kontekst organizacji i briefy
- Przeprowadza research zewnętrzny
- Formułuje strategię content
- Generuje kreatywne tematy
- Ocenia i optymalizuje wyniki

### 2. Enhanced Brief Analyzer

Zaawansowana analiza briefów wykorzystująca:
- Ekstrakcję kluczowych tematów
- Identyfikację priorytetów
- Mapowanie wymagań
- Ocenę zgodności z celami biznesowymi

### 3. External Integrations (`app/core/external_integrations.py`)

#### Tavily Integration
```python
tavily = TavilyIntegration()
results = await tavily.search(
    query="AI trends 2024",
    search_depth="advanced",
    max_results=10
)
```

#### RAGFlow Integration
```python
ragflow = RAGFlowIntegration()
similar_content = await ragflow.get_similar_content(
    content="Your content here",
    limit=5
)
```

### 4. Industry Knowledge Base

Automatyczna analiza:
- Strony internetowej firmy
- Trendów branżowych
- Strategii konkurencji
- Preferencji odbiorców

## Jak korzystać

### 1. Generowanie tematów z Deep Reasoning

```bash
POST /api/v1/advanced/content-plans/{plan_id}/generate-with-reasoning
```

Parametry:
- `force_regenerate` (bool) - wymusza regenerację istniejących tematów
- `use_deep_research` (bool) - włącza głęboki research (domyślnie: true)

### 2. Research tematu

```bash
POST /api/v1/advanced/research/topic
{
    "topic": "Sztuczna inteligencja w logistyce",
    "organization_id": 123,
    "depth": "deep",
    "include_raw_data": false,
    "store_results": true
}
```

### 3. Generowanie Smart Variant

```bash
POST /api/v1/advanced/topics/{topic_id}/generate-smart-variant?platform_name=linkedin
```

## Konfiguracja

### Zmienne środowiskowe

```env
# Tavily API
TAVILY_API_KEY=your_key_here

# RAGFlow
RAGFLOW_API_URL=http://localhost:9380
RAGFLOW_API_KEY=your_key_here
RAGFLOW_KB_ID=your_kb_id

# Ustawienia generowania
DEFAULT_CONTENT_MODEL=gemini-1.5-pro-latest
ENABLE_DEEP_REASONING=true
RESEARCH_DEPTH=deep
```

### Prompty AI

System wykorzystuje zaawansowane prompty dla każdego etapu:

1. **deep_reasoning** - analiza kontekstu
2. **research_analysis** - synteza danych z researchu
3. **strategy_formulation** - tworzenie strategii content
4. **creative_generation** - generowanie tematów
5. **evaluation** - ocena i optymalizacja

## Workflow

### 1. Przygotowanie

1. Utwórz Content Plan
2. Dodaj briefy (opcjonalnie)
3. Skonfiguruj correlation rules

### 2. Generowanie

1. System analizuje:
   - Dane organizacji
   - Strategię komunikacji
   - Briefy
   - Odrzucone tematy (uczenie się)

2. Przeprowadza research:
   - Trendy branżowe
   - Analiza konkurencji
   - Aktualne wydarzenia

3. Generuje tematy:
   - Aligned z briefami
   - Zróżnicowane tematycznie
   - Zoptymalizowane pod SEO
   - Z unikalnymi kątami

### 3. Ocena jakości

Każdy temat otrzymuje:
- **Priority Score** (1-10) - zgodność z briefem
- **Content Type** - typ treści (educational, thought_leadership, etc.)
- **Pillar** - filar tematyczny
- **Brief Alignment** - jak dobrze odpowiada na brief

## Analityka

### Content Performance Analytics

```bash
GET /api/v1/advanced/analytics/content-performance?organization_id=123
```

Zwraca:
- Wskaźniki akceptacji tematów
- Rozkład typów treści
- Wykorzystanie briefów
- Porównanie metod generowania

### Generation Insights

```bash
GET /api/v1/advanced/content-plans/{plan_id}/generation-insights
```

Pokazuje:
- Wykorzystane insights z branży
- Metryki różnorodności
- Zgodność z briefami
- Kroki rozumowania

## Best Practices

### 1. Briefy

- Dodawaj szczegółowe briefy z konkretnymi wymaganiami
- Oznaczaj priorytety (1-10)
- Używaj słów kluczowych istotnych dla branży

### 2. Strategia komunikacji

- Zdefiniuj dokładnie ton i styl
- Dodaj forbidden/preferred phrases
- Skonfiguruj style dla każdej platformy

### 3. Research

- Włącz deep research dla najlepszych wyników
- Regularnie aktualizuj knowledge base
- Monitoruj trendy branżowe

### 4. Iteracja

- Analizuj odrzucone tematy
- Dostosowuj prompty na podstawie wyników
- Testuj różne głębokości researchu

## Troubleshooting

### Problem: Tematy są zbyt ogólne

**Rozwiązanie:**
- Dodaj więcej szczegółów do briefów
- Włącz deep research
- Zwiększ priority_score threshold

### Problem: Brak zgodności z briefem

**Rozwiązanie:**
- Sprawdź analizę briefu w insights
- Upewnij się, że brief jest jasny
- Użyj force_regenerate z lepszymi parametrami

### Problem: Wolne generowanie

**Rozwiązanie:**
- Zmniejsz liczbę research queries
- Użyj cache dla powtarzających się zapytań
- Rozważ użycie "basic" depth dla testów

## Migracja z starego systemu

1. Istniejące Content Plans będą działać normalnie
2. Nowe plany mogą używać obu systemów
3. Metadata w topics pokazuje metodę generowania
4. Możesz regenerować stare tematy nowym systemem

## Rozwój

### Planowane funkcje

1. **Multi-language support** - generowanie w różnych językach
2. **A/B testing** - porównywanie różnych strategii
3. **Auto-optimization** - uczenie się z zaakceptowanych tematów
4. **Content clustering** - automatyczne grupowanie tematów
5. **Predictive analytics** - przewidywanie skuteczności

### Współpraca z MCP

System jest przygotowany na integrację z MCP (Model Context Protocol):
- Konfiguracja przez zmienne środowiskowe
- Wsparcie dla MCP serwerów Tavily i RAGFlow
- Możliwość dodania własnych MCP tools

## Podsumowanie

Nowy system generowania treści w Ada 2.0 to znaczący krok naprzód w automatyzacji content marketingu. Wykorzystując deep reasoning, zewnętrzny research i inteligentną analizę, system generuje treści które są:
- Bardziej trafne i aligned z celami biznesowymi
- Oparte na aktualnych danych i trendach
- Zoptymalizowane pod kątem odbiorców
- Zróżnicowane i kreatywne

Dla najlepszych rezultatów, używaj systemu regularnie i iteracyjnie dostosowuj parametry na podstawie wyników.