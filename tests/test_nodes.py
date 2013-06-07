from nose.tools import raises
from gdflib import String, Double, Integer, Boolean, Color
from gdflib import InvalidSchemaItem
from gdflib import Edge, Node, GdfEntries

class Product(Node):
    company = String(required=True)
    price = Double(required=False)
    available = Boolean(default=False, required=True)

class TestProduct(object):
    @raises(InvalidSchemaItem)
    def test_missing_required(self):
        p = Product(name='Name')

    def test_required_with_default(self):
        p = Product(name='Name', company='Unknown')
        assert p.available == False

class TestEntries(object):
    def test_entries(self):
        ge = GdfEntries(Product, Edge)
        ge.add_node(Product(name='Somenode', company='Unknown'))
        ge.add_node(Product(name='Otherone', company='Unknown'))
        ge.link('Somenode', 'Otherone', color=(255,0,0))
        ge.dumps()
