import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import create_app, app

if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Karpagam College Backend WSGI server on port {port}...")
    serve(app, host='0.0.0.0', port=port)

