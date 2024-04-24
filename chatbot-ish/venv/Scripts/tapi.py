#!C:\Users\hancomtst\chatbot-ish\venv\Scripts\python.exe
#! -*- coding: utf-8 -*-

__doc__ = """Framework for Testing APIs"""
__author__ = "Jimmy John <jimmyislive@gmail.com>"
__license__ = "MIT"

import argparse
from collections import OrderedDict
import copy
from datetime import datetime, timedelta
import hashlib
from importlib import import_module
import json
import os
import random
import sys
import traceback
import urlparse

from jsonpath_rw import jsonpath, parse
import requests

class TapiConfigException(Exception):
    """Exception thrown when the json config is not valid"""
    pass

class TapiExprEvaluator(object):

    """Utility class for detecting/evaluating tapi expressions."""

    @classmethod
    def is_tapi_expr(cls, value):
        """An expression is a tapi expression if it contains anything within double square brackets. [[...]]"""
        value = value.strip()
        return (value.find('[[') != -1 and value.find(']]') != -1)

    @classmethod
    def is_jsonpath_expr(cls, value):
        """An expression is a json path expression if it begins with $(which indicates the root element)"""
        value = value.strip()
        return value[0] == '$'

    @classmethod
    def _helper_get_expression_value(cls, test_output_so_far, value):
        """Helper method to extract the value of a token from the results so far"""
        if value.startswith('startup[') and value.endswith(']'):
            run_index = int(value[8:-1])
            token_value = test_output_so_far['startup']['run'][run_index]
            return token_value
        elif value.startswith('teardown[') and value.endswith(']'):
            run_index = int(value[9:-1])
            token_value = test_output_so_far['teardown']['run'][run_index]
            return token_value
        else:
            return test_output_so_far[value]

    @classmethod
    def normalize_request_tapi_expr(cls, value, test_output_so_far, config_data):
        """Executes a script or extracts the value of a token indicated by the tapi expression.

        This is called when evaluating tapi expressions within the 'request' subsection. Key point being that a script/token
        always returns a value to be used in the request.

        """
        value = value.strip()

        #is it a script?
        if value.startswith('[[script:'):
            script_name = value[9:-5]
            mod = import_module('{0}'.format(script_name))
            return mod.RequestRunner.get_value(test_output_so_far, config_data)
        #it's probably a token
        else:
            #NOTE: a token can reside anywhere within a string e.g. 'blah blah blah [[token]]'
            token_start_index = value.find('[[token:')
            token_end_index = value.find(']]')

            if token_start_index != -1 and token_end_index != -1:
                dot_names = value[token_start_index + 8:token_end_index]

                pieces = dot_names.split('.')

                token_value = cls._helper_get_expression_value(test_output_so_far, pieces[0])
                
                for piece in pieces[1:]:
                    token_value = cls._helper_get_expression_value(token_value, piece)

                return value[:token_start_index] + token_value + value[token_end_index + 2:]
            else:
                env_start_index = value.find('[[env:')
                env_end_index = value.find(']]')

                if env_start_index != -1 and env_end_index != -1:
                    env_var = value[env_start_index + 7:env_end_index]
                    try:
                        return os.environ[env_var]
                    except KeyError:
                        return ''
                else:
                    return ''

    @classmethod
    def get_response_tapi_expr(cls, value, test_output_so_far, test_config_data, response):
        """Allows us to execute arbitrary scripts to verify the output.

        Note that the output in these scripts should always be True/False. i.e. is the response correct as per the 
        provided spec in the json file
        """
        value = value.strip()

        #is it a script?
        if value.startswith('[[script:'):

            script_name = value[9:-5]
            mod = import_module('{0}'.format(script_name))
            return mod.ResponseRunner.validate(test_output_so_far, test_config_data, response)
        else:
            return value

class InputConfigValidator(object):
    """Validates input json file and ensures all key/values comply with spec.

    Methods in this class always return True if the field is OK, else an exception is raised.
    """

    @classmethod
    def verify_request(cls, request):
        """Request subsections has to have a url"""

        if not request.has_key('url'):
            raise TapiConfigException('Request needs a url')
        elif request.has_key('verb'):
            if request['verb'].lower() not in ['get', 'put', 'post', 'delete']:
                raise TapiConfigException('Only valid verbs are get|put|post|delete')

        return True

    @classmethod
    def verify_response(cls, response):
        if response.has_key('status_code'):
            try:
                int(response['status_code'])
            except:
                raise TapiConfigException('Response status code has to be an integer')
        if response.has_key('headers') and not type(response['headers']) in [unicode, str, dict]:
            raise TapiConfigException('Response headers has to be a dictionary or tapi expression string')
        if response.has_key('body') and not type(response['body']) in [unicode, str, dict]:
            raise TapiConfigException('Response body has to be a dictionary or string')

        return True

    @classmethod
    def verify_on_failure(cls, on_failure):
        """If present, only valid values are abort|continue"""

        if on_failure.lower() not in ['abort', 'continue']:
            raise TapiConfigException('Valid values for on_failure are abort|continue')

        return True

    @classmethod
    def verify_request_response(cls, config, is_common=False):
        """In the global 'common' section everything is optional. In all other subsections, 'request' is required."""
        try:
            cls.verify_request(config['request'])
        except KeyError:
            if is_common:
                pass
            else:
                raise

        if config.has_key('response'):
            cls.verify_response(config['response'])

        return True

    @classmethod
    def verify_startup_harness(cls, startup_harness_config):
        if not type(startup_harness_config) == list:
            raise TapiConfigException('Startup harness has to be a list')

        for startup_harness in startup_harness_config:
            for key in startup_harness.keys():
                return cls.verify_request_response(startup_harness[key])

    @classmethod
    def verify_teardown_harness(cls, teardown_harness_config):
        if not type(teardown_harness_config) == list:
            raise TapiConfigException('Teardown harness has to be a list')

        for teardown_harness in teardown_harness_config:
            for key in teardown_harness.keys():
                return cls.verify_request_response(teardown_harness[key])

    @classmethod
    def verify_startup(cls, startup_config, is_common = False):
        if not type(startup_config) == list:
            raise TapiConfigException('startup subsection should be of type list')

        for startup in startup_config:
            try:
                return cls.verify_request_response(startup['main'], is_common)
            except KeyError:
                raise TapiConfigException('startup section does not have a "main" subsection')

    @classmethod
    def verify_main(cls, main_config, is_common = False):
        return cls.verify_request_response(main_config, is_common)

    @classmethod
    def verify_teardown(cls, teardown_config, is_common = False):
        if not type(teardown_config) == list:
            raise TapiConfigException('teardown subsection should be of type list')

        for teardown in teardown_config:
            try:
                return cls.verify_request_response(teardown['main'], is_common)
            except KeyError:
                raise TapiConfigException('teardown section does not have a "main" subsection')

    @classmethod
    def verify_confirm(cls, confirm_config, is_common = False):
        return cls.verify_request_response(confirm_config, is_common)

    @classmethod
    def verify_common(cls, common_config):
        if not type(common_config) == dict:
            raise TapiConfigException('Common has to be a dict')
        if common_config.has_key('startup'):
            cls.verify_startup(common_config['startup'], True)
        if common_config.has_key('main'):
            cls.verify_main(common_config['main'], True)
        if common_config.has_key('confirm'):
            cls.verify_confirm(common_config['confirm'], True)
        if common_config.has_key('teardown'):
            cls.verify_teardown(common_config['teardown'], True)

        return True

    @classmethod
    def verify_tests(cls, tests):

        if not len(tests):
            raise TapiConfigException('At least one test must be specified')

        test_ids = []

        for test in tests:

            if test.has_key('id'):
                if test['id'] in test_ids:
                    raise TapiConfigException('test ids have to be unique. {0} is repeated'.format(test['id']))
                else:
                    test_ids.append(test['id'])

            if test.has_key('startup'):
                cls.verify_startup(test['startup'])

            try:
                cls.verify_main(test['main'])
            except KeyError:
                raise TapiConfigException('A main subsection in a test is required')

            if test.has_key('confirm'):
                cls.verify_confirm(test['confirm'])

            if test.has_key('teardown'):
                cls.verify_teardown(test['teardown'])

        return True

class OutputResponseValidator(object):
    """Validates the actual response with the expected response"""

    @classmethod
    def validate_response_status_code(cls, test_output_so_far, test_config_data, config_status_code, response_status_code):
        return int(config_status_code) == int(response_status_code)

    @classmethod
    def validate_response_headers(cls, test_output_so_far, test_config_data, config_response_headers, response_headers):
        for k,v in config_response_headers.items():
            if TapiExprEvaluator.is_tapi_expr(v):
                if not TapiExprEvaluator.get_response_tapi_expr(v, test_output_so_far, test_config_data, response_headers):
                    return False, 'Script {0} validation failed'.format(v)
            else:
                try:
                    if config_response_headers[k] == '*':
                        #we don't care what value the response header has, just the key needs to be there
                        if response_headers.keys().count(k):
                            continue
                        else:
                            return False, 'Header {0} is not present in the response'.format(k)

                    if v.lower() != response_headers[k].lower():
                        return False, 'Expected {0}, Got {1}'.format(v, response_headers[k])
                except KeyError:
                    return False, 'Header {0} does not exist in the response'.format(k)

        return True, None

    @classmethod
    def validate_response_body(cls, test_output_so_far, test_config_data, config_response_body, response_body):
        if type(config_response_body) == dict:
            for k,v in config_response_body.items():
                if TapiExprEvaluator.is_tapi_expr(v):
                    if not TapiExprEvaluator.get_response_tapi_expr(v, test_output_so_far, test_config_data, response_body):
                        return False, 'Script {0} validation failed'.format(v)
                elif TapiExprEvaluator.is_jsonpath_expr(k):

                    json_expr = parse(k)
                    try:
                        matches = json_expr.find(json.loads(response_body))
                    except:
                        return False, 'Json path expression {0} did not find any match against {1}'.format(k, response_body)

                    if v == '*':
                        return True, None

                    if not (len(matches) and matches[0].value == v):
                        return False, 'Json path expression {0} did not validate against {1}'.format(k, v)
        else:
            if TapiExprEvaluator.is_tapi_expr(config_response_body):
                if not TapiExprEvaluator.get_response_tapi_expr(config_response_body, test_output_so_far, test_config_data, response_body):
                        return False, 'Script {0} validation failed'.format(config_response_body)

        return True, None

class Tapi(object):

    """Read in the config into this object. Verify and run tests."""

    def __init__(self, config_data):

        try:
            self.heading = config_data['heading']
        except KeyError:
            self.heading = ''

        try:
            self.base_url = config_data['base_url']
        except KeyError:
            self.base_url = ''

        try:
            InputConfigValidator.verify_common(config_data['common'])
            self.common = config_data['common']
        except KeyError:
            self.common = {}

        try:
            InputConfigValidator.verify_on_failure(config_data['on_failure'])
            self.on_failure = config_data['on_failure']
        except KeyError:
            self.on_failure = 'continue'

        try:
            InputConfigValidator.verify_startup_harness(config_data['startup_harness'])
            self.startup_harness = config_data['startup_harness']
        except KeyError:
            self.startup_harness = []

        try:
            InputConfigValidator.verify_teardown_harness(config_data['teardown_harness'])
            self.teardown_harness = config_data['teardown_harness']
        except KeyError:
            self.teardown_harness = []

        try:
            InputConfigValidator.verify_tests(config_data['tests'])
            self.tests = config_data['tests']
        except KeyError:
            self.tests = []

    def run_startup_harness(self, test_result_so_far = {}):
        """A stratup Harness is run only once, just before all the tests."""

        return self.run_test('startup_harness', test_result_so_far, self.startup_harness)

    def run_teardown_harness(self, test_result_so_far):
        """A teardown harness is run only once, just after all the tests."""

        return self.run_test('teardown_harness', test_result_so_far, self.teardown_harness)

    def run_startup(self, test_result_so_far, test_config):
        """The startup section is run once for every test."""
        try:
            for test in test_config['startup']:
                test_result_so_far = self.run_test('startup', test_result_so_far, test['main'])
        except KeyError:
            test_result_so_far = self.run_test('startup', test_result_so_far, [])

        return test_result_so_far

    def run_main_test(self, test_result_so_far, test_config):
        """The main api being tested"""

        return self.run_test('main', test_result_so_far, test_config['main'] if test_config.has_key('main') else {})

    def run_test_confirm(self, test_result_so_far, test_config):
        """Ensure that the api did what it claimed to have done."""

        if test_config.has_key('confirm'):
            return self.run_test('confirm', test_result_so_far, test_config['confirm'])
        else:
            return test_result_so_far

    def run_teardown(self, test_result_so_far, test_config):
        """The teardown section is run once for every test."""
        try:
            for test in test_config['teardown']:
                test_result_so_far = self.run_test('teardown', test_result_so_far, test['main'])
        except KeyError:
            test_result_so_far = self.run_test('teardown', test_result_so_far, [])

        return test_result_so_far

    def _helper_get_request_cfg_val(self, run_subsection_name, test_output_so_far, config_data, key):

        if config_data['request'].has_key(key):
            if type(config_data['request'][key]) == dict:
                for k,v in config_data['request'][key].items():
                    if TapiExprEvaluator.is_tapi_expr(v):
                        config_data['request'][key][k] = TapiExprEvaluator.normalize_request_tapi_expr(v, test_output_so_far, config_data)
            else:
                if TapiExprEvaluator.is_tapi_expr(config_data['request'][key]):
                    config_data['request'][key] = TapiExprEvaluator.normalize_request_tapi_expr(config_data['request'][key], test_output_so_far, config_data)

        if run_subsection_name in ['startup', 'teardown']:
            if config_data['request'].has_key(key):
                return config_data['request'][key]
            else:
                return {}
        else:
            try:
                config_request_param = copy.deepcopy(self.common[run_subsection_name]['request'][key])
            except KeyError:
                config_request_param = {}
            
            if config_data['request'].has_key(key):
                #e.g. headers
                if type(config_data['request'][key]) == dict:
                    #override with new values
                    config_request_param.update(config_data['request'][key])

                else:
                    #if string, e.g. payload can be the output of a script, use as is
                    config_request_param = config_data['request'][key]

            return config_request_param

    def _helper_get_response_cfg_val(self, run_subsection_name, config_data, key):
        if config_data.has_key('response'):
            if run_subsection_name in ['startup', 'teardown']:
                if config_data['response'].has_key(key):
                    return config_data['response'][key]
                else:
                    return None
            else:
                try:
                    config_response_param = copy.deepcopy(self.common[run_subsection_name]['response'][key])
                except KeyError:
                    config_response_param = None

                if config_data['response'].has_key(key):
                    #e.g. headers
                    if type(config_data['response'][key]) == dict and type(config_response_param) == dict:
                        #override with new values
                        config_response_param.update(config_data['response'][key])
                    else:
                        #if string, e.g. body can be the output of a script, use as is
                        config_response_param = config_data['response'][key]

                return config_response_param
        else:
            return None

    def _build_base_test_output(self, requests_method, url, config_request_payload, config_request_headers, config_response_status_code):
        """Populate all request/response params so it can be referenced later"""

        output = {}
        output['request'] = {}
        output['request']['url'] = url
        output['request']['action'] = str(requests_method)
        output['request']['payload'] = config_request_payload
        output['request']['headers'] = config_request_headers
        output['response'] = {}
        output['response']['status_code'] = config_response_status_code
        output['response']['headers'] = {}
        output['response']['body'] = ''
        output['status'] = True
        output['status_msg'] = []

        return output

    def _helper_create_test_id(self, test_config):
        """Every test has an id. This method generates one if you do not provide one."""
        return hashlib.sha256(str(datetime.now) + str(random.randrange(1,1000000))).hexdigest()

    def run_test(self, run_subsection_name, test_output_so_far, config_data):
        """Runs the test encapsulated by config_data"""

        if config_data:

            #request payload...
            config_request_payload = self._helper_get_request_cfg_val(run_subsection_name, test_output_so_far, config_data, 'payload')
            #request headers...
            config_request_headers = self._helper_get_request_cfg_val(run_subsection_name, test_output_so_far, config_data, 'headers')

            if config_data['request'].has_key('verb'):
                if config_data['request']['verb'].lower() == 'get':
                    requests_method = requests.get
                elif config_data['request']['verb'].lower() == 'post':
                    requests_method = requests.post
                elif config_data['request']['verb'].lower() == 'put':
                    requests_method = requests.put
                elif config_data['request']['verb'].lower() == 'delete':
                    requests_method = requests.delete
            else:
                requests_method = requests.get

            try:
                if TapiExprEvaluator.is_tapi_expr(config_data['request']['url']):
                    url = TapiExprEvaluator.normalize_request_tapi_expr(config_data['request']['url'], test_output_so_far, config_data)
                else:
                    url = config_data['request']['url']

                if self.base_url:
                    url = urlparse.urljoin(self.base_url, url)

                response = requests_method(url, data=config_request_payload, headers=config_request_headers)

                #response status code
                config_response_status_code = self._helper_get_response_cfg_val(run_subsection_name, config_data, 'status_code') or 200
                #response headers...
                config_response_headers = self._helper_get_response_cfg_val(run_subsection_name, config_data, 'headers') or {}

                #response body...
                config_response_body = self._helper_get_response_cfg_val(run_subsection_name, config_data, 'body') or {}

                test_output = self._build_base_test_output(requests_method, url, config_request_payload, config_request_headers,
                              config_response_status_code)

                test_output['response']['status_code'] = response.status_code
                test_output['response']['headers'] = response.headers
                test_output['response']['body'] = response.text

                if not OutputResponseValidator.validate_response_status_code(test_output_so_far, config_data, config_response_status_code, response.status_code):
                    test_output['status'] = False
                    test_output['status_msg'].append('Status code check failed. Expected {0}, Got {1}'.format(config_response_status_code, response.status_code))

                out, reason = OutputResponseValidator.validate_response_headers(test_output_so_far, config_data, config_response_headers, response.headers)
                if not out:
                    test_output['status'] = False
                    test_output['status_msg'].append('Response header mismatch: {0}'.format(reason))

                out, reason = OutputResponseValidator.validate_response_body(test_output_so_far, config_data, config_response_body, response.text)
                if not out:
                    test_output['status'] = False
                    test_output['status_msg'].append('Response body mismatch: {0}'.format(reason))

                #test_output_so_far[run_subsection_name] = test_output
                if run_subsection_name in ['startup', 'teardown']:
                    test_output_so_far[run_subsection_name] = {}
                    test_output_so_far[run_subsection_name]['status'] = test_output['status']
                    test_output_so_far[run_subsection_name]['status_msg'] = test_output['status_msg']
                    try:
                        test_output_so_far[run_subsection_name]['run'].append({'main':test_output})
                    except KeyError:
                        test_output_so_far[run_subsection_name]['run'] = [{'main':test_output}]
                else:
                    test_output_so_far[run_subsection_name] = test_output

                test_output_so_far['status'] = test_output['status']
                test_output_so_far['status_msg'] = test_output['status_msg']
                test_output_so_far['last_section'] = run_subsection_name

                return test_output_so_far

            except Exception, e:
                raise 

        else:
            test_output_so_far[run_subsection_name] = {}
            if run_subsection_name in ['startup', 'teardown']:
                test_output_so_far[run_subsection_name]['run'] = []

            test_output_so_far[run_subsection_name]['status'] = True
            test_output_so_far[run_subsection_name]['status_msg'] = ['No "{0}" section'.format(run_subsection_name)]
            test_output_so_far['status'] = True
            test_output_so_far['last_section'] = run_subsection_name

            return test_output_so_far

    def run(self, test_ids):
        """Iterates through all the tests and runs them"""

        #stats bookkeeping
        full_run_test_output = {}
        full_run_test_output['tot_time'] = timedelta(0)
        full_run_test_output['tot_count'] = 0
        full_run_test_output['fail_count'] = 0
        full_run_test_output['pass_count'] = 0
        full_run_test_output['results'] = OrderedDict()

        #first run the startup_harness
        full_run_test_output['startup_harness'] = self.run_startup_harness()

        test_ids_list = test_ids.split(',')

        if full_run_test_output['startup_harness']['status']:

            for test_config in self.tests:

                if test_ids != '*':
                    if not test_config.has_key('id'):
                        continue
                    if test_config['id'] not in test_ids_list:
                        continue

                full_run_test_output['tot_count'] += 1

                start_time = datetime.now()

                try:
                    name = test_config['name']
                except KeyError:
                    name = test_config['main']['request']['url']

                print 'running test: {0}...'.format(name)

                #for each test run the startup / main / confirm / teardown sections (in that order)
                #if any of them fail, the test is considered to have failed.

                single_run_test_result = {'name': name}
                single_run_test_result['startup_harness'] = full_run_test_output['startup_harness']
                single_run_test_result = self.run_startup(single_run_test_result, test_config)

                if single_run_test_result['status']:
                    single_run_test_result = self.run_main_test(single_run_test_result, test_config)
                    if single_run_test_result['status']:
                        single_run_test_result = self.run_test_confirm(single_run_test_result, test_config)
                        if single_run_test_result['status']:
                            single_run_test_result = self.run_teardown(single_run_test_result, test_config)
                            if single_run_test_result['status']:
                                full_run_test_output['pass_count'] += 1
                            else:
                                full_run_test_output['fail_count'] += 1
                        else:
                            full_run_test_output['fail_count'] += 1
                    else:
                        full_run_test_output['fail_count'] += 1
                else:
                    full_run_test_output['fail_count'] += 1

                end_time = datetime.now()

                single_run_test_result['time_taken'] = (end_time - start_time)
                full_run_test_output['tot_time'] += single_run_test_result['time_taken']

                try:
                    test_id = test_config['id']
                except KeyError:
                    test_id = self._helper_create_test_id(test_config)

                full_run_test_output['results'][test_id] = single_run_test_result

                if ((self.on_failure == 'abort') and (single_run_test_result['status'] == False)):
                    break

        full_run_test_output['teardown_harness'] = self.run_teardown_harness(full_run_test_output)

        return full_run_test_output

def parse_and_run(config_file, test_ids, only_verify_flag=False):
    """Parses out the diferrent sections of the config file"""

    sys.path.append(os.path.dirname(os.path.realpath(config_file)))

    with open(config_file, 'r') as fp:
        try:
            config_data = json.load(fp)
            try:
                tapi = Tapi(config_data)
            except TapiConfigException, e:
                traceback.print_exc(file=sys.stdout)
                sys.exit(1)

            if not only_verify_flag:
                test_output = tapi.run(test_ids)
                print
                print 'Summary: {0}'.format(tapi.heading)
                print '********'
                print 'Total tests run: {0}'.format(test_output['tot_count'])
                print 'Total tests failed: {0}'.format(test_output['fail_count'])
                print 'Total tests passed: {0}'.format(test_output['pass_count'])
                print 'Total time taken: {0} seconds'.format(test_output['tot_time'])
                print
                print 'Test Results'
                print '************'
                for id_key, output in test_output['results'].items():
                    print '{0} - {1} ({2})'.format(output['name'], 'Pass' if output['status'] else 'Fail ', str(output['time_taken']))
                    if not output['status']:
                        last_section = output['last_section']
                        print '\t Details:'
                        if last_section in ['startup', 'teardown']:
                            print '\t\t Request Url: {0}'.format(output[last_section]['run'][-1]['main']['request']['url'])
                            print '\t\t Request Action: {0}'.format(output[last_section]['run'][-1]['main']['request']['action'])
                            print '\t\t Request Payload: {0}'.format(output[last_section]['run'][-1]['main']['request']['payload'])
                            print '\t\t Request Headers: {0}'.format(output[last_section]['run'][-1]['main']['request']['headers'])
                            print '\t\t Response Headers: {0}'.format(output[last_section]['run'][-1]['main']['response']['headers'])
                            print '\t\t Response Body: {0}'.format(output[last_section]['run'][-1]['main']['response']['body'])
                            print '\t\t Error Msg: {0}'.format(output[last_section]['status_msg'])
                        else:
                            print '\t\t Request Url: {0}'.format(output[last_section]['request']['url'])
                            print '\t\t Request Action: {0}'.format(output[last_section]['request']['action'])
                            print '\t\t Request Payload: {0}'.format(output[last_section]['request']['payload'])
                            print '\t\t Request Headers: {0}'.format(output[last_section]['request']['headers'])
                            print '\t\t Response Headers: {0}'.format(output[last_section]['response']['headers'])
                            print '\t\t Response Body: {0}'.format(output[last_section]['response']['body'])
                            print '\t\t Error Msg: {0}'.format(output[last_section]['status_msg'])
                    print
                print

            else:
                print 'File {0} seems to be legit...'.format(config_file)

        except ValueError:
            print 'Invalid json file:'
            print '********************'
            traceback.print_exc(file=sys.stdout)
            print '********************'
            sys.exit(1)

def main():
    """Parse out command line"""

    parser = argparse.ArgumentParser(description='Testing APIs')
    parser.add_argument('-c', '--config', help='location of the tapi.cfg file (default is current dir)')
    parser.add_argument('-v', '--verify', help='only verify the config file, don\'t run any tests', action='store_true', default=False)
    parser.add_argument('-i', '--ids', help='only run tests with these comma separated ids', default='*')
    args = parser.parse_args()

    if not args.config:
        config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tapi.json')
    else:
        config_file = args.config

    if not os.path.exists(config_file):
        print 'File {0} not found'.format(config_file)
        sys.exit(1)

    parse_and_run(config_file, args.ids, args.verify)

if __name__ == '__main__':
    main()

