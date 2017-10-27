# coding: utf-8

import unittest
import time
from io import StringIO
from os.path import basename

from yametrikapy import Metrika

try:
    from . import secret_settings
except ImportError:
    class secret_settings:
        MAIN_USER_LOGIN = ''
        MAIN_CLIENT_ID = ''
        MAIN_CLIENT_SECRET = ''
        MAIN_TOKEN = ''

        OTHER_USER_LOGIN = ''
        OTHER_CLIENT_ID = ''
        OTHER_TOKEN = ''


MAIN_USER_LOGIN = secret_settings.MAIN_USER_LOGIN
MAIN_CLIENT_ID = secret_settings.MAIN_CLIENT_ID
MAIN_CLIENT_SECRET = secret_settings.MAIN_CLIENT_SECRET
MAIN_TOKEN = secret_settings.MAIN_TOKEN

OTHER_USER_LOGIN = secret_settings.OTHER_USER_LOGIN
OTHER_CLIENT_ID = secret_settings.OTHER_CLIENT_ID
OTHER_TOKEN = secret_settings.OTHER_TOKEN


class TestMetrikaBase(unittest.TestCase):
    def setUp(self):
        self.main_user_login = MAIN_USER_LOGIN
        self.metrika = Metrika(MAIN_CLIENT_ID, token=MAIN_TOKEN)

        self.other_user_login = OTHER_USER_LOGIN
        self.other_metrika = Metrika(OTHER_CLIENT_ID, token=OTHER_TOKEN)


class TestMetrikaWithCounter(TestMetrikaBase):
    def setUp(self):
        super(TestMetrikaWithCounter, self).setUp()

        counter = self.metrika.add_counter('Test name of counter', 'test-name-counter.ru')
        self.counter_id = counter.counter['id']
        self.counter_name = counter.counter['name']

        self.assertIsInstance(self.counter_id, int)
        self.assertTrue(self.counter_id)

    def tearDown(self):
        counter = self.metrika.delete_counter(self.counter_id)
        self.assertTrue(counter.success)

    def test_counters(self):
        counters = self.metrika.counters(permission='own').counters
        self.assertIsInstance(counters, list)
        # self.assertTrue(len(counters) > 0)

        counter = self.metrika.update_counter(self.counter_id, name='New test name of counter')
        self.assertEqual(self.counter_id, counter.counter['id'])

        counter = self.metrika.counter(self.counter_id)
        self.assertEqual(self.counter_id, counter.counter['id'])

        counter = self.metrika.delete_counter(self.counter_id)
        self.assertTrue(counter.success)

        counter = self.metrika.undelete_counter(self.counter_id)
        self.assertTrue(counter.success)

    def test_goals(self):
        goals = self.metrika.goals(self.counter_id).goals
        self.assertFalse(goals)

        # goal = self.metrika.add_goal(self.counter_id, 'Goal name', 'number', depth=2)
        CONDITION_URL = 'indexpage'
        CONDITION_TYPE = 'contain'

        conditions = [{'url': CONDITION_URL, 'type': CONDITION_TYPE}]

        goal = self.metrika.add_goal(self.counter_id, 'Goal name', 'url', conditions=conditions)
        goal_id = goal.goal['id']
        self.assertIsInstance(goal_id, int)
        self.assertTrue(goal_id)

        CONDITION_URL = 'indexpage2'
        CONDITION_TYPE = 'contain'

        conditions = [{'url': CONDITION_URL, 'type': CONDITION_TYPE}]
        # goal = self.metrika.update_goal(self.counter_id, goal_id, 'New goal name', 'action', conditions=conditions)
        goal = self.metrika.update_goal(self.counter_id, goal_id, 'New goal name', 'url', conditions=conditions)
        self.assertEqual(goal_id, goal.goal['id'])

        goal = self.metrika.goal(self.counter_id, goal_id).goal
        self.assertTrue(goal_id == goal['id'])
        self.assertTrue(goal['conditions'][0]['url'] == CONDITION_URL)
        self.assertTrue(goal['conditions'][0]['type'] == CONDITION_TYPE)

        goal = self.metrika.delete_goal(self.counter_id, goal_id)
        self.assertTrue(goal.success)

    def test_filters(self):
        filters = self.metrika.filters(self.counter_id).filters
        self.assertFalse(filters)

        filter = self.metrika.add_filter(self.counter_id, 'url', 'contain', 'indexpage')
        filter_id = filter.filter['id']
        self.assertIsInstance(filter_id, int)
        self.assertTrue(filter_id)

        filter = self.metrika.update_filter(self.counter_id, filter_id, 'url', 'contain', 'newindexpage')
        self.assertEqual(filter_id, filter.filter['id'])

        filter = self.metrika.filter(self.counter_id, filter_id).filter
        self.assertEqual(filter_id, filter['id'])

        filter = self.metrika.delete_filter(self.counter_id, filter_id)
        self.assertTrue(filter.success)

    def test_operations(self):
        operations = self.metrika.operations(self.counter_id)
        self.assertTrue(len(operations.operations) == 0)

        operation = self.metrika.add_operation(self.counter_id, 'merge_https_and_http', 'url', '', status='active')
        operation_id = operation.operation['id']
        self.assertIsInstance(operation_id, int)
        self.assertTrue(operation_id)

        operation = self.metrika.update_operation(self.counter_id, operation_id, 'merge_https_and_http', 'url', '',
                                                  status='disabled')
        self.assertEqual(operation_id, operation.operation['id'])

        operation = self.metrika.operation(self.counter_id, operation_id)
        self.assertEqual(operation_id, operation.operation['id'])

        operation = self.metrika.delete_operation(self.counter_id, operation_id)
        self.assertTrue(operation.success)

    def test_grants(self):
        grants = self.metrika.grants(self.counter_id).grants
        self.assertIsInstance(grants, list)

        grant = self.metrika.add_grant(self.counter_id, self.other_user_login, 'view')
        grant = self.metrika.grant(self.counter_id, self.other_user_login).grant

        grant = self.metrika.update_grant(self.counter_id, '', 'public_stat')

        grant = self.metrika.delete_grant(self.counter_id, '')
        self.assertTrue(grant.success)

    def test_clients(self):
        self.assertIsInstance(self.metrika.clients([self.counter_id]).clients, list)

    def test_binding_counters_to_labels(self):
        LABEL_NAME = 'TEST_LABEL'

        self.metrika.add_label(LABEL_NAME)
        labels = self.metrika.labels().labels
        self.assertTrue(len(labels) > 0)
        labels = list(filter(lambda label: label['name'] == LABEL_NAME, labels))
        self.assertTrue(len(labels) > 0)
        label_id = labels[0]['id']

        binding = self.metrika.bind_to_label(self.counter_id, label_id)
        self.assertTrue(binding.success)

        unbinding = self.metrika.unbind_from_label(self.counter_id, label_id)
        self.assertTrue(unbinding.success)

        label = self.metrika.delete_label(label_id)
        self.assertTrue(label.success)

    def test_segments(self):
        segments = self.metrika.segments(self.counter_id).segments
        self.assertIsInstance(segments, list)

        SEGMENT_NAME = 'TEST_SEGMENT'
        TEST_EXPRESSION = u"ym:s:regionCityName=='Москва'"

        segment = self.metrika.add_segment(self.counter_id, SEGMENT_NAME, TEST_EXPRESSION).segment
        self.assertTrue(segment['name'] == SEGMENT_NAME)
        segment_id = segment['segment_id']
        segment = self.metrika.segment(self.counter_id, segment_id).segment
        self.assertTrue(segment['name'] == SEGMENT_NAME)

        NEW_SEGMENT_NAME = 'TEST_NEW_SEGMENT'

        self.metrika.update_segment(self.counter_id, segment_id, name=NEW_SEGMENT_NAME)

        segment = self.metrika.segment(self.counter_id, segment_id).segment
        self.assertTrue(segment['name'] == NEW_SEGMENT_NAME)
        self.assertTrue(segment['expression'] == TEST_EXPRESSION)

        segment = self.metrika.delete_segment(self.counter_id, segment_id)
        self.assertTrue(segment.success)

    def test_uploadings(self):
        uploadings = self.metrika.uploadings(self.counter_id).uploadings
        self.assertIsInstance(uploadings, list)

        with StringIO('"P12345","age",42\r\n"P12345","name","abc"') as f:
            filename = basename(getattr(f, 'file', 'file.csv'))
            uploading = self.metrika.upload_uploading(self.counter_id, f).uploading

        uploading_id = uploading['id']

        COMMENT = u'Файл {}'.format(filename)

        uploading = self.metrika.confirm_uploading(self.counter_id, uploading_id, content_id_type='user_id',
                                                   action='update', status='is_processed',
                                                   comment=COMMENT).uploading
        self.assertTrue(uploading['comment'] == COMMENT)

        uploading = self.metrika.uploading(self.counter_id, uploading_id).uploading

        self.assertTrue(uploading['comment'] == COMMENT)

        NEW_COMMENT = 'file'

        uploading = self.metrika.update_uploading(self.counter_id, uploading_id, comment=NEW_COMMENT).uploading

        self.assertTrue(uploading['comment'] == NEW_COMMENT)

        n = 60
        while uploading.get('status', '') == 'is_processed' and n > 0:
            time.sleep(2)
            uploading = self.metrika.uploading(self.counter_id, uploading_id).uploading
            n -= 1

        self.assertTrue(uploading['status'] == 'linkage_failure')

    def test_offline_conversions(self):
        extended_threshold = self.metrika.on_extended_threshold(self.counter_id)
        self.assertTrue(extended_threshold.success)
        extended_threshold = self.metrika.off_extended_threshold(self.counter_id)
        self.assertTrue(extended_threshold.success)

        data = '''UserId,Target,DateTime,Price,Currency
133591247640966458,GOAL1,1481718166,123.45,RUB
133591247640966458,GOAL2,1481718142,678.90,RUB
133591247640966458,GOAL3,1481718066,123.45,RUB
579124169844706072,GOAL3,1481718116,678.90,RUB
148059425477661429,GOAL2,1481718126,123.45,RUB
148059425477661429,GOAL3,1481714026,678.90,RUB
'''
        with StringIO(data) as f:
            filename = basename(getattr(f, 'file', 'file.csv'))
            uploading = self.metrika.upload_offline_conversions(self.counter_id, f, 'USER_ID', comment=filename).uploading

        self.assertTrue(uploading['status'] in ('LINKAGE_FAILURE', 'PROCESSED', 'UPLOADED'))

        uploadings = self.metrika.offline_conversions_uploadings(self.counter_id).uploadings
        self.assertTrue(len(uploadings) == 1)

        uploading_id = uploadings[0]['id']

        uploading = self.metrika.offline_conversions_uploading(self.counter_id, uploading_id).uploading
        self.assertTrue(uploading['status'] in ('LINKAGE_FAILURE', 'PROCESSED', 'UPLOADED'))

    def test_offline_conversions_calls(self):
        calls_extended_threshold = self.metrika.on_calls_extended_threshold(self.counter_id)
        self.assertTrue(calls_extended_threshold.success)
        calls_extended_threshold = self.metrika.off_calls_extended_threshold(self.counter_id)
        self.assertTrue(calls_extended_threshold.success)

        data = '''UserId, DateTime, Price, Currency, PhoneNumber, TalkDuration, HoldDuration, CallMissed, Tag, FirstTimeCaller, URL, CallTrackerURL
133591247640966458, 1481714026, 678.90, RUB, +71234567890, 136, 17, 0,, 1, https://test.com/, https://test.com/
579124169844706072, 1481718066, 123.45, RUB, +70987654321, 17, 23, 0,, 2, https://test.com/, https://test.com/
148059425477661429, 1481718126, 678.90, RUB, +71234509876, 72, 11, 0,, 0, https://test.com/, https://test.com/
'''
        with StringIO(data) as f:
            filename = basename(getattr(f, 'file', 'file.csv'))
            uploading = self.metrika.upload_calls(self.counter_id, f, 'USER_ID', comment=filename, new_goal_name='GOAL1').uploading

        self.assertTrue(uploading['status'] in ('LINKAGE_FAILURE', 'PROCESSED', 'UPLOADED'))

        uploadings = self.metrika.calls_uploadings(self.counter_id).uploadings
        self.assertTrue(len(uploadings) == 1)

        uploading_id = uploadings[0]['id']

        uploading = self.metrika.calls_uploading(self.counter_id, uploading_id).uploading
        self.assertTrue(uploading['status'] in ('LINKAGE_FAILURE', 'PROCESSED', 'UPLOADED'))

    def test_statistics(self):
        metrics = ['ym:s:visits', 'ym:s:users']

        stat = self.metrika.stat_data(self.counter_id, ','.join(metrics), dimensions='ym:s:searchEngineName',
                                      filters="ym:s:trafficSourceName=='Переходы из поисковых систем'")
        self.assertIsInstance(stat.data, list)
        self.assertEquals(stat.query['metrics'], metrics)

        metrics = ['ym:s:pageviews']

        stat = self.metrika.stat_data_drilldown(self.counter_id, ','.join(metrics))
        self.assertIsInstance(stat.data, list)
        self.assertEquals(stat.query['metrics'], metrics)
        stat = self.metrika.stat_data_bytime(self.counter_id, ','.join(metrics))
        self.assertIsInstance(stat.data, list)
        self.assertEquals(stat.query['metrics'], metrics)
        stat = self.metrika.stat_data_comparison(self.counter_id, ','.join(metrics))
        self.assertIsInstance(stat.data, list)
        self.assertEquals(stat.query['metrics'], metrics)
        stat = self.metrika.stat_data_comparison_drilldown(self.counter_id, ','.join(metrics), limit=50)
        self.assertIsInstance(stat.data, list)
        self.assertEquals(stat.query['metrics'], metrics)


class TestMetrikaWithoutCounter(TestMetrikaBase):
    def test_accounts(self):
        delegates = self.metrika.add_delegate(self.other_user_login, comment='comments').delegates
        self.assertIsInstance(delegates, list)
        self.assertTrue(list(filter(lambda item: item['user_login'] == self.other_user_login, delegates)))

        accounts = self.other_metrika.accounts().accounts
        self.assertIsInstance(accounts, list)
        self.assertTrue(list(filter(lambda item: item['user_login'] == self.main_user_login, accounts)))

        accounts = self.other_metrika.update_accounts(accounts).accounts
        self.assertIsInstance(accounts, list)
        self.assertTrue(list(filter(lambda item: item['user_login'] == self.main_user_login, accounts)))

        account = self.other_metrika.delete_account(self.main_user_login)
        self.assertTrue(account.success)

        delegates = self.metrika.delegates().delegates
        self.assertIsInstance(delegates, list)
        self.assertFalse(list(filter(lambda item: item['user_login'] == self.other_user_login, delegates)))

    def test_delegates(self):
        delegates = self.metrika.delegates().delegates
        self.assertIsInstance(delegates, list)

        delegates = self.metrika.add_delegate(self.other_user_login, comment='comments').delegates
        self.assertIsInstance(delegates, list)
        self.assertTrue(list(filter(lambda item: item['user_login'] == self.other_user_login, delegates)))

        delegates = self.metrika.delegates().delegates
        self.assertIsInstance(delegates, list)
        self.assertTrue(list(filter(lambda item: item['user_login'] == self.other_user_login, delegates)))

        delegate = self.metrika.delete_delegate(self.other_user_login)
        self.assertTrue(delegate.success)

    def test_labels(self):
        labels = self.metrika.labels().labels
        self.assertIsInstance(labels, list)

        LABEL_NAME = 'TEST_LABEL'

        self.metrika.add_label(LABEL_NAME)
        labels = self.metrika.labels().labels
        self.assertTrue(len(labels) > 0)
        labels = list(list(filter(lambda label: label['name'] == LABEL_NAME, labels)))
        self.assertTrue(len(labels) > 0)
        label_id = labels[0]['id']
        label = self.metrika.label(label_id).label
        self.assertTrue(label['name'] == LABEL_NAME)

        NEW_LABEL_NAME = 'TEST_LABEL2'
        label = self.metrika.update_label(label_id, NEW_LABEL_NAME).label
        self.assertTrue(label['name'] == NEW_LABEL_NAME)

        label = self.metrika.delete_label(label_id)
        self.assertTrue(label.success)


if __name__ == '__main__':
    unittest.main()
