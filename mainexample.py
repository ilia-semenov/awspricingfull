'''
Created on Mar 26, 2015

@author: isemenov
'''
import awspricingfull


if __name__ == '__main__':
    awspf=awspricingfull.AllAWSPrices()
    awspf.save_csv("all","C:\\AWS_DATA\\pricing_data\\")
    