# Copyright 2014 healthcheck-as-a-service authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import mock
import json
import os
import unittest

from healthcheck.plugin import (add_url, add_watcher, command, main,
                                remove_watcher, remove_url)


class PluginTest(unittest.TestCase):

    def set_envs(self):
        os.environ["TSURU_TARGET"] = self.target = "https://cloud.tsuru.io/"
        os.environ["TSURU_TOKEN"] = self.token = "abc123"

    def delete_envs(self):
        del os.environ["TSURU_TARGET"], os.environ["TSURU_TOKEN"]

    @mock.patch("urllib2.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_url(self, Request, urlopen):
        self.set_envs()
        self.addCleanup(self.delete_envs)

        request = mock.Mock()
        Request.return_value = request

        add_url("name", "url")

        Request.assert_called_with(
            'POST',
            self.target + 'services/proxy/name?callback=/url',
            data=json.dumps({'url': 'url', 'name': 'name'})
        )

        calls = [
            mock.call("authorization", "bearer {}".format(self.token)),
            mock.call("content-type", "application/x-www-form-urlencoded"),
            mock.call("accept", "text/plain"),
        ]
        request.add_header.has_calls(calls)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("urllib2.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_remove_url(self, Request, urlopen):
        self.set_envs()
        self.addCleanup(self.delete_envs)

        request = mock.Mock()
        Request.return_value = request

        remove_url("name", "url")

        Request.assert_called_with(
            'DELETE',
            self.target + 'services/proxy/name?callback=/name/url/url',
            data=None,
        )
        request.add_header.assert_called_with("Authorization",
                                              "bearer " + self.token)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("urllib2.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_add_watcher(self, Request, urlopen):
        self.set_envs()
        self.addCleanup(self.delete_envs)

        request = mock.Mock()
        Request.return_value = request

        add_watcher("name", "watcher@watcher.com")

        Request.assert_called_with(
            'POST',
            self.target + 'services/proxy/name?callback=/watcher',
            data=json.dumps({'watcher': 'watcher@watcher.com', 'name': 'name'})
        )

        calls = [
            mock.call("authorization", "bearer {}".format(self.token)),
            mock.call("content-type", "application/x-www-form-urlencoded"),
            mock.call("accept", "text/plain"),
        ]
        request.add_header.has_calls(calls)
        urlopen.assert_called_with(request, timeout=30)

    @mock.patch("urllib2.urlopen")
    @mock.patch("healthcheck.plugin.Request")
    def test_remove_watcher(self, Request, urlopen):
        self.set_envs()
        self.addCleanup(self.delete_envs)

        request = mock.Mock()
        Request.return_value = request

        remove_watcher("name", "watcher@watcher.com")

        uri = 'services/proxy/name?callback=/name/watcher/watcher@watcher.com'
        Request.assert_called_with(
            'DELETE',
            self.target + uri,
            data=None,
        )
        request.add_header.assert_called_with("Authorization",
                                              "bearer " + self.token)
        urlopen.assert_called_with(request, timeout=30)

    def test_commands(self):
        expected_commands = {
            "add-url": add_url,
            "add-watcher": add_watcher,
            "remove-url": remove_url,
            "remove-watcher": remove_watcher,
        }
        for key, cmd in expected_commands.items():
            self.assertEqual(command(key), cmd)

    @mock.patch("healthcheck.plugin.add_url")
    def test_main(self, add_url_mock):
        main("add-url", "myhc", "http://tsuru.io")
        add_url_mock.assert_called_with("myhc", "http://tsuru.io")
