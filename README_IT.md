# ServiceBooking - Backend

[English](README.md) | Italiano

## Descrizione

ServiceBooking è un backend sviluppato in Python utilizzando il framework Django con Channels (websocket). Questo progetto fornisce un sistema di gestione delle prenotazioni per diversi tipi di servizi, rendendolo adattabile alle esigenze di vari business. Che tu offra servizi di bellezza, consulenze o altri tipi di appuntamenti, ServiceBooking ti permette di gestire le tue prenotazioni in modo efficiente.

## Features

- Autenticazione utente
- Ruoli utente (admin, staff, cliente)
- Gestione dei servizi
- Gestione delle prenotazioni
- API basata su WebSocket per aggiornamenti in tempo reale
- Pronto per dispositivi mobili

## Installazione

Assicurati di avere i seguenti software installati:
- Docker
- Docker Compose

Clona il repository e naviga nella directory del progetto:

```bash
git clone https://github.com/Catalin2702/ServiceBooking_BE.git

cd ServiceBooking_BE
```

Esegui il seguente comando per avviare il progetto:

```bash
docker-compose up --build

PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=nail_booking_b.settings;API_PORT=8000
```

## Utilizzo

Dopo aver completato l'installazione, puoi accedere all'API all'indirizzo ws://localhost:8000.

## Licenza

Questo progetto è open source e disponibile sotto la MIT License.

## Ringraziamenti

Questo progetto è stato ispirato dalla necessità di un semplice sistema di gestione delle prenotazioni per vari tipi di servizi. È stato sviluppato per aiutare dei conoscenti a gestire le loro prenotazioni in modo più efficiente ed è disponibile per chiunque desideri utilizzarlo o modificarlo.

## Supporto

Se desideri contribuire al progetto, sentiti libero di inviare una pull request o di segnalare eventuali problemi tramite la sezione [Issues](https://github.com/Catalin2702/ServiceBooking_BE/issues).