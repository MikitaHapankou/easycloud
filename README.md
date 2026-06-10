# Dokumentacja Projektu easycloud
**Przedmiot:** Wprowadzenie do cyberbezpieczeństwa - projekty  
**Temat projektu:** Temat 17 - Autoryzacja w aplikacjach webowych  

---

### Zespół
* **Numer grupy projektowej:** 6
* **Numer grupy dziekańskiej:** 4A
* **Skład zespołu:**
  1. Mikita Hapankou, nr albumu: 201249
  2. Łukasz Polarczyk, nr albumu: 203157
  3. Piotr Skierka, nr albumu: 203246

---

## 1. Opis projektu
Projekt polega na implementacji bezpiecznej aplikacji webowej typu Cloud Storage, inspirowanej funkcjonalnością serwisu Dropbox. Głównym celem systemu jest umożliwienie użytkownikom przechowywania oraz udostępniania plików na serwerze.
Aplikacja realizuje uwierzytelnianie oraz 2 różne mechanizmy autoryzacji użytkowników na różnych poziomach uprawnień, zgodnie z wymaganiami projektowymi.
## 2. Obrane Technologie
* **Backend:** 
  * `Python` - główny język programowania.
  * `FastAPI` -  framework webowy służący do budowy API.
* **Walidacja i konfiguracja:**
  * `Pydantic` - biblioteka do walidacji danych wejściowych i wyjściowych oraz zapewnienia spójności typów.
  * `pydantic-settings` - moduł tej bioblioteki do zarządzania zmiennymi środowiskowymi i konfiguracją z plików `.env`.
* **Baza danych:**
  * `SQLAlchemy` - ORM (Object-Relational Mapping) do mapowania relacji z bazy danych na obiekty w Pythonie.
  * `PostgreSQL (Supabase)` - baza danych hostowana w chmurze na platformie Supabase, zapewniająca stabilność i bezpieczeństwo danych.
* **Serwer:**
  * `Uvicorn` - asynchroniczny serwer do uruchamiania aplikacji FastAPI.
* **Bezpieczeństwo:**
  * `Bcrypt` - narzędzie do haszowania haseł użytkowników przed zapisem do bazy danych.
  * `PyJWT` - generowanie, podpisywanie oraz weryfikacja tokenów JWT na potrzeby bezstanowej autoryzacji sesji.

---

## 3. Część techniczna i architektura bezpieczeństwa
Architektura systemu opiera się na bezpiecznym oddzieleniu warstwy przechowywania plików od warstwy zarządzania uprawnieniami. Fizyczne pliki użytkowników nie są przechowywane w bazie danych lub supabase storage, lecz w dedykowanym na serwerze katalogu `user_storage`. Dostęp do zasobów na dysku jest w pełni nadzorowany przez backend, co uniemożliwia bezpośrednie i nieautoryzowane pobranie pliku z zewnątrz.

### 3.1. Uwierzytelnianie
**Bezpieczeństwo haseł**

Hasła użytkowników nigdy nie są przechowywane w bazie danych w postaci jawnej. Do ich zabezpieczenia wykorzystano algorytm Bcrypt. Przed zapisem do bazy, każde hasło jest haszowane z automatycznie generowanym saltem. 
Zastosowanie soli skutecznie chroni bazę przed atakami z użyciem tablic do różnych algorytmów hashujących.

**Implementacja w kodzie:**
Logika kryptograficzna znajduje się w pliku `app/services/security.py`
```
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, salt)
    return password_hash.decode('utf-8')
```

**Bezstanowa sesja**

Aplikacja wykorzystuje bezstanowy mechanizm uwierzytelniania oparty na tokenach JWT (JSON Web Token).
Po pomyślnym logowaniu serwer generuje token (podpisywany bezpiecznym algorytmem szyfrowania symetrycznego HS256 z użyciem sekretnego klucza przechowywanego w zmiennych środowiskowych).
Token jest przekazywany do klienta za pomocą nagłówka `Set-Cookie` jako ciasteczko `HttpOnly`. Dzięki temu klient automatycznie i w sposób transparentny dołącza token do każdego kolejnego zapytania.
`Payload` tokenu zawiera niezbędne dane takie jak czas wygaśnięcia (exp) oraz czas aktywacji (nbf), co zapobiega użyciu przeterminowanych lub jeszcze nieważnych tokenów.
Przykład JWT z aplikacji:
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "Mikita",
  "role": "ADMIN",
  "exp": 1780441366,
  "nbf": 1780438966
}

Signature:
IFE7gEeOk4jbOpYi8P79TSCZjFDuRsIKxlffEv72ifk
```

Mechanizm uwierzytelniania został zaimplementowany w warstwie serwisowej w pliku `app/services/userService.py`. Po weryfikacji hasła algorytmem Bcrypt, serwer generuje token z odpowiednimi roszczeniami (`exp`, `nbf`). 
Kluczowym elementem bezpieczeństwa jest sposób przekazania tokenu do klienta, odbywa się to poprzez nagłówek `Set-Cookie` z restrykcyjnymi flagami:
```
response.set_cookie(
    key = "token",
    value = token,
    httponly = True,  # Zabezpieczenie przed atakami ze strony skryptów JS po stronie klients
    samesite = "lax", # Zabezpieczenie pezed atakami CSRF
    path = "/"
)
```

### 3.2. Autoryzacja i Kontrola Dostępu
Zgodnie z wymogami projektu, w aplikacji zaimplementowano i zintegrowano dwie niezależne metody kontroli dostępu, co pozwala na elastyczne zarządzanie uprawnieniami:

#### A. Role-Based Access Control (RBAC)
Pierwsza warstwa autoryzacji opiera się na rolach zdefiniowanych w modelu użytkownika. W systemie występują dwie główne role:
* `USER` - standardowy użytkownik. Domyślnie ma izolowany dostęp wyłącznie do własnego podkatalogu w user_storage, utworzonego na podstawie jego loginu. Zabezpiecza to pliki przed wglądem ze strony innych standardowych użytkowników.
* `ADMIN` - administrator systemu. Posiada globalne uprawnienia pozwalające na podgląd i zarządzanie wszystkimi folderami na serwerze, omijając standardowe restrykcje przypisane dla roli `USER`.
* 
**Implementacja w kodzie:**
Dostępne role definiowane są poprzez klasę `Role(Enum)` w pliku `app/config/config.py`. Weryfikacja uprawnień RBAC odbywa się bezpośrednio podczas prób dostępu do zasobów. Na przykład, w pliku `app/services/dashboardService.py` logika wymusza izolację katalogów dla zwykłych użytkowników, podczas gdy administrator ma dostęp globalny:
```
if user.role != config.Role.ADMIN.name:
    # Jeśli użytkownik nie jest administratorem, musi poruszać się tylko we własnym folderze
    if not file_path.startswith(os.path.join(config.BASE_DIR, user.login)):
        raise HTTPException(status_code=400, detail="Bad filename")
```

#### B. Access Control List (ACL)
Druga warstwa autoryzacji służy do realizacji funkcjonalności bezpiecznego współdzielenia plików pomiędzy użytkownikami z rolą `USER`. Mechanizm ACL został zamodelowany w bazie danych:
Architektura bazy opiera się na tabeli `users`, tabeli `permissions` (reprezentującej unikalne zasoby, np. ścieżkę w formacie owner_login/dirname) oraz tabeli asocjacyjnej `acl`.
Jeśli użytkownik udostępni swój plik innej osobie, w tabeli `acl` tworzony jest wpis łączący ID użytkownika docelowego, ID uprawnienia oraz rodzaj akcji (np. read).

**Implementacja w kodzie:**
Proces współdzielenia konkretnych plików opiera się na modyfikacji tabeli `acl_records`. Funkcja obsługująca współdzielenie (`app/services/dashboardService.py`) najpierw weryfikuje fizyczne istnienie pliku na dysku oraz poprawność ścieżek dostępu, a następnie zapisuje relację w bazie danych za pomocą SQLAlchemy:
```
stmt = insert(acl_records).values(
    user_id=target_user.id,
    permission_id=permission.id,
    action=action # np. "read"
)
db.execute(stmt)
db.commit()
```

### 3.3. Zabezpieczenia operacji na plikach
Proces udostępniania oraz pobierania plików posiada dodatkowe mechanizmy obronne:

Przed nadaniem uprawnień ACL aplikacja weryfikuje, czy zasób fizycznie istnieje na dysku.
Zaimplementowano ochronę przed atakiem typu Directory Traversal (Path Traversal). Weryfikacja bezwzględnych ścieżek dostępu (os.path.abspath) gwarantuje, że użytkownik nie może wyjść poza swój zdefiniowany katalog roboczy (np. poprzez przesyłanie ścieżek z użyciem ../) i uzyskać dostępu do plików systemowych lub danych innych użytkowników bez uprzednio nadanego rekordu ACL.

**Ochrona przed atakiem Path Traversal (Directory Traversal)**

Aby zapobiec nieautoryzowanemu wyjściu poza dedykowany katalog `user_storage` (np. za pomocą ścieżek typu `../../../etc/`), aplikacja wykorzystuje wbudowane mechanizmy biblioteki `os`. 
W pliku `app/services/dashboardService.py` każda ścieżka do pliku jest poddawana weryfikacji:
```
def get_file_path(filename: str, user: User = Depends(dependencies.get_current_user)):
    # 1. Neutralizacja niebezpiecznych znaków (np. ../) poprzez os.path.abspath
    safe_path = os.path.join(config.BASE_DIR, filename)
    file_path = os.path.abspath(safe_path)

    # 2. Walidacja, czy znormalizowana ścieżka nadal znajduje się w dozwolonym katalogu bazowym
    if not file_path.startswith(config.BASE_DIR):
        raise HTTPException(status_code = 400, detail = "Bad filename")
```

### 3.4 Struktura Projektu a Implementacja Bezpieczeństwa
Poniższa struktura katalogów obrazuje modułowość aplikacji, co jest kluczowe z punktu widzenia bezpieczeństwa kodu:
```
easycloud/
├── app/
│   ├── config/
│   │   └── config.py            # Klasa Settings bazująca na pydantic-settings do walidacji pliku .env
│   ├── db/
│   │   └── database.py          # Konfiguracja sesji ORM i połączenia z Supabase
│   ├── models/                  # modele bazy danych
│   │   ├── acl.py               
│   │   ├── permission.py        
│   │   └── user.py              
│   ├── routers/                 # Routery API
│   │   ├── dashboardRouter.py   # Endpointy zarządzania plikami i procesem współdzielenia
│   │   └── userRouter.py        # Endpointy autentykacji i zarządzanie profilem użytkownika
│   ├── schemas/                 # Schematy do walidacji danych za pomocą biblioteki Pydantic
│   │   ├── dashboard.py         
│   │   └── user.py              
│   ├── services/                # Logika biznesowa
│   │   ├── dashboardService.py  # Operacje na plikach
│   │   ├── security.py          # Funkcje bezpieczeństwa (kryptografia i tokeny PyJWT)
│   │   └── userService.py       # Operacje na kontach użytkowników
│   ├── templates/               # Pliki HTML
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   └── register.html
│   ├── user_storage/            # Odizolowane repozytorium plików, niedostępne bezpośrednio z sieci
│   ├── dependencies.py          # Logika sprawdzania uprawnień używana jako dependency injection w serwisach
│   └── main.py                  # Punkt wejścia aplikacji, inicjalizacja FastAPI
├── .env                         # Lokalny plik konfiguracyjny
├── .gitignore                   # Pliki i katalogi ignorowane przez git
├── example.env                  # Szablon zmiennych środowiskowych do konfiguracji projektu
├── README.md                    # Dokumentacja projektu
└── requirements.txt             # Lista zewnętrznych zależności projektu
```

## 4. Instrukcja uruchomienia
Do pracy z projektem rekomendowane jest użycie środowiska IDE PyCharm (na nim opierają się poniższe kroki), jednak aplikację można z powodzeniem uruchomić w dowolnym innym środowisku.

Wymagania:
* Python 3.12
* Git
* Pip

1) Trzeba pobrać repozytorium z projektem za pomocą poleceń:
```
git clone https://github.com/MikitaHapankou/easycloud.git
cd easycloud
```
2) Aby uniknąć konfliktów z globalnymi pakietami Pythona, należy utwórzyć i aktywować środowisko wirtualne:
```
python3 -m venv venv
source venv/bin/activate
```
3) Następnie trzeba zainstalować wszystkie wymagane biblioteki i zależności zdefiniowane w pliku `requirements.txt`:
```
pip install -r requirements.txt
```
4) Aplikacja wymaga do działania odpowiednio skonfigurowanych zmiennych środowiskowych:
   * W głównym katalogu projektu (easycloud) należy utwórzyć nowy plik z nazwą `.env`
   * Skopiować do niego wszystkie zmienne z pliku `example.env` (nie zmieniając ich nazw)
   * Uzupełnij wartości swoimi danymi
5) Gdy środowisko jest skonfigurowane, można uruchomić serwer aplikacji za pomocą serwera Uvicorn:
```
uvicorn app.main:app --reload
```
6) Dostęp do aplikacji i dokumentacji API:
* Po poprawnym uruchomieniu serwera, aplikacja będzie nasłuchiwać na lokalnym porcie `http://localhost:8000/`
* Automatyczna dokumentacja tworzona przed FastAPI znajduje się pod `http://localhost:8000/docs`
