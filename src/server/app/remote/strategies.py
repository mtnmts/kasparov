import app.resources as resources
import re
import time
import logging
from hashlib import sha1
import random
# Installation stratagies


class DebianStrategy(object):

    def __init__(self, server_connection):
        self._server_connection = server_connection
        self._logger = logging.getLogger(__name__)

    def verifyInstallation(self, pkg_name):
        res = self._server_connection.runCommand(
            'apt-cache policy ' + pkg_name)
        if re.match('.*Unable to  locate package ' + pkg_name + ".*", res) or re.match(".*Installed: (none).*", res):
            return False
        return True

        def verifyRemoval(self, pkg_name):
            res = self._server_connection.runCommand(
                'apt-cache policy ' + pkg_name)
            if re.match('.*Unable to  locate package ' + pkg_name + ".*", res) or re.match(".*Installed: (none).*", res):
                return True
            return False

    def installPackage(self, pkg_name):
        res = self._server_connection.runCommand(
            'apt-get install -y -q ' + pkg_name)
        return self.verifyInstallation(pkg_name)

    def uninstallPackage(self, pkg_name):
        res = self._server_connection.runCommand(
            'apt-get remove -y -q ' + pkg_name)
        return self.verifyInstallation(pkg_name)

    def execute(self):
        raise NotImplementedError(
            "Abstract debian strategy can't be executed.")


class NginxStrategy(DebianStrategy):

    def __init__(self, server_connection):
        super(self.__class__, self).__init__(server_connection)

    def execute(self):
        if not self.installPackage('nginx'):
            self._logger.error(
                "Failed installing package nginx in " + str(self.__class__) + " Strategy")
            return False
        self._server_connection.runCommand('mkdir -p /var/www')
        self._server_connection.runCommand(
            'rm -f /etc/nginx/sites-enabled/default')
        data, path = resources.RESOURCE[resources.PHP_CONF_KEY]
        self._server_connection.saveFile(data, path)
        data, path = resources.RESOURCE[resources.DEFAULT_PHP_NGINX_KEY]
        self._server_connection.saveFile(data, path)

        self._server_connection.runCommand('invoke-rc.d nginx restart')
        return not self._server_connection.runCommandAnticipate('cat /run/nginx.pid', '.*No such file*')


class PhpStrategy(DebianStrategy):
    PHP_PACKAGES = ['php5-fpm', 'php5-cli', 'php5-curl', 'php5-gd',
                    'php5-intl', 'php5-mcrypt', 'php-gettext', 'php5-mysql', 'php5-sqlite']

    def __init__(self, server_connection):
        super(self.__class__, self).__init__(server_connection)

    def execute(self):
        if not all([self.installPackage(x) for x in PhpStrategy.PHP_PACKAGES]):
            self._logger.error("Failed installing PHP Packages.")
            return False
        if not any([self.installPackage('php5-apc'), self.installPackage('php-apc')]):
            self._logger.error('Failed installing PHP5 APC')
        self._server_connection.runCommand('invoke-rc.d php5-fpm restart')
        return True


class NewWebsiteStrategy(DebianStrategy):


    def __init__(self, server_connection, site):
        super(self.__class__, self).__init__(server_connection)
        self._site = site
    
    def execute(self):
        site = self._site
        self._server_connection.runCommand('mkdir -p /var/www/' + site + '/public')
        data, path = resources.RESOURCE[resources.SITE_AVAILABLE_KEY]
        path = path.format(site=site)
        data = data.replace('$1', site)
        self._server_connection.saveFile(data, path)
        self._server_connection.runCommand('ln -s /etc/nginx/sites-available/{site}.conf /etc/nginx/sites-enabled/{site}.conf'.format(site=site))
        self._server_connection.runCommand('chown www-data:www-data -R "/var/www/{site}'.format(site=site))
        self._server_connection.runCommand('invoke-rc.d nginx restart')
        self._server_connection.saveFile(data, path)
        #fname = '/var/www/{site}/public/'.format(site=site) + str(random.getrandbits()) + '.txt'
        #fdata = str(random.getrandbits(512))
        #self._server_connection.saveFile(fname, fdata)
        return True

    def get_site_directory(self):
        return "/var/www/{site}".format(self._site)

    def get_http_root(self):
        return "/var/www/{site}/public".format(self._site)

class MysqlStrategy(DebianStrategy):
    PRE_INSTALL_COMMANDS = ' && '.join(['export DEBIAN_FRONTEND="noninteractive"',
                            'echo mysql-server mysql-server/root_password password {passw} | debconf-set-selections',
                            'echo mysql-server mysql-server/root_password_again password {passw} | debconf-set-selections',
                            'apt-get install -y mysql-server'])
    
    def __init__(self, server_connection, sql_pass=None):
        super(self.__class__, self).__init__(server_connection)
        if sql_pass:
            self._sql_pass = sql_pass
        else:
            self._sql_pass = _random_pass()

 
    def execute(self):
        self._server_connection.runCommand(MysqlStrategy.PRE_INSTALL_COMMANDS.format(passw=self._sql_pass))
        if not self.verifyInstallation('mysql-server'):
            self._logger.error("Failed installing MYSQL Server package")
            return False
        self._server_connection.saveFile('[client]\nuser=root\npassword=' + self._sql_pass, '.my.cnf')
        self._server_connection.runCommand('nohup myslqd_safe & 2>&1')
        if not self._server_connection.runCommandAnticipate('ps aux | grep sql', '.*/mysqld.*'):
            self._logger.error("mysqld failed to start")
            return False
        self._logger.error(MysqlStrategy.PRE_INSTALL_COMMANDS.format(passw=self._sql_pass))
        return True

    def get_password(self):
        return self._sql_pass


class WordpressStrategy(DebianStrategy):
    SETUP_WP_COMMANDS = ' && '.join(['cd /tmp',
                         'rm -rf wp_tmp_dir && mkdir wp_tmp_dir && cd wp_tmp_dir',
                         'wget http://wordpress.org/latest.tar.gz',
                         'tar xfz latest.tar.gz',
                         'mv wordpress/* ./'
                         'rmdir ./wordpress/ && rm -f latest.tar.gz'])

    def __init__(self, server_connection, website):
        super(self.__class__, self).__init__(server_connection)
        self._website = website
        self._sql_pass = _random_pass()
        self._sql_user = website.replace('/','').replace('\\','').replace('.','_').replace('-','_') + '_u_wp'
        self._db_name = website.replace('/','').replace('\\','').replace('.','_').replace('-','_') + '_wp'

    def execute(self):
        nws = NewWebsiteStrategy(self._server_connection, self._website)
        if not nws.execute():
            self._logger.error("Failed to create new website for " + self._website)
            return False
        self._prepare_db()
        self._setup_wp(nws.get_http_root())
        return True

    def _prepare_db(self):
        data = resources.WORDPRESS_SQL.format(db_user=self._db_user, db_name=self._db_name, db_pass=self._sql_pass)
        tmp_fpath = '/tmp/wpss.{rand}'.format(rand=str(random.getrandbits(64)))
        self._server_connection.saveFile(data, tmp_fpath)
        self._server_connection.runCommand('mysql < ' + tmp_fpath)

    def _setup_wp(self, doc_root):
        self._server_connection.runCommand(WordpressStrategy.SETUP_WP_COMMANDS)
        self._server_connection.runCommand('mv /tmp/wp_tmp_dir/* ' + doc_root)


def _random_pass():
    # This might be our first login, generate a extremely strong random password
    # temporarily in case we need to switch passwords on login
    # not in use at the moment
    mech = sha1()
    mech.update(str(random.getrandbits(512)))
    return mech.digest().encode('base64').replace('\\','').replace('=','')

