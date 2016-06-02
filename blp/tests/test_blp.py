import unittest
from datetime import datetime
from blp import blp

class TestBLPService(unittest.TestCase):

    def setUp(self):
        self.blp_service = blp.BLPService()

    def test_BDP(self):
        pass

    def test_BDS(self):
        pass

    def test_BDH_single_sec_single_field(self):
        print(self.blp_service.BDH('IBM US Equity', 'PX_LAST', '20141231', '20150131'))

    def test_BDH_single_sec_multi_fields(self):
        print(self.blp_service.BDH('IBM US Equity', ['PX_LAST', 'PX_VOLUME'], datetime(2014, 12, 31),
                                   datetime(2015, 1, 31)))

    def test_BDH_multi_secs_multi_fields(self):
        print(
            self.blp_service.BDH(['IBM US Equity', 'JPM US Equity'], ['PX_LAST', 'PX_VOLUME'], '20141231', '20150131'))

    def test_BDH_extra_field(self):
        print(
            self.blp_service.BDH('IBM US Equity', 'PCT_CHG_INSIDER_HOLDINGS', '20141231', '20150131',
                                 periodicitySelection='WEEKLY'))

    def test_BLP_as_context_manager(self):
        # The BLPService Class can also be used as a ContextManager.
        with blp.BLPService() as blp_service:
            # Requesting a single security/field or multiple securities or fields will return a DataFrame.
            print(blp_service.BDP('IBM US Equity', 'GICS_SECTOR'))
            print(blp_service.BDP(['IBM US Equity', 'VOD LN Equity'], ['SECURITY_NAME_REALTIME', 'LAST_PRICE']))

            # You may force any request to return a DataFrame by passing the arguments as lists.
            print(blp_service.BDP(['IBM US Equity'], ['NAME_RT']))

            # Requesting a single security and field will return a DataFrame.
            print(blp_service.BDS('IBM US Equity', 'EQY_DVD_ADJUST_FACT'))

            # You may request multiple securities and/or fields.
            # This feature is generally not useful as the resulting DataFrame is ugly.
            print(blp_service.BDS(['IBM US Equity', 'VOD LN Equity'], 'PG_REVENUE'))
            print(blp_service.BDS('IBM US Equity', ['EQY_DVD_ADJUST_FACT', 'DVD_HIST_ALL']))

    def tearDown(self):
        self.blp_service._disconnect()
