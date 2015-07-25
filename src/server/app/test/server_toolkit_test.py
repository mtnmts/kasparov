import requests
import unittest
import os
import logging
import app.remote.server_connection as st
import app.remote.strategies as strat
import subprocess
import time
from nose.plugins.attrib import attr

logging.basicConfig(level=logging.INFO)

HOST, PASSWORD, USER = '10.0.0.6', 'hello', 'root'

class ServerTest(unittest.TestCase):
	def setUp(self):
		self._logger = logging.getLogger(__name__)
		
	@attr("website")
	@attr("nginx")
	@attr("blog")
	def test_install_nginx(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		self.assertTrue(sc.connect())
		self.assertTrue(sc.verify())
		ngst = strat.NginxStrategy(sc)
		self.assertTrue(ngst.execute())

	def test_connection(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		sc = sc.connect()
	

	def test_verify_unconnected(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		self.assertFalse(sc.verify())

	def test_verify(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		self.assertTrue(sc.connect())
		self.assertTrue(sc.verify())

	@attr("blog")
	def test_install_php(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		self.assertTrue(sc.connect())
		self.assertTrue(sc.verify())
		ngst = strat.PhpStrategy(sc)
		self.assertTrue(ngst.execute())

	@attr("website")
	def test_install_website(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		self.assertTrue(sc.connect())
		self.assertTrue(sc.verify())
		ngst = strat.NewWebsiteStrategy(sc, '10.0.0.6')
		self.assertTrue(ngst.execute())

	@attr("blog")
	@attr("sql")
	def test_install_mysql(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		self.assertTrue(sc.connect())
		self.assertTrue(sc.verify())
		ngst = strat.MysqlStrategy(sc,"coolestpasswords")
		self.assertTrue(ngst.execute())

	@attr("blog")
	@attr("wp")
	def test_install_wp(self):
		sc = st.ServerConnection(USER, PASSWORD, HOST)
		self.assertTrue(sc.connect())
		self.assertTrue(sc.verify())
		ngst = strat.WordpressStrategy(sc,"10.0.0.6")
		self.assertTrue(ngst.execute())

