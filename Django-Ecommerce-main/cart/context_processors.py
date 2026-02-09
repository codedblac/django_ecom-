from .cart import Cart


def cart(request):
	# Return the default data from our Cart
	return {'cart': Cart(request)}
