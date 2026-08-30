<p align="center">
  <a href="https://fastapi.tiangolo.com/" target="blank"><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" width="600" alt="FastAPI Logo" /></a>
</p>

## Table of Contents

1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Docker Stack](#docker-stack)
8. [Test](#test)
9. [API Documentation](#api-documentation)
10. [Contact & Follow](#contact--follow)

### General Info

***
**Print Order Reception Service API**

The **Print Order Reception Service API** is designed to receive, process, and group document print requests into
optimized print orders.
This system handles document intake, validation, and intelligent grouping to ensure efficient print job management and
resource utilization.

It is developed using **FastAPI**, **MongoDB** (with Beanie ODM), and **Pydantic**, following best practices for *
*asynchronous RESTful API design** and modern Python development.

📄 **Project Context (Technical Test):**
> This API was developed to fulfill the requirements of a technical assessment. The complete list of business rules,
> constraints, and expected behaviors is detailed in the document:  
> **[Indicaciones_Servicio_Recepcion_de_Ordenes.pdf](./Indicaciones_Servicio_Recepcion_de_Ordenes.pdf)** *(located in
the root directory of this repository)*

### Technologies

***
Core technologies and tools used in this project:

- **FastAPI:** Modern, fast (high-performance) web framework for building APIs with Python based on standard Python type
  hints.
- **MongoDB, Motor & Beanie:** Asynchronous NoSQL database with an intuitive Object-Document Mapper (ODM) for
  schema-based modeling.
- **Pydantic & Pydantic-Settings:** Data validation, serialization, and environment settings management.
- **Uvicorn:** Lightning-fast ASGI server for running the FastAPI application.
- **PyJWT, pwdlib & Argon2:** Secure authentication, authorization, and password hashing.
- **Python-Multipart:** Support for file uploads (e.g., document files for printing).
- **Swagger / OpenAPI:** Automatic interactive API documentation and specification.
- **Pytest, pytest-asyncio & pytest-cov:** Asynchronous testing framework with code coverage reporting.
- **Python-dotenv:** Environment variable management for local development.
- **Docker:** Containerization for consistent and reproducible deployment.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

### Prerequisites

***
Before you begin, ensure you have the following installed on your system:

- [Python (v3.10+)](https://www.python.org/downloads/) – Required runtime.
- [pip](https://pip.pypa.io/en/stable/installation/) – Python package installer.
- [MongoDB](https://www.mongodb.com/try/download/community) – Required as the main database.
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/) – *(Optional)*, if
  you prefer to run the application and its dependencies in containers.

⚠️ **Note:** It is highly recommended to use **Docker** for local development to avoid manual installation and
configuration of MongoDB.

## Installation

To install the API, follow these steps:

```bash
# Clone the repository
$ git clone https://github.com/jmarqb/print-order-service.git
$ cd print-order-service

# Create a virtual environment
$ python -m venv venv

# Activate the virtual environment
# On Windows:
$ .\venv\Scripts\activate
# On macOS/Linux:
$ source venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt
```

## Configuration

* Copy the contents of `.env.example` into a new `.env` file and update it with your credentials and connection
  parameters.
* Remember, you must have a running instance of MongoDB (https://www.mongodb.com/try/download/community) unless you are
  using the Docker stack.

## Running the Application

To run the Print Order Reception Service API locally, use the following command:

```bash
$ python main.py
```

This will start the development server, and the application will be available at `http://127.0.0.1:3001`.

We recommend you visit the section [API Documentation](#api-documentation).

## Docker Stack

If you have Docker and Docker Compose installed, running the application and its dependencies becomes even easier.
First, clone the repository and navigate to the project directory:

```bash
$ git clone https://github.com/jmarqb/print-order-service.git
$ cd print-order-service
```

**Important**

* Copy the contents of `.env.example` into a new `.env` file and update it with your credentials for connection
  parameters.

* Now, you can start the services by running:

```bash
$ docker-compose up --build
```

This will start the server and the API will be available at `http://localhost:3001`.

## Test

To ensure everything runs smoothly, this project includes asynchronous unit and integration tests using **Pytest**, *
*pytest-asyncio**, and **pytest-cov**. To execute them, follow these steps:

**Dependency Installation:** Before running the tests, ensure you've installed all the project dependencies
in your virtual environment :

```
# Activate the virtual environment
# On Windows:
$ .\venv\Scripts\activate
# On macOS/Linux:
$ source venv/bin/activate
```

(`pip install -r requirements.txt`).

**Run Tests:** To run the test suite with coverage reporting, use the following command:

```bash
$ pytest --cov=. tests/
```

## API Documentation

FastAPI automatically generates interactive API documentation based on the OpenAPI standard. For more detailed
information about the workflow, endpoints, request/response models, and status codes, visit the API documentation.

You can access the interactive documentation at:

- **Swagger UI:** `http://127.0.0.1:3001/ms-print/api/docs`
- **ReDoc:** `http://127.0.0.1:3001/ms-print/api/redoc`

---

## Contact & Follow

Thank you for checking out my project! If you have any questions, feedback, or just want to connect, here's where you
can find me:

**GitHub**: [jmarqb](https://github.com/jmarqb)

Feel free to [open an issue](https://github.com/jmarqb/Print-Order-Reception-Service/issues) or submit a PR if you find
any bugs or have some suggestions for improvements.

© 2026 Jacmel Márquez. All rights reserved.