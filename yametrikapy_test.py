﻿#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest

from yametrikapy import Metrika
from yametrikapy.core import APIException, NotFoundError


class TestMetrika(unittest.TestCase):

    def setUp(self):
        client_id = '6993a3cd88e34ac686504790c7fe341c'
        login = ''
        password = ''
        self.exists_other_user_login = ''
        self.metrika = Metrika(client_id, login, password)

    def tearDown(self):
        del self.metrika

    def testMetrika(self):
        # COUNTERS
        counters = self.metrika.GetCounterList().counters
        self.assertTrue(counters)

        counter = self.metrika.AddCounter('Test name of counter',
            'test-name-counter.ru')
        counter_id = counter.counter['id']
        self.assertIsInstance(counter_id, int)
        self.assertTrue(counter_id)

        counter = self.metrika.EditCounter(counter_id,
            name='New test name of counter')
        self.assertEqual(counter_id, counter.counter['id'])

        counter = self.metrika.GetCounter(counter_id)
        self.assertEqual(counter_id, counter.counter['id'])

        counter = self.metrika.CheckCounter(counter_id)
        self.assertEqual(counter_id, counter.counter['id'])

        # GOALS
        goals = self.metrika.GetCounterGoalList(counter_id).goals
        self.assertFalse(goals)

        goal = self.metrika.AddCounterGoal(counter_id, 'Goal name',
            'number', 2)
        goal_id = goal.goals[0]['id']
        self.assertIsInstance(goal_id, int)
        self.assertTrue(goal_id)

        conditions = [{'url': 'indexpage', 'type': 'contain'}]
        goal = self.metrika.EditCounterGoal(counter_id, goal_id,
            'New goal name', 'url', 0, conditions)
        self.assertEqual(goal_id, goal.goal['id'])

        goal = self.metrika.GetCounterGoal(counter_id, goal_id).goal
        self.assertEqual(goal_id, goal['id'])

        # FILTERS
        filters = self.metrika.GetCounterFilterList(counter_id).filters
        self.assertFalse(filters)

        filter = self.metrika.AddCounterFilter(counter_id, 'include', 'url',
            'contain', 'indexpage', 'active')
        filter_id = filter.filters[0]['id']
        self.assertIsInstance(filter_id, int)
        self.assertTrue(filter_id)

        filter = self.metrika.EditCounterFilter(counter_id, filter_id,
            'include', 'url', 'contain', 'newindexpage', 'disabled')
        self.assertEqual(filter_id, filter.filter['id'])

        filter = self.metrika.GetCounterFilter(counter_id, filter_id).filter
        self.assertEqual(filter_id, filter['id'])

        filter = self.metrika.DeleteCounterFilter(counter_id, filter_id)
        self.assertIsNone(filter.filter)

        # OPERATIONS
        operations = self.metrika.GetCounterOperationList(counter_id)
        self.assertFalse(operations.operations)

        operation = self.metrika.AddCounterOperation(counter_id,
            'merge_https_and_http', 'url', '', 'active')
        operation_id = operation.operations[0]['id']
        self.assertIsInstance(operation_id, int)
        self.assertTrue(operation_id)

        operation = self.metrika.EditCounterOperation(counter_id, operation_id,
            'merge_https_and_http', 'url', '', 'disabled')
        self.assertEqual(operation_id, operation.operation['id'])

        operation = self.metrika.GetCounterOperation(counter_id, operation_id)
        self.assertEqual(operation_id, operation.operation['id'])

        operation = self.metrika.DeleteCounterOperation(counter_id,
            operation_id)
        self.assertIsNone(operation.operation)

        # GRANTS
        grants = self.metrika.GetCounterGrantList(counter_id).grants
        if self.exists_other_user_login:
            grant = self.metrika.AddCounterGrant(counter_id,
                self.exists_other_user_login, 'view')
            grant = self.metrika.GetCounterGrant(counter_id,
                self.exists_other_user_login).grant

            grant = self.metrika.EditCounterGrant(counter_id,
                self.exists_other_user_login, 'edit')

            grant = self.metrika.DeleteCounterGrant(counter_id,
                self.exists_other_user_login)
            self.assertIsNone(grant.grant)

        # DELEGATES

        # ACCOUNTS

        # STATISTICS
        self.assertRaises(APIException, self.metrika.GetStatTrafficSummary, counter_id)
        stat = self.metrika.GetStatTrafficDeepness(counter_id).data_depth
        self.assertFalse(stat)
        self.assertRaises(APIException, self.metrika.GetStatTrafficHourly, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTrafficLoad, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesSummary, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesSites, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesSearchEngines, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesPhrases, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesMarketing, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesDirectSummary, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesDirectPlatforms, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesDirectRegions, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatSourcesTags, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatContentPopular, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatContentEntrance, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatContentExit, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatContentTitles, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatContentUrlParam, counter_id)
        self.assertRaises(NotFoundError, self.metrika.GetStatContentUserVars, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatContentECommerce, counter_id, goal_id)
        self.assertRaises(APIException, self.metrika.GetStatGeo, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatDemographyAgeGender, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatDemographyStructure, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechBrowsers, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechOs, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechDisplay, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechMobile, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechFlash, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechSilverlight, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechDotNet, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechJava, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechCookies, counter_id)
        self.assertRaises(APIException, self.metrika.GetStatTechJavascript, counter_id)

        # DELETE GOAL
        goal = self.metrika.DeleteCounterGoal(counter_id, goal_id)
        self.assertIsNone(goal.goal)

        # DELETE COUNTER
        counter = self.metrika.DeleteCounter(counter_id)
        self.assertIsNone(counter.counter)


if __name__ == '__main__':
    unittest.main()
