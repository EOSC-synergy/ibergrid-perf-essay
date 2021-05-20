import unittest

from eosc_perf.controller.io_controller import controller
from eosc_perf.model.facade import DatabaseFacade
from eosc_perf.tests.controller.controller.controller_test_base import IOControllerTestBase


class ControllerUserTests(IOControllerTestBase):
    def setUp(self):
        """Called before each test."""
        super().setUp()

    def test_add_current_user_if_missing(self):
        with self.app.test_request_context():
            self.assertRaises(DatabaseFacade.NotFoundError, self.facade.get_uploader, controller.get_user_id())
            self.controller._add_current_user_if_missing()
            self.assertTrue(self.facade.get_uploader(controller.get_user_id()))
            self.controller._add_current_user_if_missing()
            self.assertTrue(self.facade.get_uploader(controller.get_user_id()))


if __name__ == '__main__':
    unittest.main()
