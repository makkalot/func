from funcweb.async_tools import AsyncResultManager
from func.overlord.client import Overlord
import unittest

class TestAsyncResultManager(unittest.TestCase):

    def setUp(self):
        self.fc = Overlord("*")
        self.async_manager = AsyncResultManager()

    def test_get_current_list(self):
        pass

    def test_update_current_list(self):
        pass

    def test_check_for_changes(self):
        pass

    def test_select_from(self):
        pass

    def test_job_id_result(self):
        pass

    def test_current_db(self):
        #that test also test the test_get_current_list with no changes option

        result_ids = self.fc.open_job_ids()
        manual_list = {}
        for job_id,code in result_ids.iteritems():
            manual_list[job_id]=[code,self.async_manager.JOB_CODE_NEW]

        real_result =self.async_manager.current_db()
        #print real_result
        assert manual_list ==real_result 


