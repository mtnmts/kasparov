# Install the blog!

import time
import paramiko
import random
from hashlib import sha1

IP, PASSWORD = open('secret.txt','rb').readlines()
INSTALLER_SCRIPT = r'https://raw.githubusercontent.com/Xeoncross/lowendscript/master/setup-debian.sh'



SAVE_PATH = r'setup_script.sh'

SLEEP_INTERVAL = 0.1

LAMP_STACK_COMMANDS = ['dropbear 22', 'mysql', 'nginx', 'php', 'site ' + IP, 'mysqluser ' + IP, 'wordpress ' + IP]
CLEANUP =  ['apt-get -q -y update',
			'apt-get -q -y upgrade',
			'apt-get -q -y autoremove']


def create_client():
	c = paramiko.client.SSHClient()
	# Tag client with IP address
	c.ip = IP
	c.load_system_host_keys()
	c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	c.connect(IP, username='root', password=PASSWORD)
	return c

# def bypass_inital_root(client):
# 	# This might be our first login, generate a extremely strong random password (SHA1 of a number 2**64 stringified)
# 	# temporarily in case we need to switch passwords on login
# 	# not in use at the moment
# 	mech = sha1()
# 	sha1.update(str(random.randint(0,2**64 - 1)))
# 	temp_password = sha.digest().encode('base64')
# 	log_info('Setting password to ' + temp_password + ' temporarily!, if something goes wrong/crashes, know this is your password.')


def perform_cleanup_upgrades(client):
	log_info("updating, upgrading and removing unnecessary stuff")
	for cmd in CLEANUP:
		run_command(client, cmd)
	log_info("finished updating")

def install_lamp_stack(client):
	log_info("Installing LAMP Stack")
	for cmd in LAMP_STACK_COMMANDS:
		run_command(client, './' + SAVE_PATH + ' ' + cmd)
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

def log_info(log):
	print "\n{{!}} INFO: " + log

def log_cmd(command):
	print "\n(*!*) Executing: " + command

def log_console(stdout='', stderr=''):
	print '\n'.join(['[!] ' + l for l in stderr.splitlines()])
	print '\n'.join(['[*] ' + l for l in stderr.splitlines()])

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



def main():
	c = create_client()
	fetch_script(c)
	perform_cleanup_upgrades(c)
	install_lamp_stack(c)


main()