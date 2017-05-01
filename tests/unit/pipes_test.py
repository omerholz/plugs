import pytest
from itertools import product
from plugs import pipes


double = lambda x: 2*x
inc = lambda x: 1+x
mirror = lambda x: -x
square = lambda x: x*x

_functions = [double,inc, mirror, square]
_functions_product = product(_functions, repeat=len(_functions))

@pytest.fixture(scope="module")
def random():
    """provide a consistent random instance accross the module
    """
    import random as r
    return r.Random()

@pytest.fixture(scope="module", params=[(-100,100)])
def random_int(request, random):
    a,b = request.param
    return random.randint(a,b)

@pytest.fixture()
def random_string(request, random):
    import string
    LENGTH=10
    return ''.join(random.choice(
        string.ascii_uppercase + string.digits
    ) for _ in range(LENGTH))

@pytest.fixture(scope="module", params=_functions_product)
def functions(request):
    """return a fixture: a list of callables"""

    return request.param

def test_compose(functions, random_int):
    f = pipes.compose(*functions)
    cur = random_int
    for g in functions:
        cur = g(cur)

    f(random_int).should.be.equal(cur)

def test_compose_strings():
    def foo(x=None):
        return x and x+' hello' or 'hello'
    def bar(x=None):
        return x and x+' world' or 'world'
    f = pipes.compose(foo, bar)
    f().should.be.equal('hello world')
    f('another').should.be.equal('another hello world')
    g = pipes.compose(bar, foo)
    g().should.be.equal('world hello')
    g('another').should.be.equal('another world hello')


def test_functional_pipe(functions, random_int):
    p = pipes.FunctionalPipe(*functions)
    cur = random_int
    for g in functions:
        cur = g(cur)

    p (random_int).should.be.equal(cur)

def test_right_connected_pipe(functions, random_int):
    # find the middle of the functions list
    halfway = int(len(functions)/2)

    # split the functions into 2 lists
    first_funcs = functions[:halfway]
    second_funcs = functions[halfway:]

    # we create a pipe for each of them, from left to right
    first = pipes.FunctionalPipe(*first_funcs)
    second = pipes.FunctionalPipe(*second_funcs)

    # we connect the two pipes together
    pipe = first >> second

    # we calculate the result of all the functions, manually
    cur = random_int
    for g in functions:
        cur = g(cur)

    # and we very we get the same result from the connected pipe
    pipe(random_int).should.be.equal(cur)

def test_left_connected_pipe(functions, random_int):
    # find the middle of the functions list
    halfway = int(len(functions)/2)

    # split the functions into 2 lists
    first_funcs = functions[:halfway]
    second_funcs = functions[halfway:]

    # we create a pipe for each of them,
    # this time from right to left
    first = pipes.FunctionalPipe(*first_funcs)
    second = pipes.FunctionalPipe(*second_funcs)

    # we connect the two pipes together
    pipe = second << first

    # we calculate the result of all the functions, manually
    cur = random_int
    for g in functions:
        cur = g(cur)

    # and we very we get the same result from the connected pipe
    pipe(random_int).should.be.equal(cur)

def test_pluggable_strings(random_string):
    # let say we have 2 simple functions:
    def foo(x=None):
        return x and x+' hello' or 'hello'
    def bar(x=None):
        return x and x+' world' or 'world'

    # we wrap these functions in a FunctionalPipe
    hello = pipes.FunctionalPipe(foo)
    world = pipes.FunctionalPipe(bar)
    # we expect the hello FunctionalPipe wrapper pipe to behave like foo function
    hello().should.be.equal('hello')
    hello().should.be.equal(foo())
    hello('say').should.be.equal('say hello')
    hello(random_string).should.be.equal(foo(random_string))

    # and the world FunctionalPipe wrapper to behave like the world function
    world().should.be.equal('world')
    world().should.be.equal(bar())
    world('say').should.be.equal('say world')
    world(random_string).should.be.equal(bar(random_string))

    # when we plug the hello FunctionalPipe to the world FunctionalPipe
    # we get a new FunctionalPipe:
    hello_world = hello >> world

    # we check that our new hello_world FunctionalPipe behave as expected
    hello_world().should.be.equal('hello world')
    hello_world('say').should.be.equal('say hello world')

    # to check that we can plug FunctionalPipes in both direction
    # we plug world into hello and validate the expected behavior
    world_hello = hello << world
    world_hello().should.be.equal('world hello')
    world_hello("don't say").should.be.equal("don't say world hello")

def test_named_args_pass(random_string, random_int):
    # we define a function that takes **kwargs and update a single value
    def update_random_string(*args, **kwargs):
        kwargs['my_string'] = kwargs.get('init_string',random_string)
        return kwargs
    # we wrap it in a pipe
    string_pipe = pipes.FunctionalPipe(update_random_string)
    # when we pass nothing kwargs is an empty dict
    string_pipe().should.equal({'my_string': random_string})

    # let's verify our named arguments are passed
    string_pipe(
        init_int=random_int,
        init_string='test_string'
    ).should.equal({
        'init_int':random_int,
        'init_string': 'test_string',
        'my_string': 'test_string'
    })


def test_sequential_args_pass(random_string, random_int):
    # we define a function that takes some sequential vars
    def update_randoms(init_int, init_string, *args, **kwargs):
        kwargs = dict()
        kwargs['my_string'] = init_string
        kwargs['my_int'] = init_int
        return kwargs
    # we wrap it in a pipe
    string_pipe = pipes.FunctionalPipe(update_randoms)
    # let's verify our named arguments are passed
    string_pipe(
        random_int,
        random_string
    ).should.equal({
        'my_int':random_int,
        'my_string': random_string
    })
    # let's try flipping the order but naming the arguments
    string_pipe(
        init_string=random_string,
        init_int=random_int
    ).should.equal({
        'my_int':random_int,
        'my_string': random_string
    })

def test_multipipe_named_args_pass(random_string, random_int):
    def update_string(*args, **kwargs):
        kwargs['random_string'] = random_string
        return kwargs
    def update_int(*args, **kwargs):
        kwargs['random_int'] = random_int
        return kwargs

    #
    string_pipe = pipes.FunctionalPipe(update_string)
    int_pipe = pipes.FunctionalPipe(update_int)
    # let's define the same multipipe in 2 different ways
    composed_pipe = pipes.FunctionalPipe(update_string, update_int)
    multi_pipe = string_pipe >> int_pipe
    # make sure they yield the same result
    composed_pipe().should.equal(multi_pipe())
    # and that it's the expected result
    multi_pipe().should.equal(
        {'random_int': random_int, 'random_string': random_string}
    )

