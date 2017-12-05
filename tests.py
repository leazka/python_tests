#!/usr/bin/env python2.7
# -*- coding: UTF-8 -*-

import requests
import unittest
from collections import OrderedDict
import random
from ConfigParser import SafeConfigParser
import time
import sys

import argparse
from ddt import *
from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestRunner


class Caller:
    def __init__(self, url):
        self.url = url

    def call(self, request):
        request_body = json.dumps(request)
        response = requests.post(self.url, request_body)

        return json.loads(response.text)


class Trigger:
    def __init__(self, caller, trigger_body, trigger_id, camp_id, key):
        self.trigger_body = trigger_body
        self.caller = caller
        self.trigger_id = trigger_id
        self.camp_id = camp_id
        self.key = key

    def create(self):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['key'] = self.key
        request['trigger_body'] = self.trigger_body
        request['request_type'] = 'trigger_create'

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Trigger was not created! Error:" + str(response['error_message']))
        self.trigger_id = response['trigger_id']

        return response

    def update(self, trigger_body_upd):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['key'] = KEY
        request['trigger_id'] = self.trigger_id
        request['trigger_body'] = trigger_body_upd
        request['request_type'] = 'trigger_update'

        self.trigger_body = trigger_body_upd
        response = self.caller.call(request)

        if response['error_code'] != 0:
            raise Exception("Trigger was not updated! Error:" + str(response['error_message']))

        return response

    def delete(self):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['key'] = KEY
        request['trigger_id'] = self.trigger_id
        request['request_type'] = 'trigger_delete'

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Trigger was not deleted! Error:" + str(response['error_message']))

        return response

    def list_read(self):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['request_type'] = 'trigger_list_read'
        request['key'] = KEY

        response = self.caller.call(request)

        if response['error_code'] != 0:
            raise Exception("List of triggers is not available! Error:" + str(response['error_message']))

        return response

    def read(self):  # not on frontend yet, returns trigger_body
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['key'] = KEY
        request['trigger_id'] = self.trigger_id
        request['request_type'] = 'trigger_read'

        response = self.caller.call(request)

        if response['error_code'] != 0:
            raise Exception("Couldn't get trigger body! Error:" + str(response['error_message']))

        return response

    def list(self):  # not on frontend yet, returns trigger_id's
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['request_type'] = 'trigger_list'
        request['key'] = KEY

        response = self.caller.call(request)

        if response['error_code'] != 0:
            raise Exception("List of triggers is not available! Error:" + str(response['error_message']))

        return response

    def items_count(self):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['request_type'] = 'trigger_items_count'
        request['key'] = KEY

        response = self.caller.call(request)

        if response['error_code'] != 0:
            raise Exception("Can't return number of triggers! Error:" + str(response['error_message']))

        return response

    def list_delete(self, trigger_ids):
        request = dict()

        request['campaign_id'] = self.camp_id
        request['key'] = KEY
        request['request_type'] = 'trigger_list_delete'
        request['trigger_ids'] = trigger_ids

        response = self.caller.call(request)

        if response['error_code'] != 0:
            raise Exception("Can't delete triggers! Error:" + str(response['error_message']))

        return response


class Emit:
    def __init__(self, campaign_id):
        self.campaign_id = campaign_id

    def emit(self):
        request = OrderedDict()
        request['campaign_id'] = self.campaign_id
        request['request_type'] = 'event_emit'
        request['key'] = KEY

        request_body = json.dumps(request)
        response = requests.post(URL, request_body)

        return response.status_code


"""
Honestly, I have no idea whether Alert_count and Mark_as_read should be separate classes or
 just methods within Alert class. Both ways don't feel quite right :(
"""


class AlertCount:
    def __init__(self, caller, camp_id):
        self.caller = caller
        self.camp_id = camp_id

    def count(self):
        request = OrderedDict()
        request['campaign_id'] = self.camp_id
        request['request_type'] = 'alert_items_count'
        request['key'] = KEY

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alerts were not counted! Error:" + str(response['error_message']))

        return response


class MarkAsRead:
    def __init__(self, caller, camp_id):
        self.caller = caller
        self.camp_id = camp_id

    def mark(self):
        request = OrderedDict()
        request['campaign_id'] = self.camp_id
        request['request_type'] = 'alert_mark_as_read'
        request['key'] = KEY

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alerts were not marked as read! Error:" + str(response['error_message']))

        return response


class Alert:
    def __init__(self, caller, alert_body, alert_id, camp_id):
        self.caller = caller
        self.alert_body = alert_body
        self.alert_id = alert_id
        self.camp_id = camp_id

    def read(self):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['request_type'] = 'alert_read'
        request['key'] = KEY
        request['alert_id'] = self.alert_id

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alert was not read! Error:" + str(response['error_message']))

        return response

    def list_read(self):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['request_type'] = 'alert_list_read'
        request['key'] = KEY

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alerts list was not read! Error:" + str(response['error_message']))

        return response

    def create(self):  # exclusively on BE, of course
        request = OrderedDict()

        request['request_type'] = 'alert_create'
        request['campaign_id'] = self.camp_id
        request['alert_body'] = self.alert_body

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alert was not created! Error:" + str(response['error_message']))

        self.alert_id = response['alert_id']

        return response

    def delete(self):
        request = OrderedDict()

        request['request_type'] = 'alert_delete'
        request['campaign_id'] = self.camp_id
        request['alert_id'] = self.alert_id

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alert was not deleted! Error:" + str(response['error_message']))

        return response

    def update(self, alert_body_upd):  # on BE
        request = OrderedDict()
        request['request_type'] = 'alert_update'
        request['campaign_id'] = self.camp_id
        request['alert_id'] = self.alert_id
        request['alert_body'] = alert_body_upd

        self.alert_body = alert_body_upd

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alert was not updated! Error:" + str(response['error_message']))

        return response

    def list(self):  # on BE
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['request_type'] = 'alert_list'

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alerts list not read! Error:" + str(response['error_message']))

        return response

    def list_delete(self, alert_ids):
        request = OrderedDict()

        request['campaign_id'] = self.camp_id
        request['request_type'] = 'alert_list_delete'
        request['alert_ids'] = alert_ids

        response = self.caller.call(request)
        if response['error_code'] != 0:
            raise Exception("Alerts were not deleted! Error:" + str(response['error_message']))

        return response


@ddt
class ARevertToZeroState(unittest.TestCase):
    @file_data('ids.json')
    def test_revert_to_zero_state(self, camp_id):
        caller = Caller(URL)
        trigger = Trigger(caller, None, None, camp_id, KEY)
        alert = Alert(caller, None, None, camp_id)

        tr_list = trigger.list()
        if 'trigger_ids' in tr_list.keys():
            trigger_ids = trigger.list()['trigger_ids']
            trigger.list_delete(trigger_ids)

        al_list = alert.list()
        if 'alert_ids' in al_list.keys():
            alert_ids = alert.list()['alert_ids']
            alert.list_delete(alert_ids)


@ddt
class TestTriggerFunctionality(unittest.TestCase):
    @file_data('ids.json')
    def test_create_check_update_delete(self, camp_id):
        caller = Caller(URL)
        trigger_body = {
            "domain": "wow.com",
            "threshold": "",
            "parameter": "position",
            "scope": "all",
            "condition": "",
        }

        trigger_body_upd = {
            "domain": "fuu.com",
            "threshold": 1,
            "condition": "changes_more_than",
            "parameter": "position",
            "scope": "all"
        }

        conditions = ['changes_more_than', 'enters_top', 'leaves_top', 'gains_more_than', 'loses_more_than']

        for i in range(len(conditions)):
            n = random.randint(1, 100)
            trigger_body['threshold'] = n
            trigger_body['condition'] = conditions[i]
            i += 1

            trigger = Trigger(caller, trigger_body, None, camp_id, KEY)

            trigger_id = trigger.create()['trigger_id']
            self.assertIn(trigger_id, trigger.list()['trigger_ids'])
            self.assertEqual(trigger.items_count()['items_count'], 1)

            trigger.update(trigger_body_upd)
            new_domain = trigger.read()['trigger_body']
            self.assertEqual(trigger_body_upd['domain'], new_domain['domain'])

            trigger.delete()
            trigger_list = trigger.list_read()['trigger_ids']
            self.assertNotIn(trigger_id, trigger_list)
            self.assertEqual(trigger.items_count()['items_count'], 0)

    @file_data('ids.json')
    def test_trigger_list_delete(self, camp_id):
        caller = Caller(URL)

        conditions = ['changes_more_than', 'enters_top', 'leaves_top', 'gains_more_than', 'loses_more_than']

        trigger_body = {
            "domain": "list.com",
            "threshold": "",
            "parameter": "position",
            "scope": "all",
            "condition": "",
        }

        trigger_ids = []
        trigger = Trigger(caller, trigger_body, None, camp_id, KEY)

        for i in range(0, 3):
            trigger_body['threshold'] = random.randint(1, 100)
            trigger_body['condition'] = conditions[random.randint(1, 4)]
            trigger.create()
            trigger_ids.append(trigger.trigger_id)

        self.assertEquals(trigger_ids, trigger.list()['trigger_ids'])
        trigger.list_delete(trigger_ids)
        self.assertFalse(trigger.list()['trigger_ids'])


@ddt
class TestAlertFunctionality(unittest.TestCase):
    @file_data('ids.json')
    def test_create_check_update_delete(self, camp_id):
        caller = Caller(URL)
        alert_body = {
            "domain": "wow.com",
            "threshold": 1,
            "condition": "changes_more_than",
            "parameter": "position",
            "scope": "all",
            "is_read": 0
        }

        alert_body_upd = {
            "domain": "fuu.com",
            "threshold": 1,
            "condition": "changes_more_than",
            "parameter": "position",
            "scope": "all",
            "is_read": 0
        }

        alert = Alert(caller, alert_body, None, camp_id)
        counter = AlertCount(caller, camp_id)
        marker = MarkAsRead(caller, camp_id)

        self.assertEqual(counter.count()['items_count'], 0)

        alert_id = alert.create()['alert_id']
        self.assertEqual(counter.count()['unread_items_count'], 1)

        self.assertIn(alert_id, alert.list()['alert_ids'])

        alert.update(alert_body_upd)
        new_domain = alert.read()
        self.assertEqual(alert_body_upd['domain'], new_domain['alert_body']['domain'])

        marker.mark()
        self.assertNotEqual(counter.count()['unread_items_count'], counter.count()['items_count'])

        alert.delete()
        alert_list = alert.list_read()['alert_ids']
        self.assertFalse(alert_list)

    @file_data('ids.json')
    def test_alert_list_delete(self, camp_id):
        caller = Caller(URL)

        alert_body = {
            "domain": "alert-list.com",
            "threshold": 13,
            "condition": "leaves_top",
            "parameter": "position",
            "scope": "all",
            "is_read": 0
        }

        alert_ids = []
        alert = Alert(caller, alert_body, None, camp_id)

        for i in range(0, 3):
            alert.create()
            alert_ids.append(alert.alert_id)

        self.assertEquals(alert_ids, alert.list()['alert_ids'])
        alert.list_delete(alert_ids)
        self.assertFalse(alert.list()['alert_ids'])


@ddt
class NegativeTesting(unittest.TestCase):
    @file_data('ids.json')
    def test_incorrect_values(self, camp_id):
        caller = Caller(URL)
        trigger_body = {
            "domain": "exception.com",
            "threshold": "",
            "condition": "changes_more_than",
            "parameter": "position",
            "scope": "all"
        }

        invalid_body = {
            "bullshit": "bullshit"
        }

        thresholds = [0, 101, -1]
        alert = Alert(caller, "Null", "incorrect_id", camp_id)
        invalid_key = 'invalid_key'
        invalid_id = 'invalid_id'

        for i in range(len(thresholds)):
            trigger_body['threshold'] = thresholds[i]
            trigger = Trigger(caller, trigger_body, "incorrect_id", camp_id, KEY)
            i += 1

            with self.assertRaises(Exception):
                trigger.create()
                trigger.read()
                alert.read()

        trigger = Trigger(caller, trigger_body, None, invalid_id, KEY)
        with self.assertRaises(Exception):
            trigger.create()

        trigger = Trigger(caller, trigger_body, None, camp_id, invalid_key)
        with self.assertRaises(Exception):
            trigger.create()

        trigger = Trigger(caller, invalid_body, None, camp_id, KEY)
        with self.assertRaises(Exception):
            trigger.create()

    @file_data('ids.json')
    def test_too_many_triggers(self, camp_id):
        caller = Caller(URL)
        trigger_body = {
            "domain": "exception.com",
            "threshold": "",
            "condition": "changes_more_than",
            "parameter": "position",
            "scope": "all"
        }

        trigger = Trigger(caller, trigger_body, None, camp_id, KEY)
        conditions = ['changes_more_than', 'enters_top', 'leaves_top', 'gains_more_than', 'loses_more_than']

        for i in range(0, 10):
            trigger_body['threshold'] = random.randint(1, 100)
            trigger_body['condition'] = conditions[random.randint(1, 4)]
            trigger.create()

        with self.assertRaises(Exception):
            trigger.create()

        trigger_ids = trigger.list()['trigger_ids']
        trigger.list_delete(trigger_ids)


@ddt
class ValidAlertTesting(unittest.TestCase):
    @file_data('ids.json')
    def test_changes_more_than(self, camp_id):
        diff = OrderedDict()
        num_kws, response = get_kws(camp_id, KEY)

        n = 0
        while n < num_kws:
            if response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != '-' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 'n/a' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 0:
                diff[response[str(n)]['Ph']] = response[str(n)]['Dt']['Diff']['*.amazon.com/*']
            n += 1

        if len(diff) == 0:
            self.skipTest("There were no changes in positions, hence - no alerts to be created")

        alerting(diff, "changes_more_than", 1, camp_id)

    @file_data('ids.json')
    def test_gains_more_than(self, camp_id):
        diff = OrderedDict()
        num_kws, response = get_kws(camp_id, KEY)

        n = 0
        while n < num_kws:
            if response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != '-' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 'n/a' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 0 and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] >= 1:  # hardcoded :(
                diff[response[str(n)]['Ph']] = response[str(n)]['Dt']['Diff']['*.amazon.com/*']
            n += 1

        if len(diff) == 0:
            self.skipTest("There were no expected changes in positions, hence - no alerts to be created")

        alerting(diff, "gains_more_than", 1, camp_id)

    @file_data('ids.json')
    def test_loses_more_than(self, camp_id):
        diff = OrderedDict()
        num_kws, response = get_kws(camp_id, KEY)

        n = 0
        while n < num_kws:
            if response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != '-' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 'n/a' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 0 and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] <= -1:  # hardcoded :(
                diff[response[str(n)]['Ph']] = response[str(n)]['Dt']['Diff']['*.amazon.com/*']
            n += 1

        if len(diff) == 0:
            self.skipTest("There were no expected changes in positions, hence - no alerts to be created")

        alerting(diff, "loses_more_than", 1, camp_id)

    @file_data('ids.json')
    def test_leaves_top(self, camp_id):
        diff = OrderedDict()
        num_kws, response = get_kws(camp_id, KEY)
        date_upd, prev_date = get_dates(camp_id, KEY)

        n = 0
        while n < num_kws:
            if response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != '-' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 'n/a' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] < 0 and \
                                    response[str(n)]['Dt'][str(prev_date)]['*.amazon.com/*'] <= 2 < \
                            response[str(n)]['Dt'][str(date_upd)]['*.amazon.com/*']:  # hardcoded :( leaves top 2.
                diff[response[str(n)]['Ph']] = response[str(n)]['Dt']['Diff']['*.amazon.com/*']
            n += 1

        if len(diff) == 0:
            self.skipTest("There were no expected changes in positions, hence - no alerts to be created")

        alerting(diff, "leaves_top", 2, camp_id)

    @file_data('ids.json')
    def test_enters_top(self, camp_id):
        diff = OrderedDict()
        num_kws, response = get_kws(camp_id, KEY)
        date_upd, prev_date = get_dates(camp_id, KEY)

        n = 0
        while n < num_kws:
            if response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != '-' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 'n/a' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] > 0 and \
                            response[str(n)]['Dt'][str(date_upd)]['*.amazon.com/*'] <= 5 < \
                            response[str(n)]['Dt'][str(prev_date)]['*.amazon.com/*']:  # hardcoded :( enters top 5.
                diff[response[str(n)]['Ph']] = response[str(n)]['Dt']['Diff']['*.amazon.com/*']
            n += 1

        if len(diff) == 0:
            self.skipTest("There were no expected changes in positions, hence - no alerts to be created")

        alerting(diff, "enters_top", 5, camp_id)

    @file_data('ids.json')
    def test_leaves_top_100(self, camp_id):
        self.skipTest("until bugfix")
        diff = OrderedDict()
        num_kws, response = get_kws(camp_id, KEY)
        date_upd, prev_date = get_dates(camp_id, KEY)

        n = 0
        while n < num_kws:
            if response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != '-' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 'n/a' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] < 0 and \
                            response[str(n)]['Dt'][str(date_upd)]['*.amazon.com/*'] == '-':
                diff[response[str(n)]['Ph']] = response[str(n)]['Dt']['Diff']['*.amazon.com/*']
            n += 1

        if len(diff) == 0:
            self.skipTest("There were no expected changes in positions, hence - no alerts to be created")

        alerting(diff, "leaves_top", 100, camp_id)

    @file_data('ids.json')
    def test_enters_top_100(self, camp_id):
        self.skipTest("until bugfix")
        diff = OrderedDict()
        num_kws, response = get_kws(camp_id, KEY)
        date_upd, prev_date = get_dates(camp_id, KEY)

        n = 0
        while n < num_kws:
            if response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != '-' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] != 'n/a' and \
                            response[str(n)]['Dt']['Diff']['*.amazon.com/*'] > 0 and \
                            response[str(n)]['Dt'][str(prev_date)]['*.amazon.com/*'] == '-':
                diff[response[str(n)]['Ph']] = response[str(n)]['Dt']['Diff']['*.amazon.com/*']
            n += 1

        if len(diff) == 0:
            self.skipTest("There were no expected changes in positions, hence - no alerts to be created")

        alerting(diff, "enters_top", 100, camp_id)


def get_ids(key):
    request = str(config_parser.get('requests', 'campaign_list_new')) + '&key=' + key
    response = requests.get(request)
    ids = []
    countries = json.loads(response.text)
    for c in countries:
        data = countries[c]['data']
        if data:
            for n in data:
                ids.append(n['Id'])
    with open('ids.json', 'w') as outfile:
        json.dump(ids, outfile)
        outfile.close()


def get_kws(campaign_id, key):
    request = str(config_parser.get('requests', 'campaign_data')) + '&campaign_id=' + campaign_id + '&key=' + key
    get = requests.get(request)
    number_kws = json.loads(get.content)['data']['Kc']  # number of kws in the campaign
    date_upd = json.loads(get.content)['data']['Vi'][7]['Dt']  # last date
    prev_date = json.loads(get.content)['data']['Vi'][6]['Dt']  # previous date
    request = str(config_parser.get('requests', 'rankings_overview')) + '&date_begin=' + prev_date + \
              '&date_end=' + date_upd + '&campaign_id=' + campaign_id + '&key=' + KEY
    get = requests.get(request)
    response = json.loads(get.content)['tracking_position_rankings_overview_organic']['data']
    return number_kws, response


# I know how ugly this is, but as for now - let it just do its job and not be beautiful


def get_dates(campaign_id, key):
    request = str(config_parser.get('requests', 'campaign_data')) + '&campaign_id=' + campaign_id + '&key=' + key
    get = requests.get(request)
    date_upd = json.loads(get.content)['data']['Vi'][7]['Dt']  # last date
    prev_date = json.loads(get.content)['data']['Vi'][6]['Dt']  # previous date
    return date_upd, prev_date


def alerting(diff, condition, threshold, camp_id):
    caller = Caller(URL)
    trigger_body = {
        "domain": "amazon.com",
        "threshold": threshold,
        "condition": condition,
        "parameter": "position",
        "scope": "all"
    }

    trigger = Trigger(caller, trigger_body, None, camp_id, KEY)
    alert = Alert(caller, None, None, camp_id)

    # clean some shit before creating triggers

    tr_list = trigger.list()
    if 'trigger_ids' in tr_list.keys():
        trigger_ids = trigger.list()['trigger_ids']
        trigger.list_delete(trigger_ids)

    trigger.create()

    # clean some shit before alerting

    al_list = alert.list()
    if 'alert_ids' in al_list.keys():
        alert_ids = alert.list()['alert_ids']
        alert.list_delete(alert_ids)

    event = Emit(camp_id)
    event.emit()

    time.sleep(5)  # sometimes alerts are not generated instantly. Gotta find better workaround though.

    try:
        alerts = alert.list_read()['alert_ids'][0]['alert_body']['keywords']
        if len(diff) != len(alerts):
            out = "Number of keywords in request and alert do not match!\ndiff: %s \nalerts: %s \nlen(diff): %s \nlen(alerts):%s " \
            % (diff, alerts, len(diff), len(alerts))
            raise Exception(out)

    except IndexError:
        print "Alert was not created, but there are kws which " + condition + " " + str(threshold) + " :"
        for key in diff:
            print "\n" + key
        exit()

    i = 0
    alerts_dict = OrderedDict()
    while i < len(alerts):
        alerts_dict[alerts[i]['keyword']] = alerts[i]['diff']
        i += 1

    matches = set(diff.items()) & set(alerts_dict.items())
    if len(matches) != len(diff):
        out = "Keywords in request and alert differ!\ndiff: %s \nalerts_dict: %s" % (diff, alerts_dict)
        raise Exception(out)

    trigger.delete()
    alert.alert_id = alert.list_read()['alert_ids'][0]['alert_id']
    alert.delete()


if __name__ == '__main__':
    global config_parser

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--config', '-c', metavar='config', help='config ini file')
    arg_parser.add_argument('unittest_args', nargs='*')

    args = arg_parser.parse_args()

    print args.config

    config_parser = SafeConfigParser()
    config_parser.read(args.config)

    KEY = config_parser.get('credentials', 'key')
    URL = config_parser.get('credentials', 'url')

    get_ids(KEY)

    sys.argv[1:] = args.unittest_args
    if is_running_under_teamcity():
        runner = TeamcityTestRunner()
    else:
        runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)

