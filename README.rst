About gdflib
-------------------------

gdflib is a Python package made to dump GDF graph files.

Installing
-------------------------------

gdflib can be installed from pypi::

    easy_install gdflib

or::

    pip install gdflib

should just work for most of the users

Usage
--------------------------------

Most simple example::

    >>> from gdflib import GdfEntries, Node
    >>>
    >>> entities = GdfEntries()
    >>> entities.add_node(Node(name='node1', label='This is the first node'))
    >>> entities.add_node(Node(name='node2', label='This is the second node'))
    >>> entities.link('node1', 'node2')
    >>> print entities.dumps()
    nodedef>name , style INT, width DOUBLE, color VARCHAR, image VARCHAR, label VARCHAR, height DOUBLE, visible BOOLEAN, labelcolor VARCHAR, y DOUBLE, x DOUBLE, strokecolor VARCHAR, fixed BOOLEAN, labelvisible BOOLEAN
    node1,1,4.000000,cornflowerblue,,'This is the first node',4.000000,true,cornflowerblue,,,cadetblue,false,false
    node2,1,4.000000,cornflowerblue,,'This is the second node',4.000000,true,cornflowerblue,,,cadetblue,false,false
    edgedef>node1 , node2 , directed BOOLEAN, color VARCHAR, weight DOUBLE, width DOUBLE, label VARCHAR, visible BOOLEAN, labelcolor VARCHAR, labelvisible BOOLEAN
    node1,node2,true,dandelion,1.000000,3.000000,'1',true,dandelion,false

By default all nodes implement the standard properties defined for GDF, unspecified properties will get
the default value.
Custom `nodes` can be defined through the `Declarative` interface::

    >>> from gdflib import String, Double
    >>> from gdflib import GdfEntries, Node
    >>>
    >>> class Product(Node):
    ...     company = String(default='Unknown Company')
    ...     price = Double(required=True)
    ...
    >>> entities = GdfEntries(Product)
    >>> entities.add_node(Product(name='node1', company='Custom Company', price=33.10))
    >>> entities.add_node(Product(name='node2', label='Low Cost Product', price=18.21))
    >>> entities.link('node1', 'node2')
    >>> entities.dumps()
    nodedef>name , style INT, width DOUBLE, color VARCHAR, image VARCHAR, label VARCHAR, height DOUBLE, visible BOOLEAN, labelcolor VARCHAR, y DOUBLE, x DOUBLE, strokecolor VARCHAR, fixed BOOLEAN, labelvisible BOOLEAN, company VARCHAR, price DOUBLE
    node1,1,4.000000,cornflowerblue,,'node1',4.000000,true,cornflowerblue,,,cadetblue,false,false,'Custom Company',33.100000
    node2,1,4.000000,cornflowerblue,,'Low Cost Product',4.000000,true,cornflowerblue,,,cadetblue,false,false,'Unknown Company',18.210000
    edgedef>node1 , node2 , directed BOOLEAN, color VARCHAR, weight DOUBLE, width DOUBLE, label VARCHAR, visible BOOLEAN, labelcolor VARCHAR, labelvisible BOOLEAN
    node1,node2,true,dandelion,1.000000,3.000000,'1',true,dandelion,false

gdflib provides also support for custom `edges`, those can be defined like custom nodes
by subclassing `Edge` and providing additional attributes. In such case instead of using
`link` function to link two nodes, `add_edge` call should be uses.