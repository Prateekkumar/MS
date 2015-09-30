from __future__ import with_statement
import unittest
import xmlrunner
import os
import sys
import time
import csv
from fabric.api import *
from subprocess import Popen
from fabric.network import disconnect_all

sys.path.append(os.path.normpath(os.path.realpath(__file__)+"/../../../"))
from toolbox.configuration import *
from toolbox.controlblu import *
from toolbox.controlpublisher import *
from toolbox.tests import *
from toolbox.parse import *
from toolbox.mbSlave import *
from toolbox.generateData import *

# Test suite name: testWindowing
# Author: Drew Garner
# Test suite descriptions: Tests the windowing feature of BLU


class testWindowing (unittest.TestCase):
    """ Sets up the configuration needed for this test"""
    def setUp(self):
        self.confVals = {}
        self.saved_path = os.getcwd()
        config_filename = ("test-suites/%s/%s.conf" %
                           (self.__class__.__name__,
                            self.__class__.__name__))
        self.confVals = read_configuration(config_filename)
        self.confVals['sensor1_ip'] = find_my_ip()

        # Set all of the global Fabric variables
        env.user = self.confVals['user']
        env.hosts = self.confVals['blu_server_ip'].split(",")
        env.password = self.confVals['password']

    @unittest.skip("demonstrating skipping")
    def test_Max(self, interval=100):
        """
        Tests that the windowed value with a Max policy is correct
        """
        print "==========================================="
        print "test_Max: Testing with Max windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestMax():

            self.confVals['window_policy'] = self.confVals['max_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            exp_val = max(agg_values)
                            act_val = float(self.get_actual_value(row))
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestMax)

    @unittest.skip("demonstrating skipping")
    def test_Min(self, interval=100):
        """
        Tests that the windowed value with a Max policy is correct
        """
        print "==========================================="
        print "test_Min: Testing with Min windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestMin():

            self.confVals['window_policy'] = self.confVals['min_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            exp_val = min(agg_values)
                            act_val = float(self.get_actual_value(row))
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestMin)

    #@unittest.skip("demonstrating skipping")
    def test_Avg(self, interval=100):
        """
        Tests that the windowed value with a Max policy is correct
        """
        print "==========================================="
        print "test_Avg: Testing with Avg windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestAvg():

            self.confVals['window_policy'] = self.confVals['avg_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            exp_val = sum(agg_values) / float(len(agg_values))
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            print "Expected Window Value before trunkation: %f" % exp_val
                            exp_val = float("%.02f"%exp_val)
                            act_val = float(self.get_actual_value(row))
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestAvg)

    @unittest.skip("demonstrating skipping")
    def test_Sum(self, interval=100):
        """
        Tests that the windowed value with a Sum policy is correct
        """
        print "==========================================="
        print "test_Sum: Testing with Sum windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestSum():

            self.confVals['window_policy'] = self.confVals['sum_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            exp_val = sum(agg_values)
                            act_val = float(self.get_actual_value(row))
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestSum)

    @unittest.skip("demonstrating skipping")
    def test_Max_Abs(self, interval=100):
        """
        Tests that the windowed value with a Absolute Max policy is correct
        """
        print "==========================================="
        print "test_AbsMax: Testing with Abs Max windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestAbsMax():

            self.confVals['window_policy'] = self.confVals['abs_max_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            exp_val = agg_values[0]
                            for i in agg_values:
                                if abs(i) > abs(exp_val):
                                    exp_val = i
                            act_val = float(self.get_actual_value(row))
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestAbsMax)

    @unittest.skip("demonstrating skipping")
    def test_Min_Abs(self, interval=100):
        """
        Tests that the windowed value with a Absolute Min policy is correct
        """
        print "==========================================="
        print "test_AbsMin: Testing with Abs Min windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestAbsMin():

            self.confVals['window_policy'] = self.confVals['abs_min_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            exp_val = agg_values[0]
                            for i in agg_values:
                                if abs(i) < abs(exp_val):
                                    exp_val = i
                            act_val = float(self.get_actual_value(row))
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestAbsMin)

    @unittest.skip("demonstrating skipping")
    def test_Avg_Abs(self, interval=100):
        """
        Tests that the windowed value with a Absolute Avg policy is correct
        """
        print "==========================================="
        print "test_AbsAvg: Testing with Abs Avg windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestAbsAvg():

            self.confVals['window_policy'] = self.confVals['abs_avg_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            exp_val = sum(abs(i) for i in agg_values) / float(len(agg_values))
                            print "Expected Window Value before trunkation: %f" % exp_val
                            exp_val = float("%.02f"%exp_val)
                            act_val = float(self.get_actual_value(row))
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestAbsAvg)

    @unittest.skip("demonstrating skipping")
    def test_Sum_Abs(self, interval=100):
        """
        Tests that the windowed value with a Absolute Sum policy is correct
        """
        print "==========================================="
        print "test_AbsSum: Testing with Abs Sum windowing policy"
        print "==========================================="
        @task  # Defines the task so that fabric can use it
        def runTestAbsSum():

            self.confVals['window_policy'] = self.confVals['abs_sum_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems(repetitions=100)
            
            self.start_blu()
            time.sleep(3)

            # Run the three "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location']))
            publisher_path = publisher_path.split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
            interval = int(self.confVals['alignment_timer']) / 2
            pub1 = Popen([publisher_path, '--file=%s' % "input.csv",
                                          '--port=%s' % self.confVals['sensor1_port'],
                                          '--logtime=0',
                                          '--interval=%f' % interval])
            pub1.wait()
            time.sleep(2)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            os.chdir(self.saved_path)
            
            status = stop_blu()

            self.assertFalse("is running" in status, "BLU is still running!")

            # #############################################################
            os.chdir("test-suites/tmp")

            outputLogPath = os.path.normpath(os.getcwd()+self.confVals['blu_log'])


            # Grab the new log file
            get(self.confVals['remote_log'], outputLogPath)
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences..."

            agg_values = []
            wnd_found = False
            num_wnd = 0
            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if wnd_found == True and "AGG" in row[3] and "Max" not in row[4]:
                        val = self.get_actual_value(row)
                        if val != None:
                            agg_values.append(val)
                    if "WND" in row[3] and self.confVals['algo_name_1'] in row[4]:
                        if wnd_found == True and len(agg_values) != 0:
                            exp_val = sum(abs(i) for i in agg_values)
                            act_val = float(self.get_actual_value(row))
                            print "-----------------------------------------------"
                            print "Agg values: %r" % agg_values
                            print "Expected Window Value: %f" % exp_val
                            print "Actual Window Value: %f" % act_val
                            if(act_val != exp_val):
                                print "==============="
                                print "Values not Equal!"
                                print "==============="
                            print "-----------------------------------------------"
                            self.assertEqual(act_val, exp_val, "Actual value %f does't match expected value %f (Line %s, Col %s)" % (act_val, exp_val, row, 5))
                            agg_values = []
                        wnd_found = True
                        num_wnd = num_wnd + 1

            self.assertTrue(num_wnd >= 10, "There should be at least 10 windowing events but only %f were found" % num_wnd)
            print "The Windowing for this situation appears okay"
        execute(runTestAbsSum)

    def get_actual_value(self, row):
        result = None
        for val in row:
            if '*' in val:
                result =  val[1:]
        try:
            result = float(result)
        except ValueError:
            result = None
        return result

    def prepare_blu(self, vMap="virtualChannelMap.csv", template="template.conf"):
        current_dir = os.getcwd()
        os.chdir("test-suites/"+self.__class__.__name__)
        fill_blud_template(self.confVals)

        put(self.confVals['blu_config'], "/tmp")
        sudo("mv /tmp/blud.conf %s" % self.confVals['blu_bin_location'])

        put(vMap, "/tmp")
        sudo("mv /tmp/%s %s/virtualChannelMap.csv" % (vMap, self.confVals['blu_bin_location']))
        # sudo("rm -f %s"%self.confVals['remote_info_log'])
        os.chdir(current_dir)

    def start_blu(self, testGood=True):
        status = start_blu()  # Attempts to start BLU
        if testGood:
            self.assertTrue("is running" in status, "BLU is not running!")
            time.sleep(3)
            status = status_blu()
            self.assertTrue("is running" in status, "BLU is not running!")
            enable_logging(self.confVals['blu_server_ip'])

    def tearDown(self):
        os.chdir(self.saved_path)
        disconnect_all()


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
