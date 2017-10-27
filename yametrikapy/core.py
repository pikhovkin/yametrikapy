# coding: utf-8

import json

from .client import APIClient


class BaseClass(object):
    pass


class ClientError(Exception):
    pass


class BadRequestError(ClientError):
    """ 400 http-status """
    pass


class UnauthorizedError(ClientError):
    """ 401 http-status """
    pass


class ForbiddenError(ClientError):
    """ 403 http-status """
    pass


class NotFoundError(ClientError):
    """ 404 http-status """
    pass


class MethodNotAllowedError(ClientError):
    """ 405 http-status """
    pass


class APIException(Exception):
    pass


class JSON2Obj(object):
    def __init__(self, page):
        self.__dict__ = json.loads(page.decode())


class Metrika(object):
    """ Class for the API of Yandex Metrika
    """
    HOST = 'https://api-metrika.yandex.ru/'
    OAUTH_TOKEN = 'https://oauth.yandex.ru/token'

    VERSION = 'v1'

    MANAGEMENT = 'management/%s' % VERSION

    COUNTERS = MANAGEMENT + '/counters'
    COUNTER = MANAGEMENT + '/counter/%d'
    COUNTER_UNDELETE = COUNTER + '/undelete'
    COUNTER_GOALS = COUNTER + '/goals'
    COUNTER_GOAL = COUNTER + '/goal/%d'
    COUNTER_FILTERS = COUNTER + '/filters'
    COUNTER_FILTER = COUNTER + '/filter/%d'
    COUNTER_OPERATIONS = COUNTER + '/operations'
    COUNTER_OPERATION = COUNTER + '/operation/%d'
    COUNTER_GRANTS = COUNTER + '/grants'
    COUNTER_GRANT = COUNTER + '/grant'

    DELEGATES = MANAGEMENT + '/delegates'
    DELEGATE = MANAGEMENT + '/delegate'
    ACCOUNTS = MANAGEMENT + '/accounts'
    ACCOUNT = MANAGEMENT + '/account'
    CLIENTS = MANAGEMENT + '/clients'
    LABELS = MANAGEMENT + '/labels'
    LABEL = MANAGEMENT + '/label/%d'

    COUNTER_LABEL = COUNTER + '/label/%d'
    COUNTER_API_SEGMENT = COUNTER + '/apisegment'
    COUNTER_API_SEGMENT_SEGMENTS = COUNTER_API_SEGMENT + '/segments'
    COUNTER_API_SEGMENT_SEGMENT = COUNTER_API_SEGMENT + '/segment/%d'
    COUNTER_USER_PARAMS = COUNTER + '/user_params'
    COUNTER_USER_PARAMS_UPLOADINGS = COUNTER_USER_PARAMS + '/uploadings'
    COUNTER_USER_PARAMS_UPLOADING = COUNTER_USER_PARAMS + '/uploading/%d'
    COUNTER_USER_PARAMS_UPLOADING_CONFIRM = COUNTER_USER_PARAMS_UPLOADING + '/confirm'
    COUNTER_USER_PARAMS_UPLOADINGS_UPLOAD = COUNTER_USER_PARAMS_UPLOADINGS + '/upload'
    COUNTER_OFFLINE_CONVERSIONS = COUNTER + '/offline_conversions'
    COUNTER_OFFLINE_CONVERSIONS_CALLS_EXTENDED_THRESHOLD = COUNTER_OFFLINE_CONVERSIONS + '/calls_extended_threshold'
    COUNTER_OFFLINE_CONVERSIONS_UPLOAD_CALLS = COUNTER_OFFLINE_CONVERSIONS + '/upload_calls'
    COUNTER_OFFLINE_CONVERSIONS_CALLS_UPLOADINGS = COUNTER_OFFLINE_CONVERSIONS + '/calls_uploadings'
    COUNTER_OFFLINE_CONVERSIONS_CALLS_UPLOADING = COUNTER_OFFLINE_CONVERSIONS + '/calls_uploading/%d'
    COUNTER_OFFLINE_CONVERSIONS_EXTENDED_THRESHOLD = COUNTER_OFFLINE_CONVERSIONS + '/extended_threshold'
    COUNTER_OFFLINE_CONVERSIONS_UPLOAD = COUNTER_OFFLINE_CONVERSIONS + '/upload'
    COUNTER_OFFLINE_CONVERSIONS_UPLOADINGS = COUNTER_OFFLINE_CONVERSIONS + '/uploadings'
    COUNTER_OFFLINE_CONVERSIONS_UPLOADING = COUNTER_OFFLINE_CONVERSIONS + '/uploading/%d'

    STAT = 'stat/%s' % VERSION

    STAT_DATA = STAT + '/data'
    STAT_DATA_DRILLDOWN = STAT_DATA + '/drilldown'
    STAT_DATA_BYTIME = STAT_DATA + '/bytime'
    STAT_DATA_COMPARISON = STAT_DATA + '/comparison'
    STAT_DATA_COMPARISON_DRILLDOWN = STAT_DATA_COMPARISON + '/drilldown'

    def __init__(self, client_id, client_secret='', token='', code=''):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token = token
        self._code = code

        self._client = APIClient()
        self._client.user_agent = 'yametrikapy'
        self._data = ''

    @property
    def user_agent(self):
        return self._client.user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        self._client.user_agent = user_agent

    def _get_response_object(f):
        def wrapper(self):
            obj = JSON2Obj(self._data)

            if hasattr(obj, 'errors'):
                if hasattr(obj, 'message'):
                    raise APIException(u'{}: {}'.format(obj.code, obj.message))

                raise APIException(u'{}: {}'.format(obj.code, '\n'.join([error['message'] for error in obj.errors])))

            if hasattr(obj, 'message'):
                raise APIException(obj.message)

            return f(self, obj)

        return wrapper

    @_get_response_object
    def _authorize_handle(self, obj):
        if hasattr(obj, 'access_token'):
            self._token = obj.access_token

    def _authorize(self):
        params = {
            'client_id': self._client_id
        }

        if self._code:
            params['grant_type'] = 'authorization_code'
            params['client_secret'] = self._client_secret
            params['code'] = self._code

        self._data = self._client.request('POST', self.OAUTH_TOKEN, params=params)
        self._authorize_handle()

    def _auth(f):
        def wrapper(self, *args, **kwargs):
            if not self._token:
                self._authorize()

            return f(self, *args, **kwargs)

        return wrapper

    def _headers(self):
        header = {
            'User-Agent': self.user_agent,
            'Accept': 'application/x-yametrika+json',
            'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
            'Authorization': 'OAuth %s' % self._token
        }
        return header

    @_get_response_object
    def _response_handle(self, obj):
        return obj

    @_auth
    def _get_data(self, method, uri, params=None):
        self._data = self._client.request(method, uri, params=params, headers=self._headers())

        if self._client.status == 400:
            raise BadRequestError('%d %s' % (self._client.status, 'Check your request'))
        if self._client.status == 401:
            raise UnauthorizedError('%d: %s' % (self._client.status, 'Check your token'))
        if self._client.status == 403:
            raise ForbiddenError('%d: %s' % (self._client.status, 'Check your access rigths to object'))
        if self._client.status == 404:
            raise NotFoundError('%d: %s' % (self._client.status, 'Resource not found'))
        if self._client.status == 405:
            allowed = self._client.get_header('Allowed')
            raise MethodNotAllowedError('%d: %s\nUse %s' % (self._client.status, 'Method not allowed', allowed))

        return self._response_handle()

    def _get_uri(self, methodname, **params):
        uri = '%s%s.json' % (self.HOST, methodname)

        if params:
            uri += '?%s' % self._client.urlencode(**params)

        return uri

    def get_data(self):
        return self._data

    def _get_all_pages(attr_data, *attrs):
        def wrapper(f):
            def func(self, *args, **kwargs):
                offset = kwargs.get('offset', 1)
                per_page = kwargs.get('per_page', 1000)

                kwargs['offset'] = offset
                kwargs['per_page'] = per_page

                obj = f(self, *args, **kwargs)
                result = BaseClass()
                setattr(result, attr_data, [])
                attr = getattr(result, attr_data)
                attr.extend(getattr(obj, attr_data))

                for a in attrs:
                    if getattr(obj, a):
                        setattr(result, a, getattr(obj, a))

                rows = getattr(obj, 'rows', 0)

                while rows > offset * per_page:
                    offset += per_page

                    kwargs['offset'] = offset

                    obj = f(self, *args, **kwargs)
                    attr.extend(getattr(obj, attr_data))

                return result

            return func

        return wrapper

    # Counters

    @_get_all_pages('counters')
    def counters(self, callback='', favorite=False, field='', label_id=None, offset=1, per_page=1000,
                 permission='', reverse=True, search_string='', sort='Default', status='Active', type=''):
        """ Return a list of existing counters available to the user
        """
        uri = self._get_uri(self.COUNTERS)
        params = {
            'callback': callback,
            'favorite': int(favorite),
            'field': field,
            'label_id': label_id,
            'offset': offset,
            'per_page': per_page,
            'permission': permission,
            'reverse': int(reverse),
            'search_string': search_string,
            'sort': sort,
            'status': status,
            'type': type
        }
        return self._get_data('GET', uri, params)

    def counter(self, counter_id, callback='', field=''):
        """ Return information about the specified counter
        """
        uri = self._get_uri(self.COUNTER % counter_id)
        params = {'field': field, 'callback': callback}
        return self._get_data('GET', uri, params)

    def add_counter(self, name, site, **kwargs):
        """ Create a counter with the specified parameters
        """
        uri = self._get_uri(self.COUNTERS)
        kwargs['name'] = name
        kwargs['site'] = site
        params = {'counter': kwargs}
        return self._get_data('POST', uri, json.dumps(params))

    def update_counter(self, counter_id, **kwargs):
        """ Modify the data for the specified counter
        """
        uri = self._get_uri(self.COUNTER % counter_id)
        params = {'counter': kwargs}
        return self._get_data('PUT', uri, json.dumps(params))

    def delete_counter(self, counter_id):
        """ Delete the specified counter
        """
        uri = self._get_uri(self.COUNTER % counter_id)
        return self._get_data('DELETE', uri)

    def undelete_counter(self, counter_id):
        """ Undelete the specified counter
        """
        uri = self._get_uri(self.COUNTER_UNDELETE % counter_id)
        return self._get_data('POST', uri)

    # Goals

    def goals(self, counter_id, callback='', sorted=False, use_deleted=False):
        """ Return information about the goals of counter
        """
        uri = self._get_uri(self.COUNTER_GOALS % counter_id)
        params = {'callback': callback, 'sorted': int(sorted), 'useDeleted': int(use_deleted)}
        return self._get_data('GET', uri, params)

    def goal(self, counter_id, goal_id, callback=''):
        """ Return information about the specified goal of counter.
        """
        uri = self._get_uri(self.COUNTER_GOAL % (counter_id, goal_id))
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def add_goal(self, counter_id, name, type, depth=0, klass=0, is_retargeting=False, flag='', conditions=[],
                 steps=[]):
        """ Create the goal of counter
        """
        uri = self._get_uri(self.COUNTER_GOALS % counter_id)
        params = {
            'goal': {
                'name': name,
                'type': type,
                'class': klass,
                'is_retargeting': int(is_retargeting),
            }
        }
        if type == 'step':
            params['goal']['steps'] = steps
        elif type == 'number':
            depth = depth if depth > 1 else 2  # depth can not be less than 2
            params['goal']['depth'] = depth
        else:
            if flag:
                params['goal']['flag'] = flag
            params['goal']['conditions'] = conditions

        return self._get_data('POST', uri, json.dumps(params))

    def update_goal(self, counter_id, goal_id, name, type, depth=0, klass=0, is_retargeting=False, flag='',
                    conditions=[], steps=[]):
        """ Change the settings specified goal of counter
        """
        uri = self._get_uri(self.COUNTER_GOAL % (counter_id, goal_id))
        params = {
            'goal': {
                'id': goal_id,
                'name': name,
                'type': type,
                'class': int(klass),
                'is_retargeting': int(is_retargeting)
            }
        }
        if type == 'step':
            params['goal']['steps'] = steps
        elif type == 'number':
            depth = depth if depth > 1 else 2  # depth can not be less than 2
            params['goal']['depth'] = depth
        else:
            if flag:
                params['goal']['flag'] = flag
            params['goal']['conditions'] = conditions

        return self._get_data('PUT', uri, json.dumps(params))

    def delete_goal(self, counter_id, goal_id):
        """ Delete the goal of counter
        """
        uri = self._get_uri(self.COUNTER_GOAL % (counter_id, goal_id))
        return self._get_data('DELETE', uri)

    # Filters

    def filters(self, counter_id, callback=''):
        """ Return information about the filter of counter
        """
        uri = self._get_uri(self.COUNTER_FILTERS % counter_id)
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def filter(self, counter_id, filter_id, callback=''):
        """ Return information about the specified filter of counter
        """
        uri = self._get_uri(self.COUNTER_FILTER % (counter_id, filter_id))
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def add_filter(self, counter_id, attr, type, value, action='include', status='active', with_subdomains=False):
        """ Create a filter of counter
        """
        uri = self._get_uri(self.COUNTER_FILTERS % counter_id)
        params = {
            'filter': {
                'attr': attr,
                'type': type,
                'value': value,
                'action': action,
                'status': status,
                'with_subdomains': int(with_subdomains)
            }
        }
        return self._get_data('POST', uri, json.dumps(params))

    def update_filter(self, counter_id, filter_id, attr, type, value, action='include', status='active', with_subdomains=False):
        """ Modify the configuration of the specified filter of counter
        """
        uri = self._get_uri(self.COUNTER_FILTER % (counter_id, filter_id))
        params = {
            'filter': {
                'id': filter_id,
                'attr': attr,
                'type': type,
                'value': value,
                'action': action,
                'status': status,
                'with_subdomains': int(with_subdomains)
            }
        }
        return self._get_data('PUT', uri, json.dumps(params))

    def delete_filter(self, counter_id, filter_id):
        """ Delete the filter of counter
        """
        uri = self._get_uri(self.COUNTER_FILTER % (counter_id, filter_id))
        return self._get_data('DELETE', uri)

    # Operations

    def operations(self, counter_id, callback=''):
        """ Return information about the operations of counter
        """
        uri = self._get_uri(self.COUNTER_OPERATIONS % counter_id)
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def operation(self, counter_id, operation_id, callback=''):
        """ Return information about the specified operation of counter
        """
        uri = self._get_uri(self.COUNTER_OPERATION % (counter_id, operation_id))
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def add_operation(self, counter_id, action, attr, value, status='active'):
        """ Create an operation for counter
        """
        uri = self._get_uri(self.COUNTER_OPERATIONS % counter_id)
        params = {
            'operation': {
                'action': action,
                'attr': attr,
                'value': value,
                'status': status
            }
        }
        return self._get_data('POST', uri, json.dumps(params))

    def update_operation(self, counter_id, operation_id, action, attr, value, status='active'):
        """ Modify the configuration of the specified operation of counter
        """
        uri = self._get_uri(self.COUNTER_OPERATION % (counter_id, operation_id))
        params = {
            'operation': {
                'id': operation_id,
                'action': action,
                'attr': attr,
                'value': value,
                'status': status
            }
        }
        return self._get_data('PUT', uri, json.dumps(params))

    def delete_operation(self, counter_id, operation_id):
        """ Delete an operation of counter
        """
        uri = self._get_uri(self.COUNTER_OPERATION % (counter_id, operation_id))
        return self._get_data('DELETE', uri)

    # Grants

    def grants(self, counter_id, callback=''):
        """ Return information about the permissions to manage the counter and statistics
        """
        uri = self._get_uri(self.COUNTER_GRANTS % counter_id)
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def grant(self, counter_id, user_login):
        """ Return information about a specific permit to control the counter
            and statistics
        """
        uri = self._get_uri(self.COUNTER_GRANT % counter_id)
        params = {'user_login': user_login}
        return self._get_data('GET', uri, params)

    def add_grant(self, counter_id, user_login, perm='view', comment=''):
        """ Create a permission to manage the counter and statistics
        """
        uri = self._get_uri(self.COUNTER_GRANTS % counter_id)
        params = {
            'grant': {
                'user_login': '' if perm == 'public_stat' else user_login,
                'perm': perm,
                'comment': comment
            }
        }
        return self._get_data('POST', uri, json.dumps(params))

    def update_grant(self, counter_id, user_login, perm, comment=''):
        """ Modify the configuration of the specified permission to manage the counter and statistics
        """
        uri = self._get_uri(self.COUNTER_GRANT % counter_id)
        params = {
            'grant': {
                'user_login': '' if perm == 'public_stat' else user_login,
                'perm': perm,
                'comment': comment
            }
        }
        return self._get_data('PUT', uri, json.dumps(params))

    def delete_grant(self, counter_id, user_login):
        """ Delete the permissions to manage the counter and statistics
        """
        uri = self._get_uri(self.COUNTER_GRANT % counter_id)
        params = {'user_login': user_login}
        return self._get_data('DELETE', uri, params)

    # Delegates

    def delegates(self, callback=''):
        """ Return list of delegates who have been granted full access to
            the account of the current user
        """
        uri = self._get_uri(self.DELEGATES)
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def add_delegate(self, user_login, comment=''):
        """ Modify the list of delegates for the current user account
        """
        uri = self._get_uri(self.DELEGATES)
        params = {
            'delegate': {
                'user_login': user_login,
                'comment': comment
            }
        }
        return self._get_data('POST', uri, json.dumps(params))

    def delete_delegate(self, user_login):
        """ Delete the user's login from the list of delegates for the current account
        """
        uri = self._get_uri(self.DELEGATE)
        params = {'user_login': user_login}
        return self._get_data('DELETE', uri, params)

    # Accounts

    def accounts(self, callback=''):
        """ Return a list of accounts, the delegate of which is the
            current user
        """
        uri = self._get_uri(self.ACCOUNTS)
        params = {'callback': callback}
        return self._get_data('GET', uri, params)

    def update_accounts(self, accounts):
        """ Modify the list of accounts whose delegate is the current user.
            Account list is updated in accordance with the list of usernames
            input structure.
            ! If the input structure does not specify a login user delegated by
            the current user, full access to the this user account will be
            revoked.
            ! If the input structure of the specified user's login,
            not included in the current list of accounts, full access to the
            account of this user NOT available.

        :param accounts: list
        :return:
        """
        uri = self._get_uri(self.ACCOUNTS)
        params = {'accounts': accounts}
        return self._get_data('PUT', uri, json.dumps(params))

    def delete_account(self, user_login):
        """ Remove the user's login from the list of accounts, which are
            delegate is the current user.
            ! When you delete a user name from the list of accounts full
            access to your account will be revoked.

        :param user_login: str
        :return: JSON2Obj
        """
        uri = self._get_uri(self.ACCOUNT)
        params = {'user_login': user_login}
        return self._get_data('DELETE', uri, params)

    # Clients

    def clients(self, counters):
        """ Return the Yandex.Direct customer data to companies which have access to the owner of Metrika counter.

        :param counters: list
        :return: JSON2Obj
        """
        uri = self._get_uri(self.CLIENTS)

        params = {'counters': ','.join(map(str, counters))}
        return self._get_data('GET', uri, params)

    # Labels

    def labels(self):
        uri = self._get_uri(self.LABELS)

        return self._get_data('GET', uri)

    def label(self, label_id):
        uri = self._get_uri(self.LABEL % label_id)

        return self._get_data('GET', uri)

    def add_label(self, name):
        uri = self._get_uri(self.LABELS)

        params = {
            'label': {
                'name': name
            }
        }
        return self._get_data('POST', uri, json.dumps(params))

    def update_label(self, label_id, name):
        uri = self._get_uri(self.LABEL % label_id)

        params = {
            'label': {
                'id': label_id,
                'name': name
            }
        }
        return self._get_data('PUT', uri, json.dumps(params))

    def delete_label(self, label_id):
        uri = self._get_uri(self.LABEL % label_id)

        return self._get_data('DELETE', uri)

    # Binding counters to labels

    def bind_to_label(self, counter_id, label_id):
        uri = self._get_uri(self.COUNTER_LABEL % (counter_id, label_id))

        return self._get_data('POST', uri)

    def unbind_from_label(self, counter_id, label_id):
        uri = self._get_uri(self.COUNTER_LABEL % (counter_id, label_id))

        return self._get_data('DELETE', uri)

    # Segments

    def segments(self, counter_id):
        uri = self._get_uri(self.COUNTER_API_SEGMENT_SEGMENTS % counter_id)

        return self._get_data('GET', uri)

    def segment(self, counter_id, segment_id):
        uri = self._get_uri(self.COUNTER_API_SEGMENT_SEGMENT % (counter_id, segment_id))

        return self._get_data('GET', uri)

    def add_segment(self, counter_id, name, expression):
        uri = self._get_uri(self.COUNTER_API_SEGMENT_SEGMENTS % counter_id)

        params = {
            'segment': {
                'name': name,
                'expression': expression,
                'segment_source': 'api'
            }
        }
        return self._get_data('POST', uri, json.dumps(params))

    def update_segment(self, counter_id, segment_id, name=None, expression=None):
        uri = self._get_uri(self.COUNTER_API_SEGMENT_SEGMENT % (counter_id, segment_id))

        params = {
            'segment': {
                'segment_source': 'api'
            }
        }
        if name:
            params['segment']['name'] = name
        if expression:
            params['segment']['expression'] = expression
        return self._get_data('PUT', uri, json.dumps(params))

    def delete_segment(self, counter_id, segment_id):
        uri = self._get_uri(self.COUNTER_API_SEGMENT_SEGMENT % (counter_id, segment_id))

        return self._get_data('DELETE', uri)

    # Uploadins

    def uploadings(self, counter_id):
        uri = self._get_uri(self.COUNTER_USER_PARAMS_UPLOADINGS % counter_id)

        return self._get_data('GET', uri)

    def uploading(self, counter_id, uploading_id):
        uri = self._get_uri(self.COUNTER_USER_PARAMS_UPLOADING % (counter_id, uploading_id))

        return self._get_data('GET', uri)

    def confirm_uploading(self, counter_id, uploading_id, content_id_type='client_id', action='update', status='is_processed', comment=''):
        uri = self._get_uri(self.COUNTER_USER_PARAMS_UPLOADING_CONFIRM % (counter_id, uploading_id))

        params = {
            'uploading' : {
                'id':  uploading_id,
                'content_id_type':  content_id_type,
                'action':  action,
                'status':  status,
                'comment':  comment
            }
        }
        return self._get_data('POST', uri, json.dumps(params))

    def upload_uploading(self, counter_id, file_descriptor, action='update'):
        uri = self._get_uri(self.COUNTER_USER_PARAMS_UPLOADINGS_UPLOAD % counter_id, action=action)

        return self._get_data('POST', uri, params=file_descriptor)

    def update_uploading(self, counter_id, uploading_id, comment=None):
        uri = self._get_uri(self.COUNTER_USER_PARAMS_UPLOADING % (counter_id, uploading_id))

        params = {
            'uploading': {
                'id': uploading_id,
                # 'content_id_type': content_id_type,
                # 'action': action,
                # 'status': status,
                # 'comment': comment
            }
        }
        if comment is not None: params['uploading']['comment'] = comment
        return self._get_data('PUT', uri, json.dumps(params))

    # Offline conversions

    def on_calls_extended_threshold(self, counter_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_CALLS_EXTENDED_THRESHOLD % counter_id)

        return self._get_data('POST', uri)

    def off_calls_extended_threshold(self, counter_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_CALLS_EXTENDED_THRESHOLD % counter_id)

        return self._get_data('DELETE', uri)

    def upload_calls(self, counter_id, file_descriptor, client_id_type, comment=None, new_goal_name=None):
        kwargs = {
            'client_id_type': client_id_type
        }
        if comment is not None: kwargs['comment'] = comment
        if new_goal_name is not None: kwargs['new_goal_name'] = new_goal_name
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_UPLOAD_CALLS % counter_id, **kwargs)

        return self._get_data('POST', uri, params=file_descriptor)

    def calls_uploadings(self, counter_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_CALLS_UPLOADINGS % counter_id)

        return self._get_data('GET', uri)

    def calls_uploading(self, counter_id, uploading_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_CALLS_UPLOADING % (counter_id, uploading_id))

        return self._get_data('GET', uri)

    def on_extended_threshold(self, counter_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_EXTENDED_THRESHOLD % counter_id)

        return self._get_data('POST', uri)

    def off_extended_threshold(self, counter_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_EXTENDED_THRESHOLD % counter_id)

        return self._get_data('DELETE', uri)

    def upload_offline_conversions(self, counter_id, file_descriptor, client_id_type, comment=None):
        kwargs = {
            'client_id_type': client_id_type
        }
        if comment is not None: kwargs['comment'] = comment
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_UPLOAD % counter_id, **kwargs)

        return self._get_data('POST', uri, params=file_descriptor)

    def offline_conversions_uploadings(self, counter_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_UPLOADINGS % counter_id)

        return self._get_data('GET', uri)

    def offline_conversions_uploading(self, counter_id, uploading_id):
        uri = self._get_uri(self.COUNTER_OFFLINE_CONVERSIONS_UPLOADING % (counter_id, uploading_id))

        return self._get_data('GET', uri)

    # Statistics

    def _stat_data(self, uri, ids, metrics, **others_params):
        if isinstance(ids, int):
            ids = str(ids)
        elif isinstance(ids, list):
            ids = ','.join(map(str, ids))

        uri = self._get_uri(uri)
        params = {
            'ids': ids,
            'metrics': metrics
        }
        params.update(others_params)
        return self._get_data('GET', uri, params)

    def stat_data(self, ids, metrics, **others_params):
        return self._stat_data(self.STAT_DATA, ids, metrics, **others_params)

    def stat_data_drilldown(self, ids, metrics, **others_params):
        return self._stat_data(self.STAT_DATA_DRILLDOWN, ids, metrics, **others_params)

    def stat_data_bytime(self, ids, metrics, **others_params):
        return self._stat_data(self.STAT_DATA_BYTIME, ids, metrics, **others_params)

    def stat_data_comparison(self, ids, metrics, **others_params):
        return self._stat_data(self.STAT_DATA_COMPARISON, ids, metrics, **others_params)

    def stat_data_comparison_drilldown(self, ids, metrics, **others_params):
        return self._stat_data(self.STAT_DATA_COMPARISON_DRILLDOWN, ids, metrics, **others_params)
