# Główne funkcjonalności:
	- Moduł kolekcjonujący testy, zapisuje je w liście słowników, gdzie każdy plik odpowiada jednemu słownikowi
	- Równoległa egzekucja testów za pomocą osobnych procesów (osobna pamięć i zasoby)
	- Metody "before" oraz "after" uruchamiane za każdym razem przed oraz po teście w celu przygotowania zasobów.
	- Intuicyjny interfejs graficzny uruchamiany lokalnie za pośrednictwem serwera HTTP, dostępny w przeglądarce
	- Dekoratory mające pomóc w wyodrębnieniu konkretnych typów testów (np. testy regresji, smoke-testy itp.)
	- Moduł logowania zapewniający osobny plik logów dla każdego z testów, zapisujący je w folderze sesji testowej z datą


# Warte wspomnienia:
	- Niestandardowe wyjątki w celu obsługi błędów
	- Wyznaczenie czasu po którym test ma się automatycznie przerwać (tzw. timeout)
	- Możliwość zdefiniowania ilukrotnie ma zostać powtórzony test w przypadku błędu
	- Końcowy wynik zawiera wynik testu (PASS, FAIL, ERROR), długość trwania testu oraz ilość powtórzeń
	- Możliwość ustawienia liczby procesów działających jednocześnie - ręcznie lub automatycznie na podstawie liczby rdzeni procesora.
	- Parametry konfiguracyjne zapisywane w pliku oraz stamtąd pobierane w różnych miejscach programu (wartość timeoutu, ilość rerunów)
	
	
# Planowane:
	- Zapis danych do bazy danych (Poprzednie sesje egzekucji - logi, HTML report).
	- Uruchamianie testów z poziomu interfejsu linii poleceń.
	- Pauzuowanie sesji egzekucji testów i powtórne wznawianie
	
	
	- Automatyczne powiadomienia dot. niepowodzenia sesji na e-mail.
	- Scheduler umożliwiający określenie w czasie kiedy automatycznie ma nastąpić egzekucja
    - Dodanie opcji porównania metryk między sobą (między egzekucjami)
