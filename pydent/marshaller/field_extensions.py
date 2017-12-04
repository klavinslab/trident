"""
Module containing custom :class:`marshmallow.fields`.
"""

import json

from marshmallow import fields, ValidationError


class JSON(fields.Field):
    """A custom JSON field"""

    def _serialize(self, value, attr, obj):
        if value is None:
            return ''
        try:
            return json.dumps(value)
        except TypeError as e:
            raise ValidationError(e)

    def _deserialize(self, value, attr, data):
        if value is None:
            return ''
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError as e:
            raise ValidationError(e)

    default_error_message = {
        'invalid': 'field was unable to be parsed as a JSON'
    }


class Relation(fields.Nested):
    """Defines a nested relationship with another model. Is a subclass of :class:`Nested`.

    Uses "callback" with "params" to find models. Callback is
    applied to the model that is fullfilling this relation. Params may include lambdas
    of the form "lambda self: <do something with self>" which passes in the model
    instance.
    """

    def __init__(self, model, callback, params, *args, allow_none=True, **kwargs):
        """Relation initializer.

        :param model: target model
        :type model: basestring
        :param args: positional parameters
        :type args:
        :param callback: function to use in Base to find model
        :type callback: basestring or callable
        :param params: tuple or list of variables (or callables) to use to search for the model. If param is
        a callable, the model instance will be passed in.
        :type params: tuple or list
        :param kwargs: rest of the parameters
        :type kwargs:
        """
        # if kwargs.get("load_only", None) is None:
        #     kwargs["load_only"] = True  # note that "load_only" is important and prevents dumping of all relationships
        super().__init__(model, *args, allow_none=allow_none, **kwargs)
        self.callback = callback
        self.default = None
        # force params to be an iterable
        if not isinstance(params, (list, tuple)):
            params = (params,)
        self.params = params

    def get_default(self):
        """Get the default value for this relation.

        * If self.default is a type, return a new instance of that type
        * If self.default is not None, return self.default
        * If default is None and self.many, return a new list
        * Else return None
        """
        if self.default is not None:
            if type(self.default) == type:
                return self.default()
            else:
                return self.default
        elif self.many:
            return []
        else:
            return None

    @property
    def model(self):
        return self.nested

    def _serialize(self, nested_obj, attr, obj):
        dumped = None

        def decompose_opts(attr, opts):
            if isinstance(opts, dict):
                if attr in opts:
                    opts = opts[attr]
                else:
                    opts = {}
            else:
                opts = {}
            return opts

        def dump(nobj):
            if hasattr(nobj, 'dump'):
                # decompose only if its a dictionary
                only = self.root.original_only
                relations = self.root.dump_relations
                only = decompose_opts(attr, only)
                relations = decompose_opts(attr, relations)
                # deserialize field
                nobj = nobj.dump(only=only,
                                 relations=relations,
                                 _depth=self.root._depth + 1,
                                 depth=self.root.dump_depth,
                                 all_relations=self.root.all_relations)
            return nobj

        if nested_obj:
            if isinstance(nested_obj, list):
                dumped = []
                for x in nested_obj:
                    xdumped = None
                    if x is not None:
                        xdumped = dump(x)
                    dumped.append(xdumped)
            else:
                dumped = dump(nested_obj)
        return dumped

    def __repr__(self):
        return "<{} (model={}, callback={}, params={})>".format(self.__class__.__name__,
                                                                self.nested, self.callback, self.params)

fields.Relation = Relation
fields.JSON = JSON