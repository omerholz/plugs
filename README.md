# plugs
plugs is a python library for plug and play algorithms. Plugs let you easily define new algorithms by plugging existing algorithms together in a functional model


## install

```
pip install git+ssh://git@github.com/Sametrica/plugs.git
```

## Use

### FunctionalPipe

The `FunctionalPipe` is the basic unit. `FunctionalPipe` is an object that wrapps around a callable. a `FunctionalPipe` constructor takes any number of callables and chains them together. Once created the `FunctionalPipe` represent a single callable that is the composition of the input callables. Calling the `FunctionalPipe` object will call the function composition

```
>>> from plugs.pipes import FunctionalPipe
>>> inc = lambda x: 1+x
>>> double = lambda x: 2*x
>>> inc_and_double = FunctionalPipe(inc, double)
>>> inc_and_double(10)
22
```

You can chain 2 or more `FunctionalPipe` objects using the `>>` and `<<`
operators

```
>>> inc_pipe = FunctionalPipe(inc)
>>> double_pipe = FunctionalPipe(double)
>>> inc_and_double = inc_pipe >> double_pipe
>>> inc_and_double(10)
22
>>> double_and_inc = inc_pipe << double_pipe
>>> double_and_inc(10)
21
```

### Algorithms

The `sametrica.algorithms` package uses `FunctionalPipe` to compose
discrete operations into a complex algorithm.

```
from sametrica.algorithms import rake, finders, text_utils

long_text = open('/Users/omer/long_text.txt').read()
foo = text_utils.clean_newlines >> rake.keywords
kywords = foo(text=long_text)
```

In a similar mannar we can chain more functions to enrich our foo
algorithm:

```
foo = text_utils.clean_newlines >> rake.keywords >> text_utils.tokenize(nltk.sent_tokenize) >> finders.occurrences >> finders.single_word_snippet
kywords = foo(text=long_text)
```

#### Cross-Occurrences

We can build an algorithm to find cross occurrences by cleaning the
text, finding keywords, tokenizing the text and then finding crossoccurrences:

```
>>> from sametrica.algorithms import rake, finders, text_utils; import nltk
>>> text = open('/Users/omer/text.txt','r').read()
>>> foo = text_utils.clean_newlines >> rake.keywords >> text_utils.tokenize(nltk.sent_tokenize) >> finders.crossoccurrences
```

At this point foo is our algorithm. Any text we run through it will be
search for crossoccurrences

```
>>> result = foo(text=text)
>>> k = list(result['crossoccurrences'].keys())[0]
>>> k
frozenset({'summative evaluation', 'budget 2008', 'student loans', 'program', 'canada', 'enhancements'})
>>> result['crossoccurrences'][k]
[{'snippet': ['A summative evaluation of the Budget 2008 Canada Student Loans Program (CSLP) enhancements has been underway since 2010 and is scheduled for completion by March 2016.']}]
```

### Examples

See tests.

To run test: `pytest -v -s`

### argument passing

Rules argument passing are still changing. TBD
