import app.resources as resources
import re
import logging
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
        # APC Disabled for now
        #data, path = resources.RESOURCE[resources.APC_20_KEY]
        #self._logger.error("PATH: " + path)
        #self._server_connection.saveFile(data, path)
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
        return True
