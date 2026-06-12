# SmartDuka

SmartDuka is a lightweight, fast, and scalable Point of Sale (POS) system built with Django and HTMX.  
It is designed for small to medium retail businesses that need real-time sales processing, inventory tracking, and credit management.

---

# Features

## POS System
- Fast cart-based sales workflow
- HTMX-powered real-time UI updates (no page reloads)
- Session-based cart management
- Instant checkout and receipt generation

## Inventory Management
- Product management
- Automatic stock deduction on sales
- Stock movement tracking (IN / OUT)
- Stock consistency enforcement via service layer

## Sales System
- Sales and sale items tracking
- Receipt number generation
- Profit calculation per sale
- Refund support (via service layer)

## Customer & Credit System
- Customer management
- Credit sales tracking
- Payment recording
- Outstanding balance calculation

## Business Logic Layer
- Centralized service layer (`SaleService`)
- Clean separation of views and business logic
- Audit logging for critical actions

## Real-Time UX
- HTMX-driven POS interface
- Instant cart updates
- Dynamic checkout flow
- Live receipt rendering

---

# Architecture Overview

SmartDuka follows a modular Django architecture:

```
POS (HTMX Frontend)
↓
Views (Thin Controllers)
↓
Service Layer (Business Logic)
↓
Models (Database Layer)
```

### Core Flow:

```
User Action
↓
HTMX Request
↓
Django View
↓
Service Layer (SaleService / CartService)
↓
Models (Sale, SaleItem, StockMovement)
↓
Database
```

---

# Project Structure

```
smart-duka/
│
├── core/         # Core utilities, dashboard, shared logic
├── pos/          # POS frontend + checkout flow
├── sales/        # Sales, customers, credit system
├── inventory/    # Products & stock management
├── templates/    # UI templates (HTMX-based)
├── docs/         # Project documentation
├── config/       # Django project settings
├── manage.py

```
---

# Tech Stack

- **Backend:** Django
- **Frontend:** HTMX + Django Templates
- **Database:** SQLite (dev) / PostgreSQL (production ready)
- **Architecture:** Service Layer Pattern
- **Real-time UI:** HTMX partial rendering

---

# Key Design Principles

- Views remain thin (no business logic inside views)
- All business rules live in service layer
- Stock integrity enforced at model/service level
- Session used for lightweight cart state
- HTMX used instead of heavy frontend frameworks

---

# Local Development Setup

## 1. Clone repository

```bash
git clone https://github.com/Michael-Nyawade/smart-duka.git
cd smart-duka
```  
## 2. Create virtual environment  

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
source venv/Scripts/activate  # Git Bash on Windows
```  

## 3. Install dependencies  

```bash
pip install -r requirements.txt
```

## 4. Run migrations

```bash
python manage.py migrate
```  

## 5. Start development server

```bash
python manage.py runserver
```

# Current Status of Project

SmartDuka is currently in active development stage with:

- Fully functional POS system
- HTMX-based real-time UI
- Service-layer refactored checkout system
- Stock movement tracking system
- Credit sales and payments system  