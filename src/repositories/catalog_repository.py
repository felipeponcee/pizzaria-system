"""Repositórios do cardápio."""
from src.models import Additional, Category, Flavor, Product, Size
from src.repositories.base import Repository


class CategoryRepository(Repository[Category]):
    model = Category


class SizeRepository(Repository[Size]):
    model = Size

    def order_by(self) -> tuple:
        return (Size.sort_order, Size.name)


class FlavorRepository(Repository[Flavor]):
    model = Flavor


class ProductRepository(Repository[Product]):
    model = Product


class AdditionalRepository(Repository[Additional]):
    model = Additional

    def order_by(self) -> tuple:
        return (Additional.kind, Additional.name)
