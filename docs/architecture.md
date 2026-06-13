# SmartDuka System Architecture

SmartDuka is a Django-based POS system designed around a **service-layer architecture with HTMX-powered UI interactions**.  
It prioritizes simplicity, transactional safety, and fast cashier workflows.

---

# High-Level Architecture

SmartDuka follows a layered architecture:

```bash
[ HTMX Frontend ]
↓
[ Django Views (Thin Layer) ]
↓
[ Service Layer (Business Logic) ]
↓
[ Django Models (Data Layer) ]
↓
[ Database ]
```

---

# Core Design Principles

## 1. Views are thin controllers
Views only:
- validate requests
- extract input data
- call service layer
- return responses (HTML or JSON)

*No business logic in views*

---

## 2. Service layer is the brain
All business logic is handled in services such as:
- `SaleService`
- `CartService`
- `RefundService`

This ensures:
- reusability
- testability
- separation of concerns

---

## 3. HTMX replaces frontend complexity
Instead of SPA frameworks:

- HTMX handles UI updates
- Django returns HTML fragments
- No heavy JavaScript state management

---

## 4. Session-based cart system
Cart is stored in Django session:

```python
request.session["cart"] = {
    product_id: {
        "name": str,
        "qty": int,
        "price": float
    }
}

id="arch3"
```

This allows:
- fast access
- no database overhead for cart
- per-user isolation

---

# Core Apps Structure

## 1. `pos` app (Frontend + workflow layer)

Responsible for:
- POS interface
- cart interactions
- checkout flow
- HTMX endpoints

Key components:
- `pos_home`
- `htmx_add_to_cart`
- `htmx_process_checkout`

---

## 2. `sales` app (Business domain)

Responsible for:
- Sales records
- SaleItem tracking
- Customer management
- Credit system
- Cashier shifts
- Audit logs

Key models:
- `Sale`
- `SaleItem`
- `Customer`
- `CreditPayment`
- `CashierShift`
- `AuditLog`

---

## 3. `inventory` app (Stock system)

Responsible for:
- Product catalog
- Stock tracking
- Stock movements

Key model:
- `Product`
- `StockMovement`

Stock updates are triggered via:
- `SaleItem.save()`
- Service layer during checkout

---

## 4. `core` app (shared utilities)

Responsible for:
- shop isolation utilities
- user-shop mapping
- shared mixins and helpers

Key utilities:
- `get_user_shop(user)`
- `for_current_shop(queryset, user)`

---

# POS Flow Architecture

## 1. Add to Cart Flow

```bash
User clicks product
↓
HTMX request (pos/htmx_add_to_cart)
↓
Session cart updated
↓
Cart partial returned (HTML)
↓
UI updated instantly
```

---

## 2. Checkout Flow

```bash
User clicks Checkout
↓
HTMX loads checkout form
↓
User selects customer/payment
↓
HTMX submits checkout
↓
SaleService.create_sale()
↓
Sale + SaleItems created
↓
StockMovement automatically triggered
↓
Cart cleared
↓
Receipt HTML returned
```
---

## 3. Stock Deduction Flow

Stock is reduced indirectly via:

```bash
SaleItem creation
↓
SaleService creates SaleItem
↓
StockMovement created (OUT)
↓
Product stock updated
```

---

# Service Layer Responsibilities

## SaleService

Handles:
- Sale creation
- SaleItem creation
- Stock deduction coordination
- Receipt generation logic

---

## CartService

Handles:
- Adding items
- Updating quantities
- Session cart normalization
- Cart calculations

---

## RefundService

Handles:
- Reversing sales
- Restoring stock via StockMovement (IN)
- Logging refund actions

---

# Data Model Relationships

## Sales Domain

```bash
Customer
↓
Sale
↓
SaleItem
↓
Product
```

---

## Inventory Domain

```bash
Product
↓
StockMovement (IN / OUT)
```

---

## Cashier System

```bash
User
↓
CashierShift
↓
Sales linked to shift
```

---

#  Real-Time UI System (HTMX)

SmartDuka uses HTMX for:

- Cart updates
- Checkout rendering
- Receipt display
- Partial UI updates


# Transaction Safety

Critical operations are wrapped in:

```python
@transaction.atomic
id="arch10"
```

Ensures:
- sale creation is atomic
- stock consistency
- rollback on failure

---

# Audit System

Every important action is logged:

- Sale creation
- Refunds
- Cashier actions

Stored in:

AuditLog


---
