import subprocess
import sys
import time
s = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)
s.stdin.write("kill -9 $(ps aux | grep run_flask.py | awk '{print $2}')\n")
s.stdin.write("kill -9 $(ps aux | grep run_autobahn.py | awk '{print $2}')\n")
time.sleep(1)
s.stdin.write('python server/run_flask.py &\n')
s.stdin.write('python server/run_autobahn.py &\n')
s.wait()

