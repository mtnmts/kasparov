import os
import logging

DEFAULT_PHP_NGINX = open(os.path.join(os.path.dirname(__file__),'res', 'default_php'),'rb').read()
PHP_CONF = open(os.path.join(os.path.dirname(__file__),'res', 'php_conf'),'rb').read()
APC_20 = open(os.path.join(os.path.dirname(__file__),'res', '20_apc_ini'),'rb').read()
SITE_AVAILABLE = open(os.path.join(os.path.dirname(__file__),'res', 'site_available'),'rb').read()
WORDPRESS_SQL = open(os.path.join(os.path.dirname(__file__),'res', 'wordpress_sql_script'),'rb').read()


DEFAULT_PHP_NGINX_KEY = "KEY_PHP_NGINX"
PHP_CONF_KEY = "KEY_PHP_CONF"
APC_20_KEY = "APC_20_KEY"
SITE_AVAILABLE_KEY = "SITE_AVAILABLE_KEY"

RESOURCE = {DEFAULT_PHP_NGINX_KEY : (DEFAULT_PHP_NGINX, r'/etc/nginx/sites-available/default_php'),
			PHP_CONF_KEY : (PHP_CONF, r'/etc/nginx/php.conf'),
			APC_20_KEY : (APC_20, r'/etc/php5/conf.d/20-apc.ini'),
			SITE_AVAILABLE_KEY : (SITE_AVAILABLE, r'/etc/nginx/sites-available/{site}.conf')}