#!/usr/bin/env python2

import linuxcnc
import logging


class mdiCodeExec:

    def exe(self, code):
        self.command.mdi(code)
        return self.command.wait_complete(self.timeout)

    def sessionStart(self):
        self.stat.poll()
        self.prevMode = self.stat.task_mode
        self.command.mode(linuxcnc.MODE_MDI)
        assert self.command.wait_complete(self.timeout) == linuxcnc.RCS_DONE
        self.sessionStarted = True

    def sessionFinish(self):
        self.command.mode(self.prevMode)
        assert self.command.wait_complete(self.timeout) == linuxcnc.RCS_DONE
        self.sessionStarted = False

    def __init__(self, timeout=30.0):
        self.command = linuxcnc.command()
        self.stat = linuxcnc.stat()
        self.logger = logging.getLogger(__name__)
        self.sessionStarted = False
        self.timeout = timeout
        self.sessionStart()
        self.logger.debug("Started MDI session, previous mode "
                          "is {}".format(self.prevMode))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.sessionFinish()
        self.logger.debug("Finished MDI session, "
                          "returned mode {}".format(self.prevMode))


# Code for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    c = linuxcnc.command()
    c.mode(linuxcnc.MODE_MANUAL)
    logger.debug("LinuxCNC mode switched to MANUAL to "
                 "test mode returning.")

    with mdiCodeExec() as mdi:

        mdi.exe("G91")  # Incremental distance mode

        assert mdi.exe("G38.2 X0.1 F50") == linuxcnc.RCS_ERROR
        logger.debug("Non-tripped G38.2 probing returned RCS_ERROR correctly.")

        assert mdi.exe("G38.3 X0.1 F50") == linuxcnc.RCS_DONE
        logger.debug("Non-tripped G38.3 probing returned RCS_DONE correctly.")

        mdi.timeout = 1.0
        assert mdi.exe("G1 X2 F60") == -1  # Timeout
        mdi.timeout = 30.0

        mdi.exe("G90")

    logger.debug("Successfully finished the MDI sesion. LinuxCNC should be in "
                 "MANUAL mode now.")
