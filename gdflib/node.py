from itertools import chain

from .schema import SchemaItem, NoDefault, SameAs
from .schema import Name, String, Double, Boolean, Color, Shape

class DeclarativeMeta(type):
   def __new__(meta, name, bases, orig_dct):
        dct = {}
        for field_type in meta.PREDEFINED_PROPERTIES:
            if field_type.name not in orig_dct:
                dct[field_type.name] = field_type

        for field_name, field_type in orig_dct.iteritems():
            if isinstance(field_type, SchemaItem) and field_type.name is NoDefault:
                field_type.name = field_name
            dct[field_name] = field_type
            
        definition = super(DeclarativeMeta, meta).__new__(meta, name, bases, dct)
        definition.__properties__ = sorted((prop for prop in dct.values() if isinstance(prop, SchemaItem)), key=lambda o:o.order)
        definition.__definition_blocks__ = ['%s %s' % (prop.name, prop.definition) for prop in definition.__properties__]
        definition.__definition__ = '%s>%s' % (definition.HEADER, ', '.join(definition.__definition_blocks__))
        return definition


class Serializable(object):
    def __new__(cls, **kw):
        obj = super(Serializable, cls).__new__(cls)
        obj.__data__ = {}
        for field in obj.__properties__:
            setattr(obj, field.name, kw.get(field.name, NoDefault))       
        return obj

    def serialize(self):
        data = self.__data__

        row = []
        for field in self.__properties__:
            value = data[field.name]
            if value is NoDefault:
                value = ''
            else:
                value = field._serialize(value)
            row.append(value)

        return ','.join(row)


class NodeMeta(DeclarativeMeta):
    HEADER = 'nodedef'
    PREDEFINED_PROPERTIES = (Name('name', order=-2),
                             Double('x', required=False, order=-1),
                             Double('y', required=False, order=-1), 
                             Boolean('visible', True, order=-1), 
                             Color('color', 'cornflowerblue', required=False, order=-1),
                             Color('strokecolor', 'cadetblue', required=False, order=-1),
                             Boolean('fixed', False, required=False, order=-1),
                             Shape('style', 'RECT', required=False, order=-1),
                             Double('width', 4, required=False, order=-1),
                             Double('height', 4, required=False, order=-1),
                             String('label', SameAs('name'), required=False, order=-1),
                             Boolean('labelvisible', False, required=False, order=-1),
                             Color('labelcolor', SameAs('color'), required=False, order=-1),
                             String('image', required=False, order=-1))


class Node(Serializable):
    __metaclass__ = NodeMeta


class EdgeMeta(DeclarativeMeta):
    HEADER = 'edgedef'
    PREDEFINED_PROPERTIES = (Name('node1', order=-5),
                             Name('node2', order=-4),
                             Boolean('directed', True, required=False, order=-3),
                             Color('color', 'dandelion', required=False, order=-2),
                             Boolean('visible', True, order=-1), 
                             Double('weight', 1, required=False, order=-1),
                             Double('width', 3, required=False, order=-1),
                             String('label', SameAs('weight'), required=False, order=-1),
                             Boolean('labelvisible', False, required=False, order=-1),
                             Color('labelcolor', SameAs('color'), required=False, order=-1))


class Edge(Serializable):
    __metaclass__ = EdgeMeta


class GdfEntries(object):
    def __init__(self, node_type=Node, edge_type=Edge):
        self.node_type = node_type
        self.edge_type = edge_type
        self._nodes = {}
        self._edges = {}

    def add_node(self, node):
        if not isinstance(node, self.node_type):
            raise ValueError('Mismatch between GdfEntries node type and provided node')

        self._nodes[node.name] = node

    def get_node(self, name):
        return self._nodes.get(name)

    @property
    def nodes(self):
        return self._nodes.itervalues()

    def add_edge(self, edge):
        if not isinstance(edge, self.edge_type):
            raise ValueError('Mismatch between GdfEntries edge type and provided edge')

        self._edges[u'%s->%s' % (edge.node1, edge.node2)] = edge

    @property
    def edges(self):
        return self._edges.itervalues()

    def link(self, node1, node2, **kw):
        self.add_edge(self.edge_type(node1=node1, node2=node2, **kw))

    def dumps(self):
        return '\n'.join(chain((self.node_type.__definition__,), 
                               (node.serialize() for node in self.nodes),
                               (self.edge_type.__definition__,),
                               (edge.serialize() for edge in self.edges)))

    def dump(self, fileobj):
        fileobj.write(self.dumps())