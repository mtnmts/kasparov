# Install the blog!

import time
import paramiko
import random
from hashlib import sha1
from StringIO import StringIO

INSTALLER_SCRIPT = r'https://raw.githubusercontent.com/Xeoncross/lowendscript/master/setup-debian.sh'



SAVE_PATH = r'setup_script.sh'

SLEEP_INTERVAL = 0.1

LAMP_STACK_COMMANDS = ['dropbear 22', 'nginx', 'php'] #'mysqluser ' + IP, 'wordpress ' + IP]
CLEANUP =  ['apt-get -q -y update',
			'apt-get -q -y upgrade',
			'apt-get -q -y autoremove']


def create_client(ip,user,passw):
	c = paramiko.client.SSHClient()
	# Tag client with IP address
	c.ip = ip
	c.load_system_host_keys()
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	log("Attempting to connect to " + ip + " at port 22 with SSH")
	c.connect(ip, username=user, password=passw)
	return c


def sftp_client(client):
	return paramiko.SFTPClient.from_transport(client.get_transport())

def random_pass():
	# This might be our first login, generate a extremely strong random password
	# temporarily in case we need to switch passwords on login
	# not in use at the moment
	mech = sha1()
	mech.update(str(random.getrandbits(512)))
	return mech.digest().encode('base64').replace('\\','').replace('=','')
 	


def perform_cleanup_upgrades(client):
	log_info("updating, upgrading and removing unnecessary stuff")
	for cmd in CLEANUP:
		run_command(client, cmd)
	log_info("finished updating")


def install_mysql(client):
	log_info("Installing MYSQL")
	sql_pass = random_pass()
	log_info("Installing with password " + sql_pass)
	run_command(client, 'export DEBIAN_FRONTEND="noninteractive"')
	run_command(client, 'sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password "' + sql_pass)
	run_command(client, 'sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password "' + sql_pass)
	run_command(client, 'apt-get install -y mysql-server')
	sfc = sftp_client(client)
	log_info("Uploading my.cnf")
	sfc.putfo(StringIO('[client]\nuser=root\npassword=' + sql_pass), '.my.cnf')
	log_info("Rebooting MYSQLD_SAFE quietly")
	run_command(client, 'nohup myslqd_safe & 2>&1')
	log_info("Waiting for MYSQL to run (1s)")
	time.sleep(1)
	stdd, stde = run_command(client, 'ps aux | grep sql')
	out = stdd + stde
	success = None
	if "/mysqld" in out:
		success = True
		log_info("MYSQL Is running fine!")
	else:
		success = False
		log_info("Uh oh!, MYSQL is not rnuning")
	return (success, sql_pass)

def install_lamp_stack(client):
	log_info("Installing LAMP Stack")
	for cmd in LAMP_STACK_COMMANDS:
		run_command(client, './' + SAVE_PATH + ' ' + cmd)
	run_command(client, 'apt-get install -y php5-mysql')
	log_info("LAMP Stack installed")


def run_command(client, command):
	''' Returns (stdout, stderr) output '''
	log_cmd(command)
	stdin,stdout,stderr = client.exec_command(command)
	wait_for_close(stderr.channel)
	wait_for_close(stdout.channel)

	stdd, stde = stdout.read(), stderr.read()
	log_console(stdd, stde)

	return (stdd, stde)

def log(msg):
	print msg

def log_info(msg):
	log("INFO: " + msg)

def log_cmd(command):
	log("Executing: " + command)

def log_console(stdout='', stderr=''):
	log('\n'.join(['[STDERR] ' + l for l in stderr.splitlines()]))
	log('\n'.join(['[STDOUT] ' + l for l in stderr.splitlines()]))

def fetch_script(client):
	run_command(client, 'wget --no-check-certificate ' + INSTALLER_SCRIPT + ' -O ' + SAVE_PATH)
	run_command(client, 'chmod +x ' + SAVE_PATH)


def wait_for_close(channel, max_sleep = 600):
	total = 0
	while not channel.closed and total < max_sleep:
		time.sleep(SLEEP_INTERVAL)
		total += SLEEP_INTERVAL
	if total > max_sleep:
		raise Exception("Sleep time exceeded while waiting for channel to close.")



# def main():
# 	c = create_client()
# 	fetch_script(c)
# 	perform_cleanup_upgrades(c)
# 	sql_pass = install_lamp_stack(c)
# 	print "\n" * 4
# 	print "-" * 80
# 	print "[*] Installation Completed! Wordpress Live at " + IP
# 	print "[*] Root SQL Password: " + sql_pass
# 	print "-" * 80
