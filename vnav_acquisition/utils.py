import os

def get_flask_port():
    """Reads the Flask port number from flask_port.txt (in the same directory)."""
    port_file_path = os.path.join(os.path.dirname(__file__), 'flask_port.txt')
    if os.path.exists(port_file_path):
        with open(port_file_path, 'r') as f:
            return f.read().strip()
    else:
        raise Exception("Flask port file not found.")