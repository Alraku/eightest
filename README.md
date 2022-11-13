# Eightest Test Runner

![alt text](docs/images/eightest-logo-wide.png)
-----
## Overview
Eightest is self made test runner written in Python that offers intuitive GUI in order to collect and execute tests suites.
 
## Installation

In order to install use this command:
```pip install eightest```

## Features:
        
- **(WIP)** Graphical User Interface 
- Parallel execution of tests
- Test execution time 
- Custom tags 
- **(WIP)** Automatic scheduler 
- **(WIP)** E-mail notifications 

## Usage

Here is an example of simple Test Suite:
```python
from eightest import TestCase

class TestString(TestCase):

    def before(self):
        # Executed before each test.
        self.text = 'text'

    def test_upper(self):
        assert self.text.upper() == 'TEXT'

    def test_isalpha(self):
        text = 'text'
        assert self.text.isalpha() == True

    def after(self):
        # Executed after each test.
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

# Technologies:

- Python 3.10.6
- Django 4.1.1

## License
[MIT](https://choosealicense.com/licenses/mit/)
