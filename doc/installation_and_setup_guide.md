# Installation and Setup Guide

### Clone the project:
```bash
git clone git@github.com:opturtio/ElevateR.git
```

### Go to repository:
```bash
cd ElevateR
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

### Create your own secret key using Python interpreter:
**Run command:**
```bash
python3
```
**Run commands in interpreter and copy the secret key:**
```python
import secrets
secrets.token_hex(16)
```

**Example secret key:**
```python
SECRET_KEY=18fd24bf6a2ad4dac04a33963db1c42f
```

### Add the two lines to the .env file
```python
DATABASE_URL=postgresql:///user
SECRET_KEY="THE SECRET KEY YOU CREATED"
```

### Run program:
```bash
flask run
```

### Copy local address to your browser:
```bash
http://127.0.0.1:5000/
```
