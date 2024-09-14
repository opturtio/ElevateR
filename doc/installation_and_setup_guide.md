# Installation and Setup Guide

### Clone the project:
```bash
git clone git@github.com:opturtio/ElevateR.git
```

### Go to repository:
```bash
cd Elevater
```

### Install virtual environment:
```bash
python3 -m venv venv
```

### Start virtual environment:
```bash
source venv/bin/activate
```

### Install requirements:
```bash
pip install -r requirements.txt
```

### Create .env-file:
```bash
touch .env
```

### Add the two lines to the .env file
DATABASE_URL=postgresql:///user

SECRET_KEY="THE SECRET KEY YOU CREATED"

### Create your own secret key using Python interpreter:
```bash
python3
```
```python
>>> import secrets
>>> secrets.token_hex(16)
'18fd24bf6a2ad4dac04a33963db1c42f'
```

**Example secret key**
SECRET_KEY=18fd24bf6a2ad4dac04a33963db1c42f

### Run program:
```bash
flask run
```

### Copy local address to your browser:
```bash
http://127.0.0.1:5000/
```