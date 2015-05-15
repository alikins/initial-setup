#
# initial_setup_log.py: Support for logging to syslog during the
#                       Initial Setup run
#
# Copyright (C) 2014  Red Hat, Inc.  All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s): Martin Kolman <mkolman@redhat.com>

import logging
import sys

from logging.handlers import SysLogHandler, SYSLOG_UDP_PORT


# pip install logging-tree
import logging_tree
# pip install rainbow-logging-handler
import rainbow_logging_handler


class InitialSetupSyslogHandler(SysLogHandler):
    """A SysLogHandler subclass that makes sure the Initial Setup
    messages are easy to identify in the syslog/Journal
    """
    def __init__(self,
                 address=('localhost', SYSLOG_UDP_PORT),
                 facility=SysLogHandler.LOG_USER,
                 tag=''):
        self.tag = tag
        SysLogHandler.__init__(self, address, facility)

    def emit(self, record):
        original_msg = record.msg
        # this is needed to properly show the "initial-setup" prefix
        # for log messages in syslog/Journal
        record.msg = '%s: %s' % (self.tag, original_msg)
        SysLogHandler.emit(self, record)
        record.msg = original_msg


class ColorHandler(rainbow_logging_handler.RainbowLoggingHandler):
    def __init__(self, *args, **kwargs):
        super(ColorHandler, self).__init__(*args, **kwargs)

        self.boldiness = True
        self.color_map['not_as_dark'] = 5
        self.bg_color = None

    def _alternate(self):
        self.boldiness = not self.boldiness
        return self.boldiness

    def _alternate_bg(self):
        if self.boldiness:
            self.bg_color = 'white'
            # self.bg_color = 'red'
        else:
            self.bg_color = 'black'
            return self.bg_color

    def emit(self, record):
        a = self._alternate()
        self._column_color['%(name)s'] = ('yellow', None, False)
        self._column_color['%(message)s'][logging.DEBUG] = ('white', None, a)
        return super(ColorHandler, self).emit(record)


def init():
    """Initialize the Initial Setup logging system"""
    log = logging.getLogger("initial-setup")
    log.setLevel(logging.DEBUG)
    # syslogHandler = InitialSetupSyslogHandler('/dev/log',
    #                                          SysLogHandler.LOG_LOCAL1,
    #                                          "initial-setup")
    # syslogHandler.setLevel(logging.DEBUG)
    # log.addHandler(syslogHandler)
    # stream_handler = logging.StreamHandler()
    stream_handler = ColorHandler(sys.stderr,
                                  color_name=('yellow', None, True),
                                  datefmt=None)
    # %(process)d):%(threadName)s
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(lineno)s "
                                  "%(name)s:[%(process)d:%(threadName)s] "
                                  "- %(message)s")
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    logging.getLogger('anaconda').addHandler(stream_handler)
    logging.getLogger('anaconda').setLevel(logging.DEBUG)

    logging.getLogger('rhsm_gui').addHandler(stream_handler)
    logging.getLogger('rhsm_gui').setLevel(logging.DEBUG)

    logging.getLogger('').addHandler(stream_handler)
    logging.getLogger('').setLevel(logging.DEBUG)

    # anaconda/initial-setup/rhsm/subscription-manager log setup is a little
    # complicated, so the 'logging_tree' module dumps out it's current state
    logging_tree.printout()
