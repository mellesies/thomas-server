# Thomas

Thomas' RESTful API and webinterface.

## Installation

### Normal
To install from PyPI use `pip`:

```bash
    pip install thomas-server
```

### Development
To do a development install:

```bash
    git clone https://github.com/mellesies/thomas-server
    cd thomas-server
    pip install -e .
```

### Docker
A Docker image is available for easy deployment. The following command will
start a server, listening on `localhost`, port `5000`:

```bash
    docker run --rm -it -p 5000:5000 mellesies/thomas-server
```

## Usage
Start the server as follows:

```bash
# Load the fixtures (incl. default user root/toor)
thomas load-fixtures --environment=dev

# Start the server (see --help for details)
thomas start
```

Then point your browser towards [localhost](http://localhost:5000/static/index.html).
