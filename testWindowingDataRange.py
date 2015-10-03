"""
__test_name_: testWindowing

__author_: Prateek Kumar

__date_: 2.10.2015 

__test_description_: Tests the windowing data Range of BLU.
"""

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


class testWindowingDataRange (unittest.TestCase):
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

    #@unittest.skip("demonstrating skipping")
    def test_DataRange(self, interval=100):
        """
        Tests the data range of windowing in BLU
        """
        print "test_DataRange-Tests the windowing data range of BLU"
        
	@task  # Defines the task so that fabric can use it
        def runTestDataRange():

	    #Putting the window policy of 3
            self.confVals['window_policy'] = self.confVals['sum_key']
            self.prepare_blu(vMap="virtualChannelMap.csv", template=self.confVals['template_name'])
            os.chdir("./test-suites/tmp")
            generate_cdfLog_hfems_ones(repetitions=15,HP=False,numChannels=1,numFreqs=1,runLength=5,startVal=0)
            
            self.start_blu()
            time.sleep(3)

            # Run the "HFEMS" CDF publishers
            publisher_path = (os.path.normpath(os.getcwd()+
                              self.confVals['cdf_publisher_location'])).split()[0]
            print "Publisher at :%s" % publisher_path
            print "Running in :%s" % os.getcwd()
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

            # Getting the new log file from the bLU log
            get(self.confVals['remote_log'], outputLogPath)

	    #making sure the original output log file is present.
            self.assertTrue(os.path.isfile(outputLogPath), "The original output log of Blu does not exist")

            print "Testing for differences"

            with open(outputLogPath, "rb") as csvfile:
                csvre = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in csvre:
                    if "WND" in row[3] and "form1" in row[4]:
			print "The sum of  Agg value will 5.0 in this situation"
                        exp_val = float(5.0)
                        act_val = float(self.get_actual_value(row))
                        print "-----------------------------------------------"
                        print "Agg values: %r" % float(5.0)
                        print "Expected Window Value: %f" % exp_val
                        print "Actual Window Value: %f" % act_val
                        if(act_val != exp_val):
                            print "******************************************"
                            print "Values not Equal!"
                            print "******************************************"
                       	print "-----------------------------------------------"
                        self.assertEqual(act_val, exp_val)
            print "The Windowing data range for this situation appears okay"
        execute(runTestDataRange)


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
