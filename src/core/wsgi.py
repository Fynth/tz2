import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add the src directory to the Python path
# This allows imports relative to 'src' directory (e.g., 'core', 'api')
src_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(src_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_wsgi_application()
