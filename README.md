# Dokumentacja Projektu easycloud (Klon Dropbox)
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

### 3.1. Uwierzytelnianie (Authentication)
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

### 3.2. Autoryzacja i Kontrola Dostępu (Authorization)
Zgodnie z wymogami projektu, w aplikacji zaimplementowano i zintegrowano dwie niezależne metody kontroli dostępu, co pozwala na elastyczne zarządzanie uprawnieniami:

#### A. Role-Based Access Control (RBAC)
Pierwsza warstwa autoryzacji opiera się na rolach zdefiniowanych w modelu użytkownika. W systemie występują dwie główne role:
* `USER` - standardowy użytkownik. Domyślnie ma izolowany dostęp wyłącznie do własnego podkatalogu w user_storage, utworzonego na podstawie jego loginu. Zabezpiecza to pliki przed wglądem ze strony innych standardowych użytkowników.
* `ADMIN` - administrator systemu. Posiada globalne uprawnienia pozwalające na podgląd i zarządzanie wszystkimi folderami na serwerze, omijając standardowe restrykcje przypisane dla roli `USER`.

#### B. Access Control List (ACL)
Druga warstwa autoryzacji służy do realizacji funkcjonalności bezpiecznego współdzielenia plików pomiędzy użytkownikami z rolą `USER`. Mechanizm ACL został zamodelowany w bazie danych:
Architektura bazy opiera się na tabeli `users`, tabeli `permissions` (reprezentującej unikalne zasoby, np. ścieżkę w formacie owner_login/dirname) oraz tabeli asocjacyjnej `acl`.
Jeśli użytkownik udostępni swój katalog innej osobie, w tabeli `acl` tworzony jest wpis łączący ID użytkownika docelowego, ID uprawnienia oraz rodzaj akcji (np. read).

### 3.3. Zabezpieczenia operacji na plikach
Proces udostępniania oraz pobierania plików posiada dodatkowe mechanizmy obronne:

Przed nadaniem uprawnień ACL aplikacja weryfikuje, czy zasób fizycznie istnieje na dysku.
Zaimplementowano ochronę przed atakiem typu Directory Traversal (Path Traversal). Weryfikacja bezwzględnych ścieżek dostępu (os.path.abspath) gwarantuje, że użytkownik nie może wyjść poza swój zdefiniowany katalog roboczy (np. poprzez przesyłanie ścieżek z użyciem ../) i uzyskać dostępu do plików systemowych lub danych innych użytkowników bez uprzednio nadanego rekordu ACL.

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