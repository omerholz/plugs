import functools

def compose_two(f, g):
    def wrapped(*args, **kwargs):
        ret = g(*args,**kwargs)
        if type(ret) is tuple and len(ret)==2 and type(ret[0]) is tuple and type(ret[1]) is dict:
            return f(*ret[0], **ret[1])
        elif type(ret) is dict:
            return f(**ret)
        elif ret==None:
            return f(*args,**kwargs)
        else:
            return f(ret)
    return wrapped

def compose(*functions):
    functions = reversed(functions)
    return functools.reduce(
        compose_two,
        functions
    )

#TODO: add support for "graphs" with split and merge
class FunctionalPipe(object):
    """this encapsulate a run of a set of transformations on a peace of data.
    This will let us cache a run, including the transformation code,
    as oppose to only reference to the code like in the SQL runs table"""

    def __init__(self, *transformations):
        self._composed = compose(*transformations)

    def __rshift__(self, other):
        if isinstance(other,self.__class__):
            return self.__class__(self._composed, other._composed)
        elif callable(other):
            return self.__class__(self._composed, other)
        else:
            raise Exception('FunctionalPipe >> only supports callables and other FunctionalPipe')

    def __lshift__(self, other):
        if isinstance(other,self.__class__):
            return self.__class__(other._composed, self._composed)
        elif callable(other):
            return self.__class__(other, self._composed)
        else:
            raise Exception('FunctionalPipe >> only supports callables and other FunctionalPipe')

    def __call__(self, *args, **kwargs):
        return self._composed(*args, **kwargs)


