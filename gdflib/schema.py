NoDefault = object()

class UnserializableSchemaItem(Exception):
    pass

class InvalidSchemaItem(Exception):
    pass

class SameAs(object):
    def __init__(self, other):
        self.other = other

    def _resolve(self, obj):
        return getattr(obj, self.other, NoDefault)

class SchemaItem(object):
    def __init__(self, name=NoDefault, default=NoDefault, required=True, order=0):
        self.default = default
        self.name = name
        self.required = required
        self.order = order

    def _serialize(self, value):
        raise UnserializableSchemaItem('%s cannot be serialized' % self.__class__.__name__)

    def _validate(self, obj, value):
        if value is NoDefault:
            value = self.default

        if isinstance(value, SameAs):
            value = value._resolve(obj)

        if self.required and value is NoDefault:
            raise InvalidSchemaItem('%s:%s is required' % (self.__class__.__name__, self.name))

        return value

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        return instance.__data__.get(self.name, self.default)
        
    def __set__(self, instance, value):
        instance.__data__[self.name] = self._validate(instance, value)

    def __delete__(self, instance):
        instance.__data__.pop(self.name, None)

class Double(SchemaItem):
    definition = 'DOUBLE'

    def _serialize(self, value):
        return '%f' % value

class String(SchemaItem):
    definition = 'VARCHAR'

    def _serialize(self, value):
        return "'%s'" % unicode(value).encode('utf-8')

class Name(SchemaItem):
    definition = ''

    def _serialize(self, value):
        return "%s" % unicode(value).encode('utf-8')

class Integer(SchemaItem):
    definition = 'INT'

    def _serialize(self, value):
        return '%d' % value

class Boolean(SchemaItem):
    definition = 'BOOLEAN'

    def _serialize(self, value):
        return ('false', 'true')[bool(value)]

class Color(String):
    def _serialize(self, value):
        if isinstance(value, (tuple, list)):
            return "'%s,%s,%s'" % value
        else:
            return str(value)

class Shape(Integer):
    SHAPES = (None, 'RECT', 'ELLIPSE', 'ROUNDED_RECT', 'TEXT_RECT', 'TEXT_ELLIPSE', 'TEXT_ROUNDED_RECT', 'IMAGE')

    def _serialize(self, value):
        if value not in self.SHAPES:
            raise UnserializableSchemaItem('%s is not a valid shape %s' % (value, self.SHAPES))
        return '%s' % self.SHAPES.index(value)

