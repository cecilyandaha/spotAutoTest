import unittest

from BeautifulReport import BeautifulReport


#from TestContractParam import TestContractParam
from Test_Java_Interface import TestJavaInterface

if __name__ == "__main__":
    print(unittest)
    #suite = unittest.TestSuite()
    #suite.addTest(TestContractParam('test_price_limit_rate'))
    suite = unittest.TestLoader().discover(".")
    result = BeautifulReport(suite)
    result.report(filename='测试报告', description='测试deafult报告', report_dir='report', theme='theme_default')

