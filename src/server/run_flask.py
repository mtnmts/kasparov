from app.server import app
from app.installer_component import installer_service
import threading


app.run(port=8080)