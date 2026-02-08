from typing import Dict
from store.models import Product, Profile


class Cart:
    """
    Session-based shopping cart with optional persistence
    for authenticated users.
    """

    SESSION_KEY = "cart"

    def __init__(self, request):
        self.request = request
        self.session = request.session

        # Initialize cart in session if not present
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = self.session[self.SESSION_KEY] = {}

        self.cart: Dict[str, int] = cart

    
    # Internal Helpers
    # =========================

    def _save(self) -> None:
        """
        Mark session as modified and sync cart
        to authenticated user's profile.
        """
        self.session.modified = True

        if self.request.user.is_authenticated:
            Profile.objects.filter(
                user_id=self.request.user.id
            ).update(old_cart=self.cart)

    @staticmethod
    def _get_product_id(product) -> str:
        """
        Normalize product ID.
        """
        return str(product.id if hasattr(product, "id") else product)

    # =========================
    # Cart Operations
    # =========================

    def add(self, product, quantity: int = 1) -> None:
        """
        Add a product to the cart.
        """
        product_id = self._get_product_id(product)

        if product_id not in self.cart:
            self.cart[product_id] = int(quantity)

        self._save()

    def update(self, product, quantity: int) -> Dict[str, int]:
        """
        Update product quantity in the cart.
        """
        product_id = self._get_product_id(product)
        self.cart[product_id] = int(quantity)

        self._save()
        return self.cart

    def delete(self, product) -> None:
        """
        Remove a product from the cart.
        """
        product_id = self._get_product_id(product)

        if product_id in self.cart:
            del self.cart[product_id]

        self._save()

    # =========================
    # Query Methods
    # =========================

    def __len__(self) -> int:
        """
        Return total number of unique items in cart.
        """
        return len(self.cart)

    def get_products(self):
        """
        Return Product queryset for items in cart.
        """
        product_ids = self.cart.keys()
        return Product.objects.filter(id__in=product_ids)

    def get_quantities(self) -> Dict[str, int]:
        """
        Return cart quantities.
        """
        return self.cart

    def get_total_price(self) -> float:
        """
        Calculate total cart value.
        """
        products = self.get_products()
        total = 0

        for product in products:
            quantity = self.cart.get(str(product.id), 0)

            price = (
                product.sale_price
                if getattr(product, "is_sale", False)
                else product.price
            )

            total += price * quantity

        return total
