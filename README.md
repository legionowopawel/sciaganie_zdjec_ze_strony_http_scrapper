

```markdown
# Scraper Downloader – Pobieranie obrazów ze strony internetowej

![Interfejs programu](images/interfejs.png)

## Opis projektu

**Scraper Downloader** to aplikacja napisana w Pythonie, umożliwiająca pobieranie multimediów (głównie obrazów) ze stron internetowych.  
Program posiada **graficzny interfejs użytkownika** (GUI), umożliwiający wpisanie adresu URL, wybór katalogu zapisu i rozpoczęcie pobierania. Wykorzystuje technologie:
- **Scrapy** do obsługi pobierania stron i ekstrakcji danych,
- **requests** do pobierania plików z internetu,
- **tqdm** do dynamicznego wyświetlania pasków postępu.

## Struktura projektu

```
scraper_sciaganie_zdjec_ze_strony_http/
├── images/
│   └── interfejs.png       # Zrzut ekranu interfejsu programu
├── src/
│   └── main.py             # Główny plik z kodem aplikacji
├── requirements.txt        # Lista zależności (Scrapy, requests, tqdm, itp.)
├── start.bat               # Skrypt uruchamiający środowisko wirtualne
├── README.md               # Ten plik
└── venv/                   # Środowisko wirtualne (nie wersjonowane - ujęte w .gitignore)
```

## Instalacja i uruchomienie (Windows, Uruchamiano w Python 3.13)

1. **Klonowanie repozytorium:**

   W terminalu :
   ```bash
   git clone https://github.com/legionowopawel/sciaganie_zdjec_ze_strony_http_scrapper.git
   ```

2. **Uruchomienie środowiska wirtualnego:**

   W katalogu głównym projektu znajduje się plik `start.bat`.  
   **Po dwukrotnym kliknięciu** pliku `start.bat` otworzy się terminal z aktywowanym środowiskiem wirtualnym.

3. **Instalacja zależności:**

   W aktywowanym środowisku uruchom komendę:
   ```bash
   pip install -r requirements.txt
   ```

4. **Uruchomienie aplikacji:**

   Przejdź do katalogu `src` i uruchom główny skrypt:
   ```bash
   python main.py
   ```
 