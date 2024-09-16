# ServiceBooking - Backend

---

## Description

---

ServiceBooking is a backend built in Python using the Django framework with Channels (websocket). This project provides a booking management system for various types of services, making it adaptable to the needs of different businesses. Whether you're offering beauty services, consultations, or other appointments, ServiceBooking allows you to manage your bookings efficiently.

## Features

---

- User authentication
- User roles (admin, staff, customer)
- Service management
- Booking management
- WebSocket-based API for real-time updates
- Mobile ready

## Installation

---

Make sure you have the following software installed:
- Docker
- Docker Compose

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Catalin2702/ServiceBooking_BE.git

cd ServiceBooking_BE

docker-compose up --build

PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=nail_booking_b.settings;API_PORT=8000
```

## Usage

---

After the installation is complete, you can access the API at `ws://localhost:8000`.

## License

---

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

---

This project was inspired by the need for a simple booking management system for various types of services. It was built to help some acquaintances manage their bookings more efficiently and is available for anyone to use and modify.

## Support

---

If you would like to contribute to the project, feel free to submit a pull request or report any issues through the [Issues](https://github.com/Catalin2702/ServiceBooking_BE/issues) section.