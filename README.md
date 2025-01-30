# Śledzenie Paczek - Dokumentacja API

Aplikacja Flask do śledzenia przesyłek z API KeyDelivery, umożliwiająca dodawanie paczek do bazy danych oraz ich edycję.

---

## 🔗 Dostępne endpointy API

### **1. Strona główna**
**GET `/`**  
Wyświetla listę wszystkich paczek zapisanych w bazie.

---

### **2. Śledzenie paczki**
**POST `/track_or_add`**  
Wysyła zapytanie do API KD100 w celu sprawdzenia statusu paczki.

#### **Parametry (formularz)**
| Parametr         | Typ     | Wymagane | Opis |
|-----------------|--------|---------|------|
| `carrier_id`    | `string` | ✅ Tak | Identyfikator przewoźnika (usps, dhl, fedex) |
| `tracking_number` | `string` | ✅ Tak | Numer śledzenia paczki |
| `action`        | `string` | ✅ Tak | `"track"` (tylko sprawdzenie) lub `"add"` (dodanie do bazy) |

#### **Przykładowe zapytanie**
```sh
curl -X POST http://127.0.0.1:5000/track_or_add \
     -d "carrier_id=usps" \
     -d "tracking_number=9400111899561590599681" \
     -d "action=track"
```
#### **Przykładowa odpowiedź**
```sh
{
    "carrier_id": "usps",
    "tracking_number": "9400111899561590599681",
    "status": "Delivered"
}
```

---


### **3. Pobranie paczki z bazy**
**GET `/api/package/<tracking_number>`**  
Zwraca szczegóły paczki zapisanej w bazie.

#### **Przykładowe zapytanie cURL**
```sh
curl -X GET "http://127.0.0.1:5000/api/package/9400111899561590599681"
```
#### **Przykładowa odpowiedź**
```sh
{
    "carrier_id": "usps",
    "tracking_number": "9400111899561590599681",
    "status": "Delivered",
    "custom_name": "Moja Paczka"
}
```

---


### **4. Edycja paczki**
**POST `/edit/<package_id>`**  
Pozwala na zmianę nazwy paczki.

#### **Parametry**
| Parametr    | Typ    | Wymagane  | Opis                                      |
|-------------|--------|-----------|-------------------------------------------|
| `custom_name` | string | ❌ Opcjonalnie | Nazwa paczki nadana przez użytkownika |

#### **Przykładowe zapytanie cURL**
```sh
curl -X POST "http://127.0.0.1:5000/edit/1" \
     -H "Content-Type: application/json" \
     -d '{"custom_name": "Prezent urodzinowy"}'
```
#### **Przykładowa odpowiedź**
```sh
{
    "message": "Paczka została zaktualizowana."
}
```

---


### **5. Usunięcie paczki**
**POST `/delete/<package_id>`**  
Usuwa paczkę z bazy.

#### **Przykładowe zapytanie cURL**
```sh
curl -X POST "http://127.0.0.1:5000/delete/1"
```
#### **Przykładowa odpowiedź**
```sh
{
    "message": "Paczka została usunięta."
}
```

---

## ⚠️ Obsługa błędów

#### **1. Nieprawidłowy numer śledzenia lub paczka nie istnieje**
Jeśli podany numer śledzenia jest nieprawidłowy lub nie istnieje, API zwróci kod błędu `404`:

```sh
{
    "message": "Paczka nie znaleziona"
}
```

---


#### **2. Paczka już istnieje w bazie**
Jeśli paczka o danym numerze już istnieje w bazie:
```sh
{
    "message": "Paczka już istnieje w bazie."
}
```
