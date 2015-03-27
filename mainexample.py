'''
Created on Mar 26, 2015

@author: isemenov
'''
import awspricingfull


if __name__ == '__main__':
    awspf= awspricingfull.AllAWSPrices()
    awspf.print_json("reserved")
    