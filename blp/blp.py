import blpapi
import pandas as pd
import numpy as np
import datetime


class BLPRequestError(Exception):
    """ A generic exception raised when there is an issue with the Bloomberg API request.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BLPService:
    """ A wrapper class around Bloomberg API that provides the three standard Bloomberg Excel API functions
        BDP, BDS and BDH functions.
        All calls are blocking and return a (possibly empty) DataFrame object.
        A BLPRequestError is raised when invalid security/field is used.
    """

    def __init__(self, host='localhost', port=8194):
        self._connected = False
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        if not self._connected:
            session_options = blpapi.SessionOptions()
            session_options.setServerHost(self.host)
            session_options.setServerPort(self.port)
            self.session = blpapi.Session(session_options)
            self.session.start()
            self.session.openService('//BLP/refdata')
            self.refDataService = self.session.getService('//BLP/refdata')
            self._connected = True

    def _disconnect(self):
        if self._connected:
            self.session.stop()
            self._connected = False

    def BDH(self, securities, fields, start_date, end_date, **kwargs):
        """ Equivalent to the Excel BDH Function.
        """
        params = {'startDate': start_date,
                  'endDate': end_date,
                  'periodicityAdjustment': 'ACTUAL',
                  'periodicitySelection': 'DAILY',
                  'nonTradingDayFillOption': 'ACTIVE_DAYS_ONLY',
                  'adjustmentNormal': False,
                  'adjustmentAbnormal': False,
                  'adjustmentSplit': True,
                  'adjustmentFollowDPDF': False}

        params.update(kwargs)

        response = self._send_request('HistoricalData', securities, fields, params)

        data = []
        keys = []

        for msg in response:
            security_data = msg.getElement('securityData')
            field_data = security_data.getElement('fieldData')
            field_data_list = [field_data.getValueAsElement(i) for i in range(field_data.numValues())]

            df = pd.DataFrame()

            for field in field_data_list:
                for v in [field.getElement(i) for i in range(field.numElements()) if
                          field.getElement(i).name() != 'date']:
                    df.ix[field.getElementAsDatetime('date'), str(v.name())] = v.getValue()

            df.index = df.index.to_datetime()
            df.replace('#N/A History', np.nan, inplace=True)

            keys.append(security_data.getElementAsString('security'))

            if not df.empty:
                data.append(df)

        # This is to take care of all empty cases
        try:
            data = pd.concat(data, keys=keys, axis=1)
        except ValueError as e:
            data = pd.DataFrame()

        return data

    def BDP(self, securities, fields, **kwargs):
        """ Equivalent to the Excel BDP Function.
        """
        response = self._send_request('ReferenceData', securities, fields, kwargs)

        data = pd.DataFrame()

        for msg in response:
            security_data = msg.getElement('securityData')
            security_data_list = [security_data.getValueAsElement(i) for i in range(security_data.numValues())]

            for sec in security_data_list:
                field_data = sec.getElement('fieldData')
                field_data_list = [field_data.getElement(i) for i in range(field_data.numElements())]

                for fld in field_data_list:
                    data.ix[sec.getElementAsString('security'), str(fld.name())] = fld.getValue()
        return data

    def BDS(self, securities, fields, **kwargs):
        """ Equivalent to the Excel BDS Function.
        """
        response = self._send_request('ReferenceData', securities, fields, kwargs)

        data = []
        keys = []

        for msg in response:
            security_data = msg.getElement('securityData')
            security_date_list = [security_data.getValueAsElement(i) for i in range(security_data.numValues())]

            for sec in security_date_list:
                field_data = sec.getElement('fieldData')
                field_data_list = [field_data.getElement(i) for i in range(field_data.numElements())]

                df = pd.DataFrame()

                for fld in field_data_list:
                    for v in [fld.getValueAsElement(i) for i in range(fld.numValues())]:
                        s = pd.Series()
                        for d in [v.getElement(i) for i in range(v.numElements())]:
                            s[str(d.name())] = d.getValue()
                        df = df.append(s, ignore_index=True)

                if not df.empty:
                    keys.append(sec.getElementAsString('security'))
                    data.append(df)

        data = pd.concat(data, keys=keys, axis=0)
        data.index = data.index.get_level_values(0)

        return data

    def _send_request(self, request_type, securities, fields, elements):
        """ Prepares and sends a request then blocks until it can return 
            the complete response.
            
            Depending on the complexity of your request, incomplete and/or
            unrelated messages may be returned as part of the response.
        """
        request = self.refDataService.createRequest(request_type + 'Request')

        if isinstance(securities, str):
            securities = [securities]
        if isinstance(fields, str):
            fields = [fields]

        [request.append('securities', security) for security in securities]
        [request.append('fields', field) for field in fields]

        if 'ReferenceData' == request_type:
            for k, v in elements.items():
                override = request.getElement('overrides').appendElement()
                override.setElement('fieldId', k)
                override.setElement('value', v)
        else:
            for k, v in elements.items():
                if isinstance(v, datetime.datetime) or isinstance(v, pd.tslib.Timestamp):
                    v = v.strftime('%Y%m%d')
                request.set(k, v)

        self.session.sendRequest(request)

        response = []
        while True:
            event = self.session.nextEvent()
            for msg in event:
                if msg.hasElement('responseError'):
                    raise BLPRequestError('{0}'.format(msg.getElement('responseError')))
                if msg.hasElement('securityData'):
                    if request_type == 'ReferenceData':
                        security_data = msg.getElement('securityData')
                        for i in range(security_data.numValues()):
                            sec = security_data.getValueAsElement(i)
                            if sec.hasElement('fieldExceptions') and (
                                        sec.getElement('fieldExceptions').numValues() > 0):
                                raise BLPRequestError('{0}'.format(sec.getElement('fieldExceptions')))
                            if sec.hasElement('securityError') and (sec.getElement('securityError').numValues() > 0):
                                raise BLPRequestError('{0}'.format(sec.getElement('securityError')))
                    if request_type == 'HistoricalData':
                        security_data = msg.getElement('securityData')
                        if security_data.hasElement('fieldExceptions') and (
                                    security_data.getElement('fieldExceptions').numValues() > 0):
                            raise BLPRequestError(
                                '{0}'.format(security_data.getElement('fieldExceptions')))
                        if security_data.hasElement('securityError'):
                            raise BLPRequestError(
                                '{0}'.format(security_data.getElement('securityError')))

                # no error occurs
                if msg.messageType() == request_type + 'Response':
                    response.append(msg)

            if event.eventType() == blpapi.Event.RESPONSE:
                break

        return response

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._disconnect()

    def __del__(self):
        self._disconnect()
