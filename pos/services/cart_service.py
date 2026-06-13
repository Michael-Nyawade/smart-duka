class CartService:

    @staticmethod
    def get_cart(session):
        return session.get("cart", {})

    @staticmethod
    def save_cart(session, cart):
        session["cart"] = cart
        session.modified = True

    @staticmethod
    def add_item(cart, product, qty=1):
        pid = str(product.id)

        if pid in cart:
            cart[pid]["qty"] += qty
        else:
            cart[pid] = {
                "name": product.name,
                "qty": qty,
                "price": float(product.selling_price),
            }

        return cart

    @staticmethod
    def update_item(cart, product_id, action):
        pid = str(product_id)

        if pid not in cart:
            return cart

        if action == "increase":
            cart[pid]["qty"] += 1

        elif action == "decrease":
            cart[pid]["qty"] -= 1
            if cart[pid]["qty"] <= 0:
                del cart[pid]

        return cart

    @staticmethod
    def clear(cart):
        return {}