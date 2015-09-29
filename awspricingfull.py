#!/usr/bin/python
#
# Copyright (c) 2015 Ilia Semenov (ilya.v.semenov@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""AWS Instances (EC2, ElastiCache, RDS, Redshift) pricing retrieval project.

Project contains one module which is designed to retrieve the AWS prices for 
four major AWS services that have reserved instances involved: EC2, ElastiCache, 
RDS and Redshift. The prices either On-Demand or Reserved (specified by user) can 
be retrieved to Command Line in JSON, Table (Prettytable) or CSV formats. CSV format 
option also saves the csv file to the folder specified by user, which is the main 
use case.

The undocumented AWS pricing APIa are used as the sources. The same APIs  serve
the data to the AWS pricing pages.
Both current and previous generation instance prices are retrieved.

Latest update: New pricing scheme (noUpfront, allUpfront, PartialUpfront) compatibility for RDS and Redshift is added. Minor bugs fixed.

Created: 25 March, 2015

Updated: 19 June, 2015

@author: Ilia Semenov

@version: 2.0
"""


import urllib2
import csv
import re
try:
    import simplejson as json
except ImportError:
    import json
import os



class AWSPrices(object):
    """
    Abstract class - base for the pricing retrieval classes for different 
    services.
    
    Attributes:
        DEFAULT_CURRENCY (str): USD Currency used in every AWS pricing by 
            default.
        REGIONS (list of str): List of AWS regions.
        JSON_NAME_TO_REGIONS_API (dict of str: str): Mapping of some internal 
            AWS region names used in few sources to the conventional ones.
            
    """

    DEFAULT_CURRENCY = "USD"
    
    REGIONS = [
    "us-east-1",
    "us-west-1",
    "us-west-2",
    "eu-west-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-northeast-1",
    "sa-east-1",
    "eu-central-1",
    "us-gov-west-1"
    ]
    
    JSON_NAME_TO_REGIONS_API = {
    "us-east" : "us-east-1",
    "us-east-1" : "us-east-1",
    "us-west" : "us-west-1",
    "us-west-1" : "us-west-1",
    "us-west-2" : "us-west-2",
    "eu-ireland" : "eu-west-1",
    "eu-west-1" : "eu-west-1",
    "apac-sin" : "ap-southeast-1",
    "ap-southeast-1" : "ap-southeast-1",
    "ap-southeast-2" : "ap-southeast-2",
    "apac-syd" : "ap-southeast-2",
    "apac-tokyo" : "ap-northeast-1",
    "ap-northeast-1" : "ap-northeast-1",
    "sa-east-1" : "sa-east-1",
    "eu-central-1":"eu-central-1",
    "us-gov-west-1":"us-gov-west-1",
    "eu-frankfurt":"eu-central-1"
    }
    
    def load_data(self,url):
        """
        Method for retrieving the pricing data in a clean dictionary format.
        
        Args:
            url: The pricing source url.
            
        Returns:
            data (dict of dict: dict): Pricing data in a dictionary format
               
        """
          
        f = urllib2.urlopen(url).read()
        f = re.sub("/\\*[^\x00]+\\*/", "", f, 0, re.M)
        f = re.sub("([a-zA-Z0-9]+):", "\"\\1\":", f)
        f = re.sub(";", "\n", f)
        f = re.sub("callback\(", "", f)
        f = re.sub("\)$", "", f)
        data = json.loads(f)
        return data
    

    def none_as_string(self,v):
            """
            Method for returning a blank string instead of None.
            
            Args:
                v: The value to be checked for None.
            
            Returns:
                v or "" is v is None.
            
            """
            if not v:
                return ""
            else:
                return v
    
    
    def get_ondemand_instances_prices(self):
        """
        Abstract method for getting On-Demand pricing. 
            Implemented in child classes.
        
        Raises:
           NotImplementedError: Abstract method is not implemented.
                
        """
        raise NotImplementedError( "Should have implemented this" )
    

    def get_reserved_instances_prices(self):
        """
        Abstract method for getting Reserved pricing. 
            Implemented in child classes.
        
        Raises:
           NotImplementedError: Abstract method is not implemented.
                
        """
        raise NotImplementedError( "Should have implemented this" )
    

    def return_json(self,u):
        """
        Method printing the pricing data in JSON format to Console.
        
        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
        
        Returns:
           str: Pricing data in JSON string format or an error message.
                
        """
        if u not in ["ondemand","reserved"]:
            print("Function requires 1 parameter. Possible values:"
                  "\"ondemand\" or \"reserved\".")
        else:        
            if u == "ondemand":
                data = self.get_ondemand_instances_prices()
            elif u == "reserved":
                data = self.get_reserved_instances_prices()           
            return (json.dumps(data))
        


class EC2Prices(AWSPrices):
    """
    Class for retrieving the EC2 pricing. Child of :class:`awspricingfull.AWSPrices` class.
    
    Attributes:
        INSTANCES_RESERVED_LINUX_URL (str): Undocumented AWS Pricing
            API URL - EC2 Linux Reserved, Current Generation.
        INSTANCES_RESERVED_RHEL_URL (str): Undocumented AWS Pricing
            API URL - EC2 RHEL Reserved, Current Generation.
        INSTANCES_RESERVED_SLES_URL (str): Undocumented AWS Pricing
            API URL - EC2 SLES Reserved, Current Generation.
        INSTANCES_RESERVED_WINDOWS_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows Reserved, Current Generation.
        INSTANCES_RESERVED_WINSQL_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL Reserved, Current Generation.
        INSTANCES_RESERVED_WINSQLWEB_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL Web Reserved, Current Generation.
        PG_INSTANCES_RESERVED_LINUX_URL (str): Undocumented AWS Pricing
            API URL - EC2 Linux Reserved, Previous Generation.
        PG_INSTANCES_RESERVED_RHEL_URL (str): Undocumented AWS Pricing
            API URL - EC2 RHEL Reserved, Previous Generation.
        PG_INSTANCES_RESERVED_SLES_URL (str): Undocumented AWS Pricing
            API URL - EC2 SLES Reserved, Previous Generation.
        PG_INSTANCES_RESERVED_WINDOWS_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows Reserved, Previous Generation.
        PG_INSTANCES_RESERVED_WINSQL_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL Reserved, Previous Generation.
        PG_INSTANCES_RESERVED_WINSQLWEB_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL Web Reserved, Previous Generation.
        INSTANCES_ONDEMAND_LINUX_URL (str): Undocumented AWS Pricing
            API URL - EC2 Linux On-Demand, Current Generation.
        INSTANCES_ONDEMAND_RHEL_URL (str): Undocumented AWS Pricing
            API URL - EC2 RHEL On-Demand, Current Generation.
        INSTANCES_ONDEMAND_SLES_URL (str): Undocumented AWS Pricing
            API URL - EC2 SLES On-Demand, Current Generation.
        INSTANCES_ONDEMAND_WINDOWS_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows On-Demand, Current Generation.
        INSTANCES_ONDEMAND_WINSQL_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL On-Demand, Current Generation.
        INSTANCES_ONDEMAND_WINSQLWEB_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL Web On-Demand, Current Generation.
        PG_INSTANCES_ONDEMAND_LINUX_URL (str): Undocumented AWS Pricing
            API URL - EC2 Linux On-Demand, Previous Generation.
        PG_INSTANCES_ONDEMAND_RHEL_URL (str): Undocumented AWS Pricing
            API URL - EC2 RHEL On-Demand, Previous Generation.
        PG_INSTANCES_ONDEMAND_SLES_URL (str): Undocumented AWS Pricing
            API URL - EC2 SLES On-Demand, Previous Generation.
        PG_INSTANCES_ONDEMAND_WINDOWS_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows On-Demand, Previous Generation.
        PG_INSTANCES_ONDEMAND_WINSQL_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL On-Demand, Previous Generation.
        PG_INSTANCES_ONDEMAND_WINSQLWEB_URL (str): Undocumented AWS Pricing
            API URL - EC2 Windows SQL Web On-Demand, Previous Generation.
        INSTANCES_ONDEMAND_OS_TYPE_BY_URL (dict of str: str): Mapping of 
            On-Dermand urls to OS types.
        INSTANCES_RESERVED_OS_TYPE_BY_URL (dict of str: str): Mapping of 
            Reserved urls to OS types.
    

            
    """
   
    INSTANCES_ON_DEMAND_LINUX_URL =("http://a0.awsstatic.com/pricing/1/ec2/"+
    "linux-od.min.js")
    INSTANCES_ON_DEMAND_RHEL_URL =("http://a0.awsstatic.com/pricing/1/ec2/"+
    "rhel-od.min.js")
    INSTANCES_ON_DEMAND_SLES_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "sles-od.min.js")
    INSTANCES_ON_DEMAND_WINDOWS_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "mswin-od.min.js")
    INSTANCES_ON_DEMAND_WINSQL_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "mswinSQL-od.min.js")
    INSTANCES_ON_DEMAND_WINSQLWEB_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "mswinSQLWeb-od.min.js")
    
    PG_INSTANCES_ON_DEMAND_LINUX_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/linux-od.min.js")
    PG_INSTANCES_ON_DEMAND_RHEL_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/rhel-od.min.js")
    PG_INSTANCES_ON_DEMAND_SLES_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/sles-od.min.js")
    PG_INSTANCES_ON_DEMAND_WINDOWS_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/mswin-od.min.js")
    PG_INSTANCES_ON_DEMAND_WINSQL_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/mswinSQL-od.min.js")
    PG_INSTANCES_ON_DEMAND_WINSQLWEB_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/mswinSQLWeb-od.min.js")
    
    INSTANCES_RESERVED_LINUX_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "ri-v2/linux-unix-shared.min.js")
    INSTANCES_RESERVED_RHEL_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "ri-v2/red-hat-enterprise-linux-shared.min.js")
    INSTANCES_RESERVED_SLES_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "ri-v2/suse-linux-shared.min.js")
    INSTANCES_RESERVED_WINDOWS_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "ri-v2/windows-shared.min.js")
    INSTANCES_RESERVED_WINSQL_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "ri-v2/windows-with-sql-server-standard-shared.min.js")
    INSTANCES_RESERVED_WINSQLWEB_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "ri-v2/windows-with-sql-server-web-shared.min.js")
    
    PG_INSTANCES_RESERVED_LINUX_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/ri-v2/linux-unix-shared.min.js")
    PG_INSTANCES_RESERVED_RHEL_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/ri-v2/red-hat-enterprise-linux-shared.min.js")
    PG_INSTANCES_RESERVED_SLES_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/ri-v2/suse-linux-shared.min.js")
    PG_INSTANCES_RESERVED_WINDOWS_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/ri-v2/windows-shared.min.js")
    PG_INSTANCES_RESERVED_WINSQL_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/ri-v2/windows-with-sql-server-standard-shared.min.js")
    PG_INSTANCES_RESERVED_WINSQLWEB_URL = ("http://a0.awsstatic.com/pricing/1/ec2/"+
    "previous-generation/ri-v2/windows-with-sql-server-web-shared.min.js")
    
    
    
    INSTANCES_ONDEMAND_OS_TYPE_BY_URL = {
        INSTANCES_ON_DEMAND_LINUX_URL : "linux",
        INSTANCES_ON_DEMAND_RHEL_URL : "rhel",
        INSTANCES_ON_DEMAND_SLES_URL : "sles",
        INSTANCES_ON_DEMAND_WINDOWS_URL : "mswin",
        INSTANCES_ON_DEMAND_WINSQL_URL : "mswinSQL",
        INSTANCES_ON_DEMAND_WINSQLWEB_URL : "mswinSQLWeb",
        PG_INSTANCES_ON_DEMAND_LINUX_URL : "linux",
        PG_INSTANCES_ON_DEMAND_RHEL_URL : "rhel",
        PG_INSTANCES_ON_DEMAND_SLES_URL : "sles",
        PG_INSTANCES_ON_DEMAND_WINDOWS_URL : "mswin",
        PG_INSTANCES_ON_DEMAND_WINSQL_URL : "mswinSQL",
        PG_INSTANCES_ON_DEMAND_WINSQLWEB_URL : "mswinSQLWeb"       
    }
    
    INSTANCES_RESERVED_OS_TYPE_BY_URL = {
    
        INSTANCES_RESERVED_LINUX_URL : "linux",
        INSTANCES_RESERVED_RHEL_URL : "rhel",
        INSTANCES_RESERVED_SLES_URL : "sles",
        INSTANCES_RESERVED_WINDOWS_URL :  "mswin",
        INSTANCES_RESERVED_WINSQL_URL : "mswinSQL",
        INSTANCES_RESERVED_WINSQLWEB_URL : "mswinSQLWeb",
        PG_INSTANCES_RESERVED_LINUX_URL : "linux",
        PG_INSTANCES_RESERVED_RHEL_URL : "rhel",
        PG_INSTANCES_RESERVED_SLES_URL : "sles",
        PG_INSTANCES_RESERVED_WINDOWS_URL :  "mswin",
        PG_INSTANCES_RESERVED_WINSQL_URL : "mswinSQL",
        PG_INSTANCES_RESERVED_WINSQLWEB_URL : "mswinSQLWeb"
    }
    
    
   
    
    def get_reserved_instances_prices(self):
        """
        Implementation of method for getting EC2 Reserved pricing. 
        
        Returns:
           result (dict of dict: dict): EC2 Reserved pricing in dictionary format.
                
        """
   
        currency = self.DEFAULT_CURRENCY
    
        urls = [
    
            self.INSTANCES_RESERVED_LINUX_URL,
            self.INSTANCES_RESERVED_RHEL_URL,
            self.INSTANCES_RESERVED_SLES_URL,
            self.INSTANCES_RESERVED_WINDOWS_URL,
            self.INSTANCES_RESERVED_WINSQL_URL,
            self.INSTANCES_RESERVED_WINSQLWEB_URL,
            self.PG_INSTANCES_RESERVED_LINUX_URL,
            self.PG_INSTANCES_RESERVED_RHEL_URL,
            self.PG_INSTANCES_RESERVED_SLES_URL,
            self.PG_INSTANCES_RESERVED_WINDOWS_URL,
            self.PG_INSTANCES_RESERVED_WINSQL_URL,
            self.PG_INSTANCES_RESERVED_WINSQLWEB_URL,
        ]
    
        result_regions = []
        result_regions_index = {}
        result = {
            "config" : {
                "currency" : currency,
            },
            "regions" : result_regions
        }
        
        for u in urls:
            os_type = self.INSTANCES_RESERVED_OS_TYPE_BY_URL[u]
            
            data = self.load_data(u)
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
                        region_name = r["region"]
                        if region_name in result_regions_index:
                            instance_types = result_regions_index[region_name]["instanceTypes"]
                        else:
                            instance_types = []
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })
                            result_regions_index[region_name] = result_regions[-1]
    
                        if "instanceTypes" in r:
                            for it in r["instanceTypes"]:
                                instance_type = it["type"]
                                prices = {
                                                      "1" : {
                                                             "noUpfront" : {
                                                                            "hourly" : None,
                                                                            "upfront" : None
                                                                            },
                                                             "partialUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               },
                                                             "allUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               }
                                                             },
                                                      "3" : {
                                                             "partialUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               },
                                                             "allUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               }
                                                             }
                                                      }
                                instance_types.append({
                                    "type" : instance_type,
                                    "os" : os_type,
                                    "prices" : prices
                                })
                                          
                                if "terms" in it:
                                    for s in it["terms"]:
                                        term=s["term"]
                                          
                                        for po_data in s["purchaseOptions"]:
                                            po=po_data["purchaseOption"]
                                            
                                            for price_data in po_data["valueColumns"]:
                                                price = None
                                                try:
                                                    price = float(re.sub("[^0-9\.]", "", 
                                                                 price_data["prices"][currency]))
                                                except ValueError:
                                                    price = None
                                                        
                                                if term=="yrTerm1":
                                                    if price_data["name"] == "upfront":
                                                        prices["1"][po]["upfront"] = price
                                                    elif price_data["name"] == "monthlyStar":
                                                        prices["1"][po]["hourly"] = price/730
                                                elif term=="yrTerm3":
                                                    if price_data["name"] == "upfront":
                                                        prices["3"][po]["upfront"] = price
                                                    elif price_data["name"] == "monthlyStar":
                                                        prices["3"][po]["hourly"] = price/730
    
        return result
    
    def get_ondemand_instances_prices(self):
        """
        Implementation of method for getting EC2 On-Demand pricing. 
        
        Returns:
           result (dict of dict: dict): EC2 On-Demand pricing in dictionary format.
                
        """
    
    
        currency = self.DEFAULT_CURRENCY
    
        urls = [
            self.INSTANCES_ON_DEMAND_LINUX_URL,
            self.INSTANCES_ON_DEMAND_RHEL_URL,
            self.INSTANCES_ON_DEMAND_SLES_URL,
            self.INSTANCES_ON_DEMAND_WINDOWS_URL,
            self.INSTANCES_ON_DEMAND_WINSQL_URL,
            self.INSTANCES_ON_DEMAND_WINSQLWEB_URL,
            self.PG_INSTANCES_ON_DEMAND_LINUX_URL,
            self.PG_INSTANCES_ON_DEMAND_RHEL_URL,
            self.PG_INSTANCES_ON_DEMAND_SLES_URL,
            self.PG_INSTANCES_ON_DEMAND_WINDOWS_URL,
            self.PG_INSTANCES_ON_DEMAND_WINSQL_URL,
            self.PG_INSTANCES_ON_DEMAND_WINSQLWEB_URL
        ]
    
        result_regions = []
        result = {
            "config" : {
                "currency" : currency,
                "unit" : "perhr"
            },
            "regions" : result_regions
        }
    
        for u in urls:
    
    
            data = self.load_data(u)
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
    
                        region_name = r["region"]
                        instance_types = []
                        if "instanceTypes" in r:
                            for it in r["instanceTypes"]:
                                if "sizes" in it:
                                    for s in it["sizes"]:
                                        instance_type = s["size"]
    
                                        for price_data in s["valueColumns"]:
                                            price = None
                                            try:
                                                price =float(re.sub("[^0-9\.]", "",
                                                                    price_data["prices"][currency]))
                                            except:
                                                price = None
                                            _type = instance_type
                                            instance_types.append({
                                                "type" : _type,
                                                "os" : price_data["name"],
                                                "price" : price
                                            })
    
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })
    
        return result
    
    def print_table(self,u):
        """
        Method printing the EC2 pricing data to the console
            in the Pretty Table format (requires Pretty Table 
            import).
        
        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
        
        Returns:
           Prints EC2 pricing in the Pretty Table format.
                
        """
                       
        try:
            from prettytable import PrettyTable
        except ImportError:
            print ("ERROR: Please install 'prettytable' using pip:"+
                    "pip install prettytable")
    
        data = None
        
        if u not in ["ondemand","reserved"]:
            print("Function requires 1 parameter. Possible values:"
                  "\"ondemand\" or \"reserved\".")
        else:
                
            if u == "ondemand":
                data = self.get_ondemand_instances_prices()
                x = PrettyTable()
                try:
                    x.set_field_names(["region", "type", "os", "price"])
                except AttributeError:
                    x.field_names = ["region", "type", "os", "price"]
    
                try:
                    x.aligns[-1] = "l"
                except AttributeError:
                    x.align["price"] = "l"
    
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        x.add_row([region_name, it["type"], it["os"], self.none_as_string(it["price"])])
                  
            elif u == "reserved":
                data = self.get_reserved_instances_prices()
                x = PrettyTable()
                try:
                    x.set_field_names(["region", "type", "os", "term", "payment_type", "price", "upfront"])
                except AttributeError:
                    x.field_names = ["region", "type", "os", "term", "payment_type", "price", "upfront"]
    
                try:
                    x.aligns[-1] = "l"
                    x.aligns[-2] = "l"
                except AttributeError:
                    x.align["price"] = "l"
                    x.align["upfront"] = "l"
    
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        for term in it["prices"]:
                            for po in it["prices"][term]:
                                x.add_row ([region_name,
                                            it["type"],
                                            it["os"],
                                            term, 
                                            po,
                                            self.none_as_string(it["prices"][term][po]["hourly"]),
                                            self.none_as_string(it["prices"][term][po]["upfront"])])                    
    
            print x

    
    def save_csv(self,u,path=os.getcwd()+"\\",name=None):
        """
        Method saving the EC2 pricing data in CSV format to the
            cpecified location.

        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
            path (str): System path for saving the data file. Current
                directory is the the defauilt value.
            name (str): The desired name of the file. The default
                values are "EC2_reserved_pricing.csv" for Reserved
                and "EC2_ondemand_pricing.csv" for On-Demand.
        
        Returns:
           Prints EC2 pricing in the CSV format (console).
                
        """
        if u not in ["ondemand","reserved"]:
            print("Function requires 1 parameter. Possible values:"
                  "\"ondemand\" or \"reserved\".")
                    
        elif u == "ondemand":
            if name is None:
                name="EC2_ondemand_pricing.csv"
            data = self.get_ondemand_instances_prices()
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,os,price"
            writer.writerow(["region","type","os","price"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow([region_name,it["type"],it["os"],self.none_as_string(it["price"])])
                    print "%s,%s,%s,%s" % (region_name, 
                                           it["type"], 
                                           it["os"], 
                                           self.none_as_string(it["price"]))
        elif u == "reserved":
            if name is None:
                name="EC2_reserved_pricing.csv"
            data = self.get_reserved_instances_prices()
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,os,term,payment_type,price,upfront"
            writer.writerow(["region","type","os","term","payment_type","price","upfront"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        for po in it["prices"][term]:
                            print "%s,%s,%s,%s,%s,%s,%s" % (region_name, 
                                                            it["type"], 
                                                            it["os"], 
                                                            term, 
                                                            po, 
                                                            self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                            self.none_as_string(it["prices"][term][po]["upfront"]))
                            writer.writerow([region_name, 
                                             it["type"], 
                                             it["os"], 
                                             term, 
                                             po, 
                                             self.none_as_string(it["prices"][term][po]["hourly"]), 
                                             self.none_as_string(it["prices"][term][po]["upfront"])])

class ELCPrices(AWSPrices):
    """
    Class for retrieving the ElastiCache pricing. Child of :class:`awspricingfull.AWSPrices` class.
    
    Attributes:
        INSTANCES_ON_DEMAND_URL (str): Undocumented AWS Pricing API URL -
            On-Demand ELC Current Generation.
        PG_INSTANCES_ON_DEMAND_URL (str): Undocumented AWS Pricing API
            URL - On-Demand ELC Previous Generation.
        INSTANCES_RESERVED_LIGHT_UTILIZATION_URL (str): Undocumented AWS
            Pricing - Light Reserved ELC Current Generation.
        INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL (str): Undocumented AWS
            Pricing- Medium Reserved ELC Current Generation.
        INSTANCES_RESERVED_HEAVY_UTILIZATION_URL (str): Undocumented AWS
            Pricing- Heavy Reserved ELC Current Generation.
        PG_INSTANCES_RESERVED_LIGHT_UTILIZATION_URL (str): Undocumented AWS
            Pricing- Light Reserved ELC Previous Generation.
        PG_INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL (str): Undocumented AWS
            Pricing- Medium Reserved ELC Previous Generation.
        PG_INSTANCES_RESERVED_HEAVY_UTILIZATION_URL (str): Undocumented AWS
            Pricing- Heavy Reserved ELC Previous Generation.
        INSTANCES_RESERVED_UTILIZATION_TYPE_BY_URL (dict of str: str): Mapping of 
            Reserved urls to Reservation types.
        INSTANCE_TYPE_MAPPING (dict of str: str): Mapping of internal AWS ELC
            Type names to the conventional analogs.
            
    """

       
    INSTANCES_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "pricing-standard-deployments-elasticache.min.js")
    PG_INSTANCES_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "previous-generation/pricing-standard-deployments-elasticache.min.js")
    INSTANCES_RESERVED_LIGHT_UTILIZATION_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "pricing-elasticache-light-standard-deployments-elasticache.min.js")
    INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "pricing-elasticache-medium-standard-deployments.min.js")
    INSTANCES_RESERVED_HEAVY_UTILIZATION_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "pricing-elasticache-heavy-standard-deployments.min.js")
    PG_INSTANCES_RESERVED_LIGHT_UTILIZATION_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "previous-generation/pricing-elasticache-light-standard-deployments.min.js")
    PG_INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "previous-generation/pricing-elasticache-medium-standard-deployments.min.js")
    PG_INSTANCES_RESERVED_HEAVY_UTILIZATION_URL=("http://a0.awsstatic.com/pricing/1/elasticache/"+
    "previous-generation/pricing-elasticache-heavy-standard-deployments.min.js")
    
    
    INSTANCES_RESERVED_UTILIZATION_TYPE_BY_URL = {
        INSTANCES_RESERVED_LIGHT_UTILIZATION_URL : "light",
        INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL : "medium",
        INSTANCES_RESERVED_HEAVY_UTILIZATION_URL : "heavy",
        PG_INSTANCES_RESERVED_LIGHT_UTILIZATION_URL : "light",
        PG_INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL : "medium",
        PG_INSTANCES_RESERVED_HEAVY_UTILIZATION_URL : "heavy"
    }
    
    INSTANCE_TYPE_MAPPING = {
        "microInstClass.microInst": "cache.t1.micro",
        "sCacheNode.sm" : "cache.m1.small",
        "sCacheNode.medInst" : "cache.m1.medium",
        "sCacheNode.lg" : "cache.m1.large",
        "sCacheNode.xl" : "cache.m1.xlarge",
        "hiMemCacheClass.xl" : "cache.m2.xlarge",
        "hiMemCacheClass.xxl" : "cache.m2.2xlarge",
        "hiMemCacheClass.xxxxl" : "cache.m2.4xlarge",
        "hiCPUDBInstClass.hiCPUxlDBInst" : "cache.c1.xlarge",
        "enInstClass2.xl" : "cache.m3.xlarge",
        "enInstClass2.xxl" : "cache.m3.2xlarge",
        
        #Reserved
        "mic" : "cache.t1.micro",
        "sm" : "cache.m1.small",
        "medInst" : "cache.m1.medium",
        "lg" : "cache.m1.large",
        "xl" : "cache.m1.xlarge",
        "xlHiMem" : "cache.m2.xlarge",
        "xxlHiMem" : "cache.m2.2xlarge",
        "xxxxlHiMem" : "cache.m2.4xlarge",
        "xlHiCPU" : "cache.c1.xlarge",
        "xlEn" : "cache.m3.xlarge",
        "xxlEn" : "cache.m3.2xlarge",
    }
    
    
    def get_reserved_instances_prices(self):
        """
        Implementation of method for getting ELC Reserved pricing. 
        
        Returns:
           result (dict of dict: dict): ELC Reserved pricing in dictionary format.
                
        """

    
        currency = self.DEFAULT_CURRENCY
    
        urls = [
            self.INSTANCES_RESERVED_LIGHT_UTILIZATION_URL,
            self.INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL,
            self.INSTANCES_RESERVED_HEAVY_UTILIZATION_URL,
            self.PG_INSTANCES_RESERVED_LIGHT_UTILIZATION_URL,
            self.PG_INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL,
            self.PG_INSTANCES_RESERVED_HEAVY_UTILIZATION_URL
        ]
    
        result_regions = []
        result_regions_index = {}
        result = {
            "config" : {
                "currency" : currency,
            },
            "regions" : result_regions
        }
    
        for u in urls:
            utilization_type = self.INSTANCES_RESERVED_UTILIZATION_TYPE_BY_URL[u]
            data = self.load_data(u)
    
            if ("config" in data and data["config"] and "regions"
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
    
                        region_name = self.JSON_NAME_TO_REGIONS_API[r["region"]]
                        if region_name in result_regions_index:
                            instance_types = result_regions_index[region_name]["instanceTypes"]
                        else:
                            instance_types = []
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })
                            result_regions_index[region_name] = result_regions[-1]
                        
                        if "instanceTypes" in r:
                            for it in r["instanceTypes"]:
                                if "tiers" in it:
                                    for s in it["tiers"]:
                                        if (u==self.INSTANCES_RESERVED_LIGHT_UTILIZATION_URL or 
                                            u==self.INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL):
                                            _type = self.INSTANCE_TYPE_MAPPING[s["size"]]
                                        else:                                          
                                            _type = s["size"]
                                            

                                        prices = {
                                            "1" : {
                                                "hourly" : None,
                                                "upfront" : None
                                            },
                                            "3" : {
                                                "hourly" : None,
                                                "upfront" : None
                                            }
                                        }
    
                                        instance_types.append({
                                            "type" : _type,
                                            "utilization" : utilization_type,
                                            "prices" : prices
                                        })
        
                                        for price_data in s["valueColumns"]:
                                            price = None
                                            try:
                                                price = float(re.sub("[^0-9\\.]", "", 
                                                                     price_data["prices"][currency]))
                                            except ValueError:
                                                price = None
        
                                            if price_data["name"] == "yrTerm1":
                                                prices["1"]["upfront"] = price
                                            elif price_data["name"] == "yearTerm1Hourly":
                                                prices["1"]["hourly"] = price
                                            elif price_data["name"] == "yrTerm3":
                                                prices["3"]["upfront"] = price
                                            elif price_data["name"] == "yearTerm3Hourly":
                                                prices["3"]["hourly"] = price            
    
        return result
    
    def get_ondemand_instances_prices(self):
        """
        Implementation of method for getting ELC On-Denand pricing. 
        
        Returns:
           result (dict of dict: dict): ELC On-Denand pricing in dictionary format.
                
        """
        
        urls = [
            self.INSTANCES_ON_DEMAND_URL,
            self.PG_INSTANCES_ON_DEMAND_URL
        ]
       
    
        currency = self.DEFAULT_CURRENCY
    
        result_regions = []
        result = {
            "config" : {
                "currency" : currency,
                "unit" : "perhr"
            },
            "regions" : result_regions
        }
        
        for u in urls:
    
            data = self.load_data(u)
            
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
                        region_name = self.JSON_NAME_TO_REGIONS_API[r["region"]]
                        instance_types = []
                        if "types" in r:
                            for it in r["types"]:
                                if "tiers" in it:
                                    for s in it["tiers"]:
                                        _type = s["name"]
                                        
                                        price = None
                                        try:
                                            price = float(re.sub("[^0-9\\.]", 
                                                                 "", s["prices"][currency]))
                                        except ValueError:
                                            price = None
        
                                        instance_types.append({
                                            "type" : _type,
                                            "price" : price
                                        })
        
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })       
        return result

    

    def print_table(self,u):
        """
        Method printing the ELC pricing data to the console
            in the Pretty Table format (requires Pretty Table 
            import).
        
        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
        
        Returns:
           Prints ELC pricing in the Pretty Table format.
                
        """
        try:
            from prettytable import PrettyTable
        except ImportError:
            print ("ERROR: Please install 'prettytable' using pip: "+
                   "pip install prettytable")
       

        data = None
        if u not in ["ondemand","reserved"]:
            print("Function requires 1 parameter. Possible values:"
                  "\"ondemand\" or \"reserved\".")
        else:
                
            if u == "ondemand":
                x = PrettyTable()
                data = self.get_ondemand_instances_prices()
                try:            
                    x.set_field_names(["region", "type", "price"])
                except AttributeError:
                    x.field_names = ["region", "type", "price"]
                
                try:
                    x.aligns[-1] = "l"
                except AttributeError:
                    x.align["price"] = "l"
                
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        x.add_row([region_name, it["type"], 
                                   self.none_as_string(it["price"])])
                   
            elif u == "reserved":
                x = PrettyTable()
                data = self.get_reserved_instances_prices()
                try:
                    x.set_field_names(["region", "type", "utilization", "term", "price", "upfront"])
                except AttributeError:
                    x.field_names = ["region", "type", "utilization", "term", "price", "upfront"]
    
                try:
                    x.aligns[-1] = "l"
                    x.aligns[-2] = "l"
                except AttributeError:
                    x.align["price"] = "l"
                    x.align["upfront"] = "l"
                
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        for term in it["prices"]:
                            x.add_row([region_name, 
                                       it["type"], 
                                       it["utilization"], 
                                       term, 
                                       self.none_as_string(it["prices"][term]["hourly"]), 
                                       self.none_as_string(it["prices"][term]["upfront"])])
    
            print x
    
    
    def save_csv(self,u,path=os.getcwd()+"\\",name=None):
        """
        Method saving the ELC pricing data in CSV format to the
            cpecified location.

        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
            path (str): System path for saving the data file. Current
                directory is the the defauilt value.
            name (str): The desired name of the file. The default
                values are "ELC_reserved_pricing.csv" for Reserved
                and "ELC_ondemand_pricing.csv" for On-Demand.
        
        Returns:
           Prints ELC pricing in the CSV format (console).
                
        """
        if u not in ["ondemand","reserved"]:
            print("Function requires Reservation parameter at the first"+
                  "position. Possible values:"+
                  "\"ondemand\" or \"reserved\".")
            
        elif u == "ondemand":
            if name is None:
                name="ELC_ondemand_pricing.csv"
            data = self.get_ondemand_instances_prices()         
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,price"
            writer.writerow(["region","type","price"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow([region_name,it["type"],
                                     self.none_as_string(it["price"])])
                    print "%s,%s,%s" % (region_name, it["type"], 
                                        self.none_as_string(it["price"]))
        elif u == "reserved":
            if name is None:
                name="ELC_reserved_pricing.csv"
            data = self.get_reserved_instances_prices()
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,utilization,term,price,upfront"
            writer.writerow(["region","type","utilization","term","price","upfront"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        print "%s,%s,%s,%s,%s,%s" % (region_name, 
                                                     it["type"], 
                                                     it["utilization"], 
                                                     term, 
                                                     self.none_as_string(it["prices"][term]["hourly"]), 
                                                     self.none_as_string(it["prices"][term]["upfront"]))
                        writer.writerow([region_name, 
                                         it["type"], 
                                         it["utilization"], 
                                         term, 
                                         self.none_as_string(it["prices"][term]["hourly"]), 
                                         self.none_as_string(it["prices"][term]["upfront"])])
    
    
class RDSPrices(AWSPrices):
    """
    Class for retrieving the RDS pricing. Child of :class:`awspricingfull.AWSPrices` class.
    
    Attributes:
        RDS_MYSQL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MySQL GPL, On-Demand, Current Generation.   
        RDS_MYSQL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MySQL GPL, On-Demand, Current Generation.
        RDS_ORACLE_LICENSED_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle Licensed, On-Demand, Current Generation.
        RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle Licensed, On-Demand, Current Generation.
        RDS_ORACLE_BYOL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle BYOL, On-Demand, Current Generation.
        RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle BYOL, On-Demand, Current Generation.   
        RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server Express Licensed, On-Demand, Current Generation.
        RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server WEB Licensed, On-Demand, Current Generation.
        RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server SE Licensed, On-Demand, Current Generation.
        RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MS SQL Server SE Licensed, On-Demand, Current Generation.
        RDS_MSSQL_BYOL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server BYOL, On-Demand, Current Generation.
        RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MS SQL Server BYOL, On-Demand, Current Generation.
        RDS_POSTGRESQL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ Postgres On-Demand, Current Generation.
        RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Postgres, On-Demand, Current Generation.
        PG_RDS_MYSQL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MySQL GPL, On-Demand, Previous Generation.   
        PG_RDS_MYSQL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MySQL GPL, On-Demand, Previous Generation.
        PG_RDS_ORACLE_LICENSED_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle Licensed, On-Demand, Previous Generation.
        PG_RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle Licensed, On-Demand, Previous Generation.
        PG_RDS_ORACLE_BYOL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle BYOL, On-Demand, Previous Generation.
        PG_RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle BYOL, On-Demand, Previous Generation.   
        PG_RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server Express Licensed, On-Demand, Previous Generation.
        PG_RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server WEB Licensed, On-Demand, Previous Generation.
        PG_RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server SE Licensed, On-Demand, Previous Generation.
        PG_RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MS SQL Server SE Licensed, On-Demand, Previous Generation.
        PG_RDS_MSSQL_BYOL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server BYOL, On-Demand, Previous Generation.
        PG_RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MS SQL Server BYOL, On-Demand, Previous Generation.
        PG_RDS_POSTGRESQL_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Single AZ Postgres On-Demand, Previous Generation.
        PG_RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Postgres, On-Demand, Previous Generation.
        RDS_MYSQL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ MySQL GPL, Reserved, Current Generation.
        RDS_MYSQL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MySQL GPL, Reserved, Current Generation.
        RDS_ORACLE_LICENSED_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle Licensed, Reserved, Current Generation.
        RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle Licensed, Reserved, Current Generation.
        RDS_ORACLE_BYOL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle BYOL, Reserved, Current Generation.
        RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle BYOL, Reserved, Current Generation.
        RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server Express Licensed, Reserved Light, Current Generation.
        RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server Express Licensed, Reserved Medium, Current Generation.
        RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server Express Licensed, Reserved Heavy, Current Generation.
        RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server WEB Licensed, Reserved Light, Current Generation.
        RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server WEB Licensed, Reserved Medium, Current Generation.
        RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server WEB Licensed, Reserved Heavy, Current Generation.
        RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server SE Licensed, Reserved Light, Current Generation.
        RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server SE Licensed, Reserved Medium, Current Generation.
        RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server SE Licensed, Reserved Heavy, Current Generation.
        RDS_MSSQL_BYOL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server BYOL, Reserved, Current Generation.
        RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MS SQL Server BYOL, Reserved, Current Generation.
        RDS_POSTGRESQL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ Postgres, Reserved, Current Generation.
        RDS_POSTGRESQL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Postgres, Reserved, Current Generation.
        PG_RDS_MYSQL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ MySQL GPL, Reserved, Previous Generation.
        PG_RDS_MYSQL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MySQL GPL, Reserved, Previous Generation.
        PG_RDS_ORACLE_LICENSED_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle Licensed, Reserved, Previous Generation.
        PG_RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle Licensed, Reserved, Previous Generation.
        PG_RDS_ORACLE_BYOL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ Oracle BYOL, Reserved, Previous Generation.
        PG_RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Oracle BYOL, Reserved, Previous Generation.
        PG_RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server Express Licensed, Reserved Light, Previous Generation.
        PG_RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server Express Licensed, Reserved Medium, Previous Generation.
        PG_RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server Express Licensed, Reserved Heavy, Previous Generation.
        PG_RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server WEB Licensed, Reserved Light, Previous Generation.
        PG_RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server WEB Licensed, Reserved Medium, Previous Generation.
        PG_RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server WEB Licensed, Reserved Heavy, Previous Generation.
        PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server SE Licensed, Reserved Light, Previous Generation.
        PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server SE Licensed, Reserved Medium, Previous Generation.
        PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL (str): Undocumented AWS
            API URL - RDS MS SQL Server SE Licensed, Reserved Heavy, Previous Generation.
        PG_RDS_MSSQL_BYOL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ MS SQL Server BYOL, Reserved, Previous Generation.
        PG_RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ MS SQL Server BYOL, Reserved, Previous Generation.
        PG_RDS_POSTGRESQL_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Single AZ Postgres, Reserved, Previous Generation.
        PG_RDS_POSTGRESQL_MULTIAZ_RESERVED_URL (str): Undocumented AWS
            API URL - RDS Multi AZ Postgres, Reserved, Previous Generation.
        RDS_ENGINE_TYPES (list of str): List of RDS engines.
        RDS_MULTIAZ_TYPES (list of str): List of RDS Multi-AZ options.
        RDS_MULTIAZ_MAPPING (dict of str: str): Mapping of internal AWS RDS
            Family names to the cvonventional Multi-AZ tag.    
        RDS_ONDEMAND_TYPE_BY_URL (dict of str: list of str): Mapping of AWS RDS URLs
            (On-Demand, Single AZ) to corresponding engine and license type.
        RDS_ONDEMAND_MULTIAZ_TYPE_BY_URL (dict of str: list of str): Mapping of AWS RDS URLs
            (On-Demand, Multi AZ) to corresponding engine and license type.
        RDS_RESERVED_TYPE_BY_URL_NEW (dict of str: list of str): Mapping of AWS RDS URLs
            (Reserved, Single AZ, New Pricing Scheme) to corresponding engine and license type.
        RDS_RESERVED_MULTIAZ_TYPE_BY_URL_NEW (dict of str: list of str): Mapping of AWS RDS URLs
            (Reserved, Multi AZ, New Pricing Scheme) to corresponding engine and license type.
        RDS_RESERVED_TYPE_BY_URL_OLD (dict of str: list of str): Mapping of AWS RDS URLs
            (Reserved, Old Pricing Scheme) to corresponding engine and license type.            
        INSTANCE_TYPE_MAPPING (dict of str: str): Mapping of internal AWS RDS
            Type names to the cvonventional analogs.
                

            
    """
    

    
    RDS_ENGINE_TYPES = [
        "mysql",
        "postgres",
        "oracle-se1",
        "oracle",
        "sqlserver-ex",
        "sqlserver-web",
        "sqlserver-se",
        "sqlserver"
    ]
    

    
    RDS_MYSQL_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/mysql/pricing-standard-deployments.min.js")
    RDS_MYSQL_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/mysql/pricing-multiAZ-deployments.min.js")     
    RDS_ORACLE_LICENSED_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/pricing-li-standard-deployments.min.js")
    RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/pricing-li-multiAZ-deployments.min.js")
    RDS_ORACLE_BYOL_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/pricing-byol-standard-deployments.min.js")
    RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/pricing-byol-multiAZ-deployments.min.js")    
    RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-ex-ondemand.min.js")
    RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-web-ondemand.min.js")
    RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-se-ondemand.min.js")
    RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-se-ondemand-maz.min.js")
    RDS_MSSQL_BYOL_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-byol-ondemand.min.js")
    RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-byol-ondemand-maz.min.js")    
    RDS_POSTGRESQL_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/postgresql/pricing-standard-deployments.min.js")
    RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/postgresql/pricing-multiAZ-deployments.min.js")
  
    PG_RDS_MYSQL_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/mysql/previous-generation/pricing-standard-deployments.min.js")
    PG_RDS_MYSQL_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/mysql/previous-generation/pricing-multiAZ-deployments.min.js")     
    PG_RDS_ORACLE_LICENSED_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/previous-generation/pricing-li-standard-deployments.min.js")
    PG_RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/previous-generation/pricing-li-multiAZ-deployments.min.js")
    PG_RDS_ORACLE_BYOL_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/previous-generation/pricing-byol-standard-deployments.min.js")
    PG_RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/oracle/previous-generation/pricing-byol-multiAZ-deployments.min.js")    
    PG_RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-ex-ondemand.min.js")
    PG_RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-web-ondemand.min.js")
    PG_RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-se-ondemand.min.js")
    PG_RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-se-ondemand-maz.min.js")
    PG_RDS_MSSQL_BYOL_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-byol-ondemand.min.js")
    PG_RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-byol-ondemand-maz.min.js")    
    PG_RDS_POSTGRESQL_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/postgresql/previous-generation/pricing-standard-deployments.min.js")
    PG_RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/postgresql/previous-generation/pricing-multiAZ-deployments.min.js")

    
    RDS_MYSQL_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/mysql-standard.min.js")
    RDS_MYSQL_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/mysql-multiAZ.min.js")        
    RDS_ORACLE_LICENSED_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/oracle-se1-license-included-standard.min.js")
    RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/oracle-se1-license-included-multiAZ.min.js")    
    RDS_ORACLE_BYOL_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/oracle-se-byol-standard.min.js")
    RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/oracle-se-byol-multiAZ.min.js")
    RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-ex-light-ri.min.js")
    RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-ex-medium-ri.min.js")
    RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-ex-heavy-ri.min.js")
    RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-web-light-ri.min.js")
    RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-web-medium-ri.min.js")
    RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-web-heavy-ri.min.js")
    RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-se-light-ri.min.js")
    RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-se-medium-ri.min.js")
    RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/sqlserver-li-se-heavy-ri.min.js")        
    RDS_MSSQL_BYOL_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/sql-server-se-byol-standard.min.js")
    RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/sql-server-se-byol-multiAZ.min.js")    
    RDS_POSTGRESQL_RESERVED_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/postgresql-standard.min.js")
    RDS_POSTGRESQL_MULTIAZ_RESERVED_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/reserved-instances/postgresql-multiAZ.min.js")            
    
    PG_RDS_MYSQL_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/mysql-standard.min.js")
    PG_RDS_MYSQL_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/mysql-multiAZ.min.js")        
    PG_RDS_ORACLE_LICENSED_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/oracle-se1-license-included-standard.min.js")
    PG_RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/oracle-se1-license-included-multiAZ.min.js")    
    PG_RDS_ORACLE_BYOL_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/oracle-se-byol-standard.min.js")
    PG_RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/oracle-se-byol-multiAZ.min.js")
    PG_RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-ex-light-ri.min.js")
    PG_RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-ex-medium-ri.min.js")
    PG_RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-ex-heavy-ri.min.js")
    PG_RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-web-light-ri.min.js")
    PG_RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-web-medium-ri.min.js")
    PG_RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-web-heavy-ri.min.js")
    PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-se-light-ri.min.js")
    PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-se-medium-ri.min.js")
    PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/sqlserver/previous-generation/sqlserver-li-se-heavy-ri.min.js")        
    PG_RDS_MSSQL_BYOL_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/sql-server-se-byol-standard.min.js")
    PG_RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL = ("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/sql-server-se-byol-multiAZ.min.js")    
    PG_RDS_POSTGRESQL_RESERVED_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/postgresql-standard.min.js")
    PG_RDS_POSTGRESQL_MULTIAZ_RESERVED_URL=("http://a0.awsstatic.com/pricing/1/"+
        "rds/previous-generation/reserved-instances/postgresql-multiAZ.min.js")     

    
    RDS_MULTIAZ_TYPES = [
        "single",
        "multi-az"
        ]
    
    RDS_MULTIAZ_MAPPING = {
        "Micro and Small Instances - Current Generation - Single-AZ" : "single",    
        "Standard Instances - Current Generation - Single-AZ" : "single",
        "Micro and Small Instances - Current Generation - Multi-AZ" : "multi-az",
        "Standard Instances - Current Generation - Multi-AZ" : "multi-az",
        "Memory Optimized Instances - Current Generation - Single-AZ" : "single",
        "Memory Optimized Instances - Current Generation - Multi-AZ" : "multi-az",
        "Micro Instances - Previous Generation - Single-AZ" : "single",
        "Micro Instances - Previous Generation - Multi-AZ" : "multi-az",
        "Standard Instances - Previous Generation - Single-AZ" : "single",
        "Standard Instances - Previous Generation - Multi-AZ" : "multi-az",
        "Micro and Small Instances - Previous Generation - Single-AZ" : "single",    
        "Standard Instances - Previous Generation - Single-AZ" : "single",
        "Micro and Small Instances - Previous Generation - Multi-AZ" : "multi-az",
        "Standard Instances - Previous Generation - Multi-AZ" : "multi-az",
        "Memory Optimized Instances - Previous Generation - Single-AZ" : "single",
        "Memory Optimized Instances - Previous Generation - Multi-AZ" : "multi-az",
        "Micro Instances - Previous Generation - Single-AZ" : "single",
        "Micro Instances - Previous Generation - Multi-AZ" : "multi-az",
        "Standard Instances - Previous Generation - Single-AZ" : "single",
        "Standard Instances - Previous Generation - Multi-AZ" : "multi-az"
    
    }
    
    RDS_ONDEMAND_TYPE_BY_URL = {
        RDS_MYSQL_ON_DEMAND_URL : ["gpl","mysql"],        
        RDS_ORACLE_LICENSED_ON_DEMAND_URL : ["included","oracle-se1"],
        RDS_ORACLE_BYOL_ON_DEMAND_URL : ["byol","oracle"],
        RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL : ["included","sqlserver-ex"],
        RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL : ["included","sqlserver-web"],
        RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL : ["included","sqlserver-se"],
        RDS_MSSQL_BYOL_ON_DEMAND_URL : ["byol","sqlserver"],
        RDS_POSTGRESQL_ON_DEMAND_URL : ["postgresql","postgres"],
        PG_RDS_MYSQL_ON_DEMAND_URL : ["gpl","mysql"],        
        PG_RDS_ORACLE_LICENSED_ON_DEMAND_URL : ["included","oracle-se1"],
        PG_RDS_ORACLE_BYOL_ON_DEMAND_URL : ["byol","oracle"],
        PG_RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL : ["included","sqlserver-ex"],
        PG_RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL : ["included","sqlserver-web"],
        PG_RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL : ["included","sqlserver-se"],
        PG_RDS_MSSQL_BYOL_ON_DEMAND_URL : ["byol","sqlserver"],
        PG_RDS_POSTGRESQL_ON_DEMAND_URL : ["postgresql","postgres"]
    }

    
    RDS_ONDEMAND_MULTIAZ_TYPE_BY_URL = {
        RDS_MYSQL_MULTIAZ_ON_DEMAND_URL : ["gpl","mysql"],
        RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL: ["included","oracle-se1"],
        RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL : ["byol","oracle"],
        RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL : ["included","sqlserver-se"],
        RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL : ["byol","sqlserver"],
        RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL : ["postgresql","postgres"],
        PG_RDS_MYSQL_MULTIAZ_ON_DEMAND_URL : ["gpl","mysql"],
        PG_RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL: ["included","oracle-se1"],
        PG_RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL : ["byol","oracle"],
        PG_RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL : ["included","sqlserver-se"],
        PG_RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL : ["byol","sqlserver"],
        PG_RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL : ["postgresql","postgres"]
    }
    
    RDS_RESERVED_TYPE_BY_URL_NEW = {
        RDS_MYSQL_RESERVED_URL : ["gpl","mysql"],
        RDS_ORACLE_LICENSED_RESERVED_URL : ["included","oracle-se1"],
        RDS_ORACLE_BYOL_RESERVED_URL : ["byol","oracle"],
        RDS_MSSQL_BYOL_RESERVED_URL : ["byol","sqlserver"],
        RDS_POSTGRESQL_RESERVED_URL : ["postgresql","postgres"],
        PG_RDS_MYSQL_RESERVED_URL : ["gpl","mysql"],
        PG_RDS_ORACLE_LICENSED_RESERVED_URL : ["included","oracle-se1"],
        PG_RDS_ORACLE_BYOL_RESERVED_URL : ["byol","oracle"],
        PG_RDS_MSSQL_BYOL_RESERVED_URL : ["byol","sqlserver"],
        PG_RDS_POSTGRESQL_RESERVED_URL : ["postgresql","postgres"]
    }
    
    RDS_RESERVED_MULTIAZ_TYPE_BY_URL_NEW = {
        RDS_MYSQL_MULTIAZ_RESERVED_URL : ["gpl","mysql"],
        RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL : ["included","oracle-se1"],
        RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL : ["byol","oracle"],
        RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL : ["byol","sqlserver"],
        RDS_POSTGRESQL_MULTIAZ_RESERVED_URL : ["postgresql","postgres"],
        PG_RDS_MYSQL_MULTIAZ_RESERVED_URL : ["gpl","mysql"],
        PG_RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL : ["included","oracle-se1"],
        PG_RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL : ["byol","oracle"],
        PG_RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL : ["byol","sqlserver"],
        PG_RDS_POSTGRESQL_MULTIAZ_RESERVED_URL : ["postgresql","postgres"]
    }                                  
                                                                        
    RDS_RESERVED_TYPE_BY_URL_OLD = {                                
        RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL : ["included","sqlserver-ex","light"],
        RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL : ["included","sqlserver-ex","medium"],
        RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL : ["included","sqlserver-ex","heavy"],
        RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL : ["included","sqlserver-web","light"],
        RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL : ["included","sqlserver-web","medium"],
        RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL : ["included","sqlserver-web","heavy"],
        RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL : ["included","sqlserver-se","light"],
        RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL : ["included","sqlserver-se","medium"],
        RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL : ["included","sqlserver-se","heavy"],
        PG_RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL : ["included","sqlserver-ex","light"],
        PG_RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL : ["included","sqlserver-ex","medium"],
        PG_RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL : ["included","sqlserver-ex","heavy"],
        PG_RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL : ["included","sqlserver-web","light"],
        PG_RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL : ["included","sqlserver-web","medium"],
        PG_RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL : ["included","sqlserver-web","heavy"],
        PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL : ["included","sqlserver-se","light"],
        PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL : ["included","sqlserver-se","medium"],
        PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL : ["included","sqlserver-se","heavy"]
    }
    
    
    
    
    INSTANCE_TYPE_MAPPING = {
        "udbInstClass.uDBInst" : "db.t1.micro",
        "dbInstClass.uDBInst" : "db.t1.micro",
        "dbInstClass.db.t1.micro" : "db.t1.micro",
        "dbInstClass.db.m3.medium" : "db.m3.medium",
        "dbInstClass.db.m3.large" : "db.m3.large",
        "dbInstClass.db.m3.xlarge" : "db.m3.xlarge",
        "dbInstClass.db.m3.2xlarge" : "db.m3.2xlarge",
        "dbInstClass.smDBInst" : "db.m1.small",
        "dbInstClass.db.m1.small" : "db.m1.small",
        "dbInstClass.medDBInst" : "db.m1.medium",
        "dbInstClass.db.m1.medium" : "db.m1.medium",
        "dbInstClass.lgDBInst" : "db.m1.large",
        "dbInstClass.db.m1.large" : "db.m1.large",
        "dbInstClass.xlDBInst" : "db.m1.xlarge",
        "dbInstClass.db.m1.xlarge" : "db.m1.xlarge",
        "hiMemDBInstClass.xlDBInst" : "db.m2.xlarge",
        "memDBCurrentGen.db.m2.xlarge" : "db.m2.xlarge",
        "hiMemDBInstClass.xxlDBInst" : "db.m2.2xlarge",
        "memDBCurrentGen.db.m2.2xlarge" : "db.m2.2xlarge",
        "hiMemDBInstClass.xxxxDBInst" : "db.m2.4xlarge",
        "memDBCurrentGen.db.m2.4xlarge" : "db.m2.4xlarge",
        "clusterHiMemDB.xxxxxxxxl" : "db.cr1.8xlarge",
        "memDBCurrentGen.db.cr1.8xl": "db.cr1.8xlarge",
    
        # Multiaz instances
        "multiAZDBInstClass.uDBInst" : "db.t1.micro",
        "multiAZDBInstClass.smDBInst" : "db.m1.small",
        "multiAZDBInstClass.medDBInst" : "db.m1.medium",
        "multiAZDBInstClass.lgDBInst" : "db.m1.large",
        "multiAZDBInstClass.xlDBInst" : "db.m1.xlarge",
        "multiAZDBInstClass.db.t1.micro" : "db.t1.micro",
        "multiAZDBInstClass.db.m1.small" : "db.m1.small",
        "multiAZDBInstClass.db.m1.medium" : "db.m1.medium",
        "multiAZDBInstClass.db.m1.large" : "db.m1.large",
        "multiAZDBInstClass.db.m1.xlarge" : "db.m1.xlarge",
        "multiAZDBInstClass.db.m3.medium" : "db.m3.medium",
        "multiAZDBInstClass.db.m3.large" : "db.m3.large",
        "multiAZDBInstClass.db.m3.xlarge" : "db.m3.xlarge",
        "multiAZDBInstClass.db.m3.2xlarge" : "db.m3.2xlarge",
        "multiAZHiMemInstClass.xlDBInst" : "db.m2.xlarge",
        "multiAZHiMemInstClass.xxlDBInst" : "db.m2.2xlarge",
        "multiAZHiMemInstClass.xxxxDBInst" : "db.m2.4xlarge",
        "multiAZClusterHiMemDB.xxxxxxxxl" : "db.cr1.8xlarge",
    
        #Reserved
        "stdDeployRes.u" : "db.t1.micro",
        "stdDeployRes.micro" : "db.t1.micro",
        "stdDeployRes.sm" : "db.m1.small",
        "stdDeployRes.med" : "db.m1.medium",
        "stdDeployRes.lg" : "db.m1.large",
        "stdDeployRes.xl" : "db.m1.xlarge",
        "stdDeployRes.xlHiMem" : "db.m2.xlarge",
        "stdDeployRes.xxlHiMem" : "db.m2.2xlarge",
        "stdDeployRes.xxxxlHiMem" : "db.m2.4xlarge",
        "stdDeployRes.xxxxxxxxl" : "db.cr1.8xlarge",
    
        #Reserved multi az
        "multiAZdeployRes.u" : "db.t1.micro",
        "multiAZdeployRes.sm" : "db.m1.small",
        "multiAZdeployRes.med" : "db.m1.medium",
        "multiAZdeployRes.lg" : "db.m1.large",
        "multiAZdeployRes.xl" : "db.m1.xlarge",
        "multiAZdeployRes.xlHiMem" : "db.m2.xlarge",
        "multiAZdeployRes.xxlHiMem" : "db.m2.2xlarge",
        "multiAZdeployRes.xxxxlHiMem" : "db.m2.4xlarge",
        "multiAZdeployRes.xxxxxxxxl" : "db.cr1.8xlarge"
    
    }
    
        
    def get_reserved_instances_prices(self):
        """
        Implementation of method for getting RDS Reserved pricing. 
        
        Returns:
           result (dict of dict: dict): RDS Reserved pricing in dictionary format.
                
        """
    

    
        currency = self.DEFAULT_CURRENCY
    
        urls_new = [
                    self.RDS_MYSQL_RESERVED_URL,
                    self.RDS_MYSQL_MULTIAZ_RESERVED_URL,
                    self.RDS_ORACLE_LICENSED_RESERVED_URL,
                    self.RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL,
                    self.RDS_ORACLE_BYOL_RESERVED_URL,
                    self.RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL,
                    self.RDS_MSSQL_BYOL_RESERVED_URL,
                    self.RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL,
                    self.RDS_POSTGRESQL_RESERVED_URL,
                    self.RDS_POSTGRESQL_MULTIAZ_RESERVED_URL,
                    self.PG_RDS_MYSQL_RESERVED_URL,
                    self.PG_RDS_MYSQL_MULTIAZ_RESERVED_URL,
                    self.PG_RDS_ORACLE_LICENSED_RESERVED_URL,
                    self.PG_RDS_ORACLE_LICENSED_MULTIAZ_RESERVED_URL,
                    self.PG_RDS_ORACLE_BYOL_RESERVED_URL,
                    self.PG_RDS_ORACLE_BYOL_MULTIAZ_RESERVED_URL,
                    self.PG_RDS_MSSQL_BYOL_RESERVED_URL,
                    self.PG_RDS_MSSQL_BYOL_MULTIAZ_RESERVED_URL,
                    self.PG_RDS_POSTGRESQL_RESERVED_URL,
                    self.PG_RDS_POSTGRESQL_MULTIAZ_RESERVED_URL
        ]
                
        urls_old = [
                    self.RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL,
                    self.RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL,
                    self.RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL,
                    self.RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL,
                    self.RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL,
                    self.RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL,
                    self.RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL,
                    self.RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL,
                    self.RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL,
                    self.PG_RDS_MSSQL_LICENSED_EX_RESERVED_LIGHT_URL,
                    self.PG_RDS_MSSQL_LICENSED_EX_RESERVED_MEDIUM_URL,
                    self.PG_RDS_MSSQL_LICENSED_EX_RESERVED_HEAVY_URL,
                    self.PG_RDS_MSSQL_LICENSED_WEB_RESERVED_LIGHT_URL,
                    self.PG_RDS_MSSQL_LICENSED_WEB_RESERVED_MEDIUM_URL,
                    self.PG_RDS_MSSQL_LICENSED_WEB_RESERVED_HEAVY_URL,
                    self.PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_LIGHT_URL,
                    self.PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_MEDIUM_URL,
                    self.PG_RDS_MSSQL_LICENSED_STANDARD_RESERVED_HEAVY_URL
        ]
    
    
        result_regions = []
        result_regions_index = {}
        result = {
            "config" : {
                "currency" : currency,
            },
            "regions" : result_regions
        }
    
        for u in urls_old:
            info = self.RDS_RESERVED_TYPE_BY_URL_OLD[u]
            dblicense = info[0]
            db = info[1]
            utilization_type = info[2]
    
            data = self.load_data(u)
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
                        region_name = self.JSON_NAME_TO_REGIONS_API[r["region"]]

                        if region_name in result_regions_index:
                            instance_types = result_regions_index[region_name]["instanceTypes"]
                        else:
                            instance_types = []
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })
                            result_regions_index[region_name] = result_regions[-1]
    
                        if "instanceTypes" in r:
                            for it in r["instanceTypes"]:
                                multiaz = self.RDS_MULTIAZ_MAPPING[it["type"]]
                                if "tiers" in it:
                                    for s in it["tiers"]:
                                        _type = s["size"]
   
                                        prices = {
                                            "1" : {
                                                "hourly" : None,
                                                "upfront" : None
                                            },
                                            "3" : {
                                                "hourly" : None,
                                                "upfront" : None
                                            }
                                        }
    
                                        instance_types.append({
                                            "type" : _type,
                                            "multiaz" : multiaz,
                                            "license" : dblicense,
                                            "db" : db,
                                            "utilization" : utilization_type,
                                            "prices" : prices
                                        })
    
                                        for price_data in s["valueColumns"]:
                                            price = None
                                            try:
                                                price = float(re.sub("[^0-9\.]", "", 
                                                                     price_data["prices"][currency]))
                                            except ValueError:
                                                price = None
    
                                            if price_data["name"] == "yrTerm1":
                                                prices["1"]["upfront"] = price
                                            elif price_data["name"] == "yrTerm1Hourly":
                                                prices["1"]["hourly"] = price
                                            elif price_data["name"] == "yearTerm1Hourly":
                                                prices["1"]["hourly"] = price
                                            elif price_data["name"] == "yrTerm3":
                                                prices["3"]["upfront"] = price
                                            elif price_data["name"] == "yrTerm3Hourly":
                                                prices["3"]["hourly"] = price
                                            elif price_data["name"] == "yearTerm3Hourly":
                                                prices["3"]["hourly"] = price
                                                
        for u in urls_new:
            if u in self.RDS_RESERVED_TYPE_BY_URL_NEW:
                licensedb = self.RDS_RESERVED_TYPE_BY_URL_NEW[u]
                multiaz = "single";
            else:
                licensedb = self.RDS_RESERVED_MULTIAZ_TYPE_BY_URL_NEW[u];
                multiaz = "multi-az";
            
            data = self.load_data(u)
            
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
                        region_name = r["region"]
                        if region_name in result_regions_index:
                            instance_types = result_regions_index[region_name]["instanceTypes"]
                        else:
                            instance_types = []
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })
                            result_regions_index[region_name] = result_regions[-1]
    
                        if "instanceTypes" in r:
                            for it in r["instanceTypes"]:
                                instance_type = it["type"]
                                prices = {
                                                      "1" : {
                                                             "noUpfront" : {
                                                                            "hourly" : None,
                                                                            "upfront" : None
                                                                            },
                                                             "partialUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               },
                                                             "allUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               }
                                                             },
                                                      "3" : {
                                                             "noUpfront" : {
                                                                            "hourly" : None,
                                                                            "upfront" : None
                                                                            },
                                                             "partialUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               },
                                                             "allUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               }
                                                             }
                                                      }
                                instance_types.append({
                                    "type" : instance_type,
                                    "multiaz" : multiaz,
                                    "license" : licensedb[0],
                                    "db" : licensedb[1],
                                    "utilization" : "heavy",
                                    "prices" : prices
                                })
                                          
                                if "terms" in it:
                                    for s in it["terms"]:
                                        term=s["term"]
                                          
                                        for po_data in s["purchaseOptions"]:
                                            po=po_data["purchaseOption"]
                                            
                                            for price_data in po_data["valueColumns"]:
                                                price = None
                                                try:
                                                    price = float(re.sub("[^0-9\.]", "", 
                                                                 price_data["prices"][currency]))
                                                except ValueError:
                                                    price = None
                                                        
                                                if term=="yrTerm1":
                                                    if price_data["name"] == "upfront":
                                                        prices["1"][po]["upfront"] = price
                                                    elif price_data["name"] == "monthlyStar":
                                                        prices["1"][po]["hourly"] = price/730
                                                elif term=="yrTerm3":
                                                    if price_data["name"] == "upfront":
                                                        prices["3"][po]["upfront"] = price
                                                    elif price_data["name"] == "monthlyStar":
                                                        prices["3"][po]["hourly"] = price/730
    
                                        
    
        return result
    
    
    
    def get_ondemand_instances_prices(self):
        """
        Implementation of method for getting RDS On-Denand pricing. 
        
        Returns:
           result (dict of dict: dict): RDS On-Denand pricing in dictionary format.
                
        """

    
        currency = self.DEFAULT_CURRENCY
    
        result_regions = []
        result = {
            "config" : {
                "currency" : currency,
                "unit" : "perhr"
            },
            "regions" : result_regions
        }
    
        urls = [
                self.RDS_MYSQL_ON_DEMAND_URL,
                self.RDS_MYSQL_MULTIAZ_ON_DEMAND_URL,
                self.RDS_ORACLE_LICENSED_ON_DEMAND_URL,
                self.RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL,
                self.RDS_ORACLE_BYOL_ON_DEMAND_URL,
                self.RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL,
                self.RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL,
                self.RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL,
                self.RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL,
                self.RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL,
                self.RDS_MSSQL_BYOL_ON_DEMAND_URL,
                self.RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL,
                self.RDS_POSTGRESQL_ON_DEMAND_URL,
                self.RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL,
                self.PG_RDS_MYSQL_ON_DEMAND_URL,
                self.PG_RDS_MYSQL_MULTIAZ_ON_DEMAND_URL,
                self.PG_RDS_ORACLE_LICENSED_ON_DEMAND_URL,
                self.PG_RDS_ORACLE_LICENSED_MULTIAZ_ON_DEMAND_URL,
                self.PG_RDS_ORACLE_BYOL_ON_DEMAND_URL,
                self.PG_RDS_ORACLE_BYOL_MULTIAZ_ON_DEMAND_URL,
                self.PG_RDS_MSSQL_LICENSED_EXPRESS_ON_DEMAND_URL,
                self.PG_RDS_MSSQL_LICENSED_WEB_ON_DEMAND_URL,
                self.PG_RDS_MSSQL_LICENSED_STANDARD_ON_DEMAND_URL,
                self.PG_RDS_MSSQL_LICENSED_STANDARD_MULTIAZ_ON_DEMAND_URL,
                self.PG_RDS_MSSQL_BYOL_ON_DEMAND_URL,
                self.PG_RDS_MSSQL_BYOL_MULTIAZ_ON_DEMAND_URL,
                self.PG_RDS_POSTGRESQL_ON_DEMAND_URL,
                self.PG_RDS_POSTGRESQL_MULTIAZ_ON_DEMAND_URL
        ]
    
        for u in urls:
            if u in self.RDS_ONDEMAND_TYPE_BY_URL:
                licensedb = self.RDS_ONDEMAND_TYPE_BY_URL[u]
                multiaz = "single";
            else:
                licensedb = self.RDS_ONDEMAND_MULTIAZ_TYPE_BY_URL[u];
                multiaz = "multi-az";

            data = self.load_data(u)
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
                        region_name = self.JSON_NAME_TO_REGIONS_API[r["region"]]

                        instance_types = []
                        if "types" in r:
                            for it in r["types"]:
                                if "tiers" in it:
                                    for s in it["tiers"]:
                                        _type = s["name"]

                                        price = None
                                        try:
                                            price = float(re.sub("[^0-9\.]", "", 
                                                                 s["prices"][currency]))
                                        except ValueError:
                                            price = None
    
                                        instance_types.append({
                                            "type" : _type,
                                            "multiaz" : multiaz,
                                            "license" : licensedb[0],
                                            "db" : licensedb[1],
                                            "price" : price
                                        })
    
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })                 
                                                       
        return result
    
            
    def print_table(self,u):
        """
        Method printing the RDS pricing data to the console
            in the Pretty Table format (requires Pretty Table 
            import).
        
        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
        
        Returns:
           Prints RDS pricing in the Pretty Table format.
                
        """
        try:
            from prettytable import PrettyTable
        except ImportError:
            print "ERROR: Please install 'prettytable' using pip:    pip install prettytable"       
        data = None
        
        if u not in ["ondemand","reserved"]:
            print("Function requires Reservation parameter at the first"+
                  "position. Possible values:"+
                  "\"ondemand\" or \"reserved\".")
        else:
            
            if u == "ondemand":
                data = self.get_ondemand_instances_prices()           
                x = PrettyTable()
                try:
                    x.set_field_names(["region", 
                                       "type", 
                                       "multiaz", 
                                       "license", 
                                       "db", 
                                       "price"])
                except AttributeError:
                    x.field_names = ["region", 
                                     "type", 
                                     "multiaz", 
                                     "license", 
                                     "db", 
                                     "price"]
    
                try:
                    x.aligns[-1] = "l"
                except AttributeError:
                    x.align["price"] = "l"
    
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        x.add_row([region_name, 
                                   it["type"], 
                                   it["multiaz"], 
                                   it["license"], 
                                   it["db"], 
                                   self.none_as_string(it["price"])])  
            
            elif u == "reserved":          
                data = self.get_reserved_instances_prices()
                x = PrettyTable()
                try:
                    x.set_field_names(["region", 
                                       "type", 
                                       "multiaz", 
                                       "license", 
                                       "db", 
                                       "utilization", 
                                       "term",
                                       "payment_type", 
                                       "price", 
                                       "upfront"])
                except AttributeError:
                    x.field_names = ["region", 
                                     "type", 
                                     "multiaz", 
                                     "license", 
                                     "db", 
                                     "utilization", 
                                     "term",
                                     "payment_type", 
                                     "price", 
                                     "upfront"]
    
                try:
                    x.aligns[-1] = "l"
                    x.aligns[-2] = "l"
                except AttributeError:
                    x.align["price"] = "l"
                    x.align["upfront"] = "l"
    
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        for term in it["prices"]:
                            if "noUpfront" in it["prices"][term] or "partialUpfront" in it["prices"][term] or "allUpfront" in it["prices"][term]:
                                for po in it["prices"][term]:                               
                                    x.add_row([region_name,
                                               it["type"],
                                               it["multiaz"],
                                               it["license"],
                                               it["db"],
                                               it["utilization"],
                                               term,
                                               po,
                                               self.none_as_string(it["prices"][term][po]["hourly"]),
                                               self.none_as_string(it["prices"][term][po]["upfront"])])
                            else:
                                x.add_row([region_name,
                                           it["type"],
                                           it["multiaz"],
                                           it["license"],
                                           it["db"],
                                           it["utilization"],
                                           term,
                                           "",
                                           self.none_as_string(it["prices"][term]["hourly"]),
                                           self.none_as_string(it["prices"][term]["upfront"])])

            print x

    def save_csv(self,u,path=os.getcwd()+"\\",name=None):
        """
        Method saving the RDS pricing data in CSV format to the
            cpecified location.

        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
            path (str): System path for saving the data file. Current
                directory is the the defauilt value.
            name (str): The desired name of the file. The default
                values are "RDS_reserved_pricing.csv" for Reserved
                and "RDS_ondemand_pricing.csv" for On-Demand.
        
        Returns:
           Prints RDS pricing in the CSV format (console).
                
        """
        data = None
        
        if u not in ["ondemand","reserved"]:
            print("Function requires Reservation parameter at the first"+
                  "position. Possible values:"+
                  "\"ondemand\" or \"reserved\".")
        
        elif u == "ondemand":
            if name is None:
                name="RDS_ondemand_pricing.csv"
            data = self.get_ondemand_instances_prices()   
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,multiaz,license,db,price"
            writer.writerow(["region",
                             "type",
                             "multiaz",
                             "license",
                             "db",
                             "price"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    print "%s,%s,%s,%s,%s,%s" % (region_name, 
                                                 it["type"], 
                                                 it["multiaz"], 
                                                 it["license"], 
                                                 it["db"], 
                                                 self.none_as_string(it["price"]))
                    writer.writerow([region_name, 
                                     it["type"], 
                                     it["multiaz"], 
                                     it["license"], 
                                     it["db"], 
                                     self.none_as_string(it["price"])])
        
        elif u == "reserved":
            if name is None:
                name="RDS_reserved_pricing.csv"
            data = self.get_reserved_instances_prices()
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,multiaz,license,db,utilization,term,payment_type,price,upfront"
            writer.writerow(["region",
                             "type",
                             "multiaz",
                             "license",
                             "db",
                             "utilization",
                             "term",
                             "payment_type",
                             "price",
                             "upfront"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        if "noUpfront" in it["prices"][term] or "partialUpfront" in it["prices"][term] or "allUpfront" in it["prices"][term]:
                            for po in it["prices"][term]:
                                print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (region_name,
                                                                         it["type"],
                                                                         it["multiaz"],
                                                                         it["license"],
                                                                         it["db"],
                                                                         it["utilization"],
                                                                         term,
                                                                         po,
                                                                         self.none_as_string(it["prices"][term][po]["hourly"]),
                                                                         self.none_as_string(it["prices"][term][po]["upfront"]))
                                writer.writerow([region_name, 
                                                 it["type"], 
                                                 it["multiaz"], 
                                                 it["license"], 
                                                 it["db"],
                                                 it["utilization"], 
                                                 term, 
                                                 po,
                                                 self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                 self.none_as_string(it["prices"][term][po]["upfront"])])
                        else:
                            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (region_name,
                                                                     it["type"],
                                                                     it["multiaz"],
                                                                     it["license"],
                                                                     it["db"],
                                                                     it["utilization"],
                                                                     term,
                                                                     "",
                                                                     self.none_as_string(it["prices"][term]["hourly"]),
                                                                     self.none_as_string(it["prices"][term]["upfront"]))
                            writer.writerow([region_name,
                                             it["type"],
                                             it["multiaz"],
                                             it["license"],
                                             it["db"],
                                             it["utilization"],
                                             term,
                                             "",
                                             self.none_as_string(it["prices"][term]["hourly"]),
                                             self.none_as_string(it["prices"][term]["upfront"])])
                            
                            


class RSPrices(AWSPrices):
    """
    Class for retrieving the Redshift pricing. Child of :class:`awspricingfull.AWSPrices` class.
    
    Attributes:
        RS_ON_DEMAND_URL (str): Undocumented AWS Pricing API 
            URL - On-Demand Redshift Nodes
        PG_RS_ON_DEMAND_URL (str): Undocumented AWS Pricing API
            URL - Reserved Redshift Nodes, Previous Generation
        RS_RESERVED_URL (str): Undocumented AWS Pricing API
            URL - Reserved Redshift Nodes
        PG_RS_RESERVED_URL (str): Undocumented AWS Pricing API
            URL - Reserved Redshift Nodes, Previous Generation
                       
    """

       
    RS_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/redshift/"+
                             "pricing-on-demand-redshift-instances.min.js")
    PG_RS_ON_DEMAND_URL=("http://a0.awsstatic.com/pricing/1/redshift/"+
                             "previous-generation/pricing-on-demand-redshift-instances.min.js")
    RS_RESERVED_URL=("http://a0.awsstatic.com/pricing/1/redshift/"+
                                                "pricing-reserved-redshift-instances.min.js")
    PG_RS_RESERVED_URL=("http://a0.awsstatic.com/pricing/1/redshift/"+
                                                "previous-generation/pricing-reserved-redshift-instances.min.js")
    
    
    
    
    def get_reserved_instances_prices(self):
        """
        Implementation of method for getting Redshift Reserved pricing. 
        
        Returns:
           result (dict of dict: dict): Redshift Reserved pricing in dictionary format.
                
        """

    
        currency = self.DEFAULT_CURRENCY
    
        urls = [
            self.RS_RESERVED_URL,
            self.PG_RS_RESERVED_URL
            ]
    
        result_regions = []
        result_regions_index = {}
        result = {
            "config" : {
                "currency" : currency,
            },
            "regions" : result_regions
        }
        
        for u in urls:
           
            data = self.load_data(u)
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
                        region_name = r["region"]
                        if region_name in result_regions_index:
                            instance_types = result_regions_index[region_name]["instanceTypes"]
                        else:
                            instance_types = []
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })
                            result_regions_index[region_name] = result_regions[-1]
    
                        if "instanceTypes" in r:
                            for it in r["instanceTypes"]:
                                instance_type = it["type"]
                                prices = {
                                                      "1" : {
                                                             "noUpfront" : {
                                                                            "hourly" : None,
                                                                            "upfront" : None
                                                                            },
                                                             "partialUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               },
                                                             "allUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               }
                                                             },
                                                      "3" : {
                                                             "noUpfront" : {
                                                                            "hourly" : None,
                                                                            "upfront" : None
                                                                            },
                                                             "partialUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               },
                                                             "allUpfront":{
                                                                               "hourly" : None,
                                                                               "upfront" : None
                                                                               }
                                                             }
                                                      }
                                instance_types.append({
                                    "type" : instance_type,
                                    "prices" : prices
                                })
                                        
          
                                if "terms" in it:
                                    for s in it["terms"]:
                                        term=s["term"]
                                        
        
        
                                        for po_data in s["purchaseOptions"]:
                                            po=po_data["purchaseOption"]
                                            upfr_temp=0
                                            for price_data in po_data["valueColumns"]:
                                                price = None
                                                try:
                                                    price = float(re.sub("[^0-9\.]", "",
                                                                         price_data["prices"][currency]))
                                                except ValueError:
                                                    price = None
                                                                                                           
                                                if term=="yrTerm1":
                                                    if price_data["name"] == "upfront":
                                                        prices["1"][po]["upfront"] = price
                                                    elif price_data["name"] == "monthlyStar":
                                                        prices["1"][po]["hourly"] = price/730
                                                elif term=="yrTerm3":
                                                    if price_data["name"] == "upfront":
                                                        prices["3"][po]["upfront"] = price
                                                    elif price_data["name"] == "monthlyStar":
                                                        prices["3"][po]["hourly"] = price/730

    
        return result
    
    def get_ondemand_instances_prices(self):
        """
        Implementation of method for getting Redshift On-Denand pricing. 
        
        Returns:
           result (dict of dict: dict): Redshift On-Denand pricing in dictionary format.
                
        """
        currency = self.DEFAULT_CURRENCY
        
        urls = [
            self.RS_ON_DEMAND_URL,
            self.PG_RS_ON_DEMAND_URL
        ]
         
        result_regions = []
        result = {
            "config" : {
                "currency" : currency,
                "unit" : "perhr"
            },
            "regions" : result_regions
        }
    
        for u in urls:
    
    
            data = self.load_data(u)
            if ("config" in data and data["config"] and "regions" 
                in data["config"] and data["config"]["regions"]):
                for r in data["config"]["regions"]:
                    if "region" in r and r["region"]:
    
                        region_name = r["region"]
                        instance_types = []
                        if "instanceTypes" in r:
                            for it in r["instanceTypes"]:
                                if "tiers" in it:
                                    for s in it["tiers"]:
                                        instance_type = s["size"]
    
                                        for price_data in s["valueColumns"]:
                                            price = None
                                            try:
                                                price =float(re.sub("[^0-9\.]", "",
                                                                    price_data["prices"][currency]))
                                            except:
                                                price = None
                                            _type = instance_type
                                            instance_types.append({
                                                "type" : _type,
                                                "price" : price
                                            })
    
                            result_regions.append({
                                "region" : region_name,
                                "instanceTypes" : instance_types
                            })
    
        return result

    

    def print_table(self,u):
        """
        Method printing the Redshift pricing data to the console
            in the Pretty Table format (requires Pretty Table 
            import).
        
        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
        
        Returns:
           Prints Redshift pricing in the Pretty Table format.
                
        """
        try:
            from prettytable import PrettyTable
        except ImportError:
            print "ERROR: Please install 'prettytable' using pip:    pip install prettytable"
       
        data = None
        
        if u not in ["ondemand","reserved"]:
            print("Function requires Reservation parameter at the first"+
                  "position. Possible values:"+
                  "\"ondemand\" or \"reserved\".")
        else:
            
            if u == "ondemand":
                data = self.get_ondemand_instances_prices()
                x = PrettyTable()
                try:
                    x.set_field_names(["region", "type", "price"])
                except AttributeError:
                    x.field_names = ["region", "type", "price"]
    
                try:
                    x.aligns[-1] = "l"
                except AttributeError:
                    x.align["price"] = "l"
    
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        x.add_row([region_name, it["type"], self.none_as_string(it["price"])])
                  
            elif u == "reserved":
                data = self.get_reserved_instances_prices()
                x = PrettyTable()
                try:
                    x.set_field_names(["region", "type", "term","payment_type" "price", "upfront"])
                except AttributeError:
                    x.field_names = ["region", "type", "term", "payment_type","price", "upfront"]
    
                try:
                    x.aligns[-1] = "l"
                    x.aligns[-2] = "l"
                except AttributeError:
                    x.align["price"] = "l"
                    x.align["upfront"] = "l"
    
                for r in data["regions"]:
                    region_name = r["region"]
                    for it in r["instanceTypes"]:
                        for term in it["prices"]:
                            for po in it["prices"][term]:
                                x.add_row([region_name,
                                          it["type"],
                                          term,
                                          po,
                                          self.none_as_string(it["prices"][term][po]["hourly"]),
                                          self.none_as_string(it["prices"][term][po]["upfront"])])
    
            print x
    
    
    def save_csv(self,u,path=os.getcwd()+"\\",name=None):
        """
        Method saving the Redshift pricing data in CSV format to the
            cpecified location.

        Args:
            u (str): Parameter specifying On-Demand ("ondemand") or 
                Reserved ("reserved") pricing option.
            path (str): System path for saving the data file. Current
                directory is the the defauilt value.
            name (str): The desired name of the file. The default
                values are "Redshift_reserved_pricing.csv" for Reserved
                and "Redshift_ondemand_pricing.csv" for On-Demand.
        
        Returns:
           Prints Redshift pricing in the CSV format (console).
                
        """
        if u not in ["ondemand","reserved"]:
            print("Function requires Reservation parameter at the first"+
                  "position. Possible values:"+
                  "\"ondemand\" or \"reserved\".")
            
        elif u == "ondemand":
            if name is None:
                name="RS_ondemand_pricing.csv"
            data = self.get_ondemand_instances_prices()
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,price"
            writer.writerow(["region","type","price"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow([region_name,it["type"],self.none_as_string(it["price"])])
                    print "%s,%s,%s" % (region_name, 
                                           it["type"], 
                                           self.none_as_string(it["price"]))
        elif u == "reserved":
            if name is None:
                name="RS_reserved_pricing.csv"
            data = self.get_reserved_instances_prices()
            writer = csv.writer(open(path+name, 'wb'))
            print "region,type,term,payment_type,price,upfront"
            writer.writerow(["region","type","term","payment_type","price","upfront"])
            for r in data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        for po in it["prices"][term]:
                            print "%s,%s,%s,%s,%s,%s" % (region_name, 
                                                            it["type"],  
                                                            term, 
                                                            po, 
                                                            self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                            self.none_as_string(it["prices"][term][po]["upfront"]))
                            writer.writerow([region_name, 
                                             it["type"],
                                             term, 
                                             po, 
                                             self.none_as_string(it["prices"][term][po]["hourly"]), 
                                             self.none_as_string(it["prices"][term][po]["upfront"])])

    
    

class AllAWSPrices(AWSPrices):
    """
    Class for retrieving the instance pricing for 4 AWS Services:
        EC2, RDS, ElastiCache and Redshift. Child of :class:`awspricingfull.AWSPrices` class.
    
    Attributes:
        ec2 (EC2Prices): instance of :class:`awspricingfull.EC2Prices` class containing methods
            for EC2 pricing retrieval.
        elc (ELCPrices): instance of :class:`awspricingfull.ELCPrices` class containing methods
            for ElastiCache pricing retrieval.    
        rds (RDSPrices): instance of :class:`awspricingfull.RDSPrices` class containing methods
            for RDS pricing retrieval.            
        rs (RSPrices): instance of :class:`awspricingfull.RSPrices` class containing methods
            for Redshift pricing retrieval.                       
    """
        
    ec2=EC2Prices()
    elc=ELCPrices()
    rds=RDSPrices()
    rs=RSPrices()
    
    def return_json(self,u):
        """
        Method printing the pricing data in JSON format to Console.
        
        Args:
            u (str): Parameter specifying On-Demand ("ondemand"), 
                Reserved ("reserved") or both ("all") pricing option.
        
        Returns:
           str: Pricing data in JSON string format or an error message.
                
        """
        if u not in ["ondemand","reserved", "all"]:
            print("Function requires Reservation parameter at the first"+
                  "position. Possible values:"+
                  "\"ondemand\" or \"reserved\" or \"all\".")
        else:
            
            if u=="ondemand":
                ec2_data=self.ec2.get_ondemand_instances_prices()
                elc_data=self.elc.get_ondemand_instances_prices()
                rds_data=self.rds.get_ondemand_instances_prices()
                rs_data=self.rs.get_ondemand_instances_prices()
                
                res={
                     "ec2":ec2_data,
                     "elasticache":elc_data,
                     "rds":rds_data,
                     "redshift":rs_data
                     }
                
                        
            elif u=="reserved":
                ec2_data=self.ec2.get_reserved_instances_prices()
                elc_data=self.elc.get_reserved_instances_prices()
                rds_data=self.rds.get_reserved_instances_prices()
                rs_data=self.rs.get_reserved_instances_prices()
                
                res={
                     "ec2":ec2_data,
                     "elasticache":elc_data,
                     "rds":rds_data,
                     "redshift":rs_data
                     }
                
            elif u=="all":
                ec2_data_od=self.ec2.get_ondemand_instances_prices()
                elc_data_od=self.elc.get_ondemand_instances_prices()
                rds_data_od=self.rds.get_ondemand_instances_prices()
                rs_data_od=self.rs.get_ondemand_instances_prices()
                ec2_data_r=self.ec2.get_reserved_instances_prices()
                elc_data_r=self.elc.get_reserved_instances_prices()
                rds_data_r=self.rds.get_reserved_instances_prices()
                rs_data_r=self.rs.get_reserved_instances_prices()
                
                res={
                     "ondemand":{
                                  "ec2":ec2_data_od,
                                  "elasticache":elc_data_od,
                                  "rds":rds_data_od,
                                  "redshift":rs_data_od},
                     "reserved":{
                                 "ec2":ec2_data_r,
                                 "elasticache":elc_data_r,
                                 "rds":rds_data_r,
                                 "redshift":rs_data_r}
                     }
                
            return json.dumps(res)
        
            
    
    def save_csv(self,u,path=os.getcwd()+"\\",name=None):
        """
        Method saving the full pricing data in CSV format to the
            cpecified location.

        Args:
            u (str): Parameter specifying On-Demand ("ondemand"),
                Reserved ("reserved") or both ("all") pricing option.
            path (str): System path for saving the data file. Current
                directory is the the defauilt value.
            name (str): The desired name of the file. The default
                values are "FULL_reserved_pricing.csv" for Reserved,
                "FULL_ondemand_pricing.csv" for On-Demand and
                "FULL_all_pricing.csv" for both.
        
        Returns:
           Prints Full pricing in the CSV format (console).
                
        """   
        
        if u not in ["ondemand","reserved","all"]:
            print("Function requires Reservation parameter at the first"+
                  "position. Possible values:"+
                  "\"ondemand\" or \"reserved\" or \"all\".")     

        elif u=="ondemand":
            
            if name is None:
                name="FULL_ondemand_pricing.csv"
            
            ec2_data=self.ec2.get_ondemand_instances_prices()
            elc_data=self.elc.get_ondemand_instances_prices()
            rds_data=self.rds.get_ondemand_instances_prices()
            rs_data=self.rs.get_ondemand_instances_prices()
                       
            writer = csv.writer(open(path+name, 'wb'))
            print "service,region,type,multiaz,license,db,os,price"
            writer.writerow(["service",
                             "region",
                             "type",
                             "multiaz",
                             "license",
                             "db",
                             "os",
                             "price"])
            
            
            for r in ec2_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow(["ec2",
                                     region_name,
                                     it["type"],
                                     "",
                                     "",
                                     "",
                                     it["os"],
                                     self.none_as_string(it["price"])])
                    print "%s,%s,%s,%s,%s,%s,%s,%s" % ("ec2",
                                                       region_name, 
                                                       it["type"], 
                                                       "",
                                                       "",
                                                       "",
                                                       it["os"], 
                                                       self.none_as_string(it["price"]))
            
            for r in elc_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow(["elasticache",
                                     region_name,
                                     it["type"],
                                     "",
                                     "",
                                     "",
                                     "",
                                     self.none_as_string(it["price"])])
                    print "%s,%s,%s,%s,%s,%s,%s,%s" % ("elasticache",
                                                       region_name, 
                                                       it["type"],
                                                       "",
                                                       "",
                                                       "",
                                                       "",
                                                       self.none_as_string(it["price"]))
            
            for r in rds_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    print "%s,%s,%s,%s,%s,%s,%s,%s" % ("rds",
                                                       region_name, 
                                                       it["type"], 
                                                       it["multiaz"], 
                                                       it["license"], 
                                                       it["db"],
                                                       "", 
                                                       self.none_as_string(it["price"]))
                    writer.writerow(["rds",
                                     region_name, 
                                     it["type"], 
                                     it["multiaz"], 
                                     it["license"], 
                                     it["db"],
                                     "",
                                     self.none_as_string(it["price"])])
            
            for r in rs_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow(["redshift",
                                     region_name,
                                     it["type"],
                                     "",
                                     "",
                                     "",
                                     "",
                                     self.none_as_string(it["price"])])
                    print "%s,%s,%s,%s,%s,%s,%s,%s" % ("redshift",
                                                       region_name, 
                                                       it["type"], 
                                                       "",
                                                       "",
                                                       "",
                                                       "", 
                                                       self.none_as_string(it["price"]))
        
        elif u=="reserved":
            if name is None:
                name="FULL_reserved_pricing.csv"
            
            ec2_data=self.ec2.get_reserved_instances_prices()
            elc_data=self.elc.get_reserved_instances_prices()
            rds_data=self.rds.get_reserved_instances_prices()
            rs_data=self.rs.get_reserved_instances_prices()
                       
            writer = csv.writer(open(path+name, 'wb'))
            print "service,region,type,multiaz,license,db,os,utilization,term,payment_type,price,upfront"
            writer.writerow(["service",
                             "region",
                             "type",
                             "multiaz",
                             "license",
                             "db",
                             "os",
                             "utilization",
                             "term",
                             "payment_type",
                             "price",
                             "upfront"])
            
            
            for r in ec2_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        for po in it["prices"][term]:
                            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("ec2",
                                                                           region_name, 
                                                                           it["type"], 
                                                                           "",
                                                                           "",
                                                                           "",
                                                                           it["os"], 
                                                                           "heavy", 
                                                                           term, 
                                                                           po, 
                                                                           self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                                           self.none_as_string(it["prices"][term][po]["upfront"]))
                            writer.writerow(["ec2",
                                             region_name, 
                                             it["type"], 
                                             "",
                                             "",
                                             "",
                                             it["os"], 
                                             "heavy", 
                                             term, 
                                             po, 
                                             self.none_as_string(it["prices"][term][po]["hourly"]), 
                                             self.none_as_string(it["prices"][term][po]["upfront"])])
            
            for r in elc_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("elasticache",
                                                                       region_name, 
                                                                       it["type"],
                                                                       "",
                                                                       "",
                                                                       "",
                                                                       "", 
                                                                       it["utilization"], 
                                                                       term, 
                                                                       "",
                                                                       self.none_as_string(it["prices"][term]["hourly"]), 
                                                                       self.none_as_string(it["prices"][term]["upfront"]))
                        writer.writerow(["elasticache",
                                         region_name, 
                                         it["type"],
                                         "",
                                         "",
                                         "",
                                         "", 
                                         it["utilization"], 
                                         term,
                                         "", 
                                         self.none_as_string(it["prices"][term]["hourly"]), 
                                         self.none_as_string(it["prices"][term]["upfront"])])
                        
            for r in rds_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        if "noUpfront" in it["prices"][term] or "partialUpfront" in it["prices"][term] or "allUpfront" in it["prices"][term]:
                            for po in it["prices"][term]:
                                print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("rds",
                                                                               region_name, 
                                                                               it["type"], 
                                                                               it["multiaz"], 
                                                                               it["license"], 
                                                                               it["db"], 
                                                                               "", 
                                                                               it["utilization"], 
                                                                               term, 
                                                                               po,
                                                                               self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                                               self.none_as_string(it["prices"][term][po]["upfront"]))
                                writer.writerow(["rds",
                                                 region_name, 
                                                 it["type"], 
                                                 it["multiaz"], 
                                                 it["license"], 
                                                 it["db"],
                                                 "", 
                                                 it["utilization"], 
                                                 term, 
                                                 po,
                                                 self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                 self.none_as_string(it["prices"][term][po]["upfront"])])
                        else:
                            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("rds",
                                                                           region_name,
                                                                           it["type"],
                                                                           it["multiaz"],
                                                                           it["license"],
                                                                           it["db"],
                                                                           "",
                                                                           it["utilization"],
                                                                           term,
                                                                           "",
                                                                           self.none_as_string(it["prices"][term]["hourly"]),
                                                                           self.none_as_string(it["prices"][term]["upfront"]))
                            writer.writerow(["rds",
                                             region_name,
                                             it["type"],
                                             it["multiaz"],
                                             it["license"],
                                             it["db"],
                                             "",
                                             it["utilization"],
                                             term,
                                             "",
                                             self.none_as_string(it["prices"][term]["hourly"]),
                                             self.none_as_string(it["prices"][term]["upfront"])])                
                        
                
            for r in rs_data["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        for po in it["prices"][term]:
                            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("redshift",
                                                                           region_name, 
                                                                           it["type"], 
                                                                           "",
                                                                           "",
                                                                           "",
                                                                           "", 
                                                                           "heavy", 
                                                                           term, 
                                                                           po, 
                                                                           self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                                           self.none_as_string(it["prices"][term][po]["upfront"]))
                            writer.writerow(["redshift",
                                             region_name, 
                                             it["type"], 
                                             "",
                                             "",
                                             "",
                                             "", 
                                             "heavy", 
                                             term, 
                                             po, 
                                             self.none_as_string(it["prices"][term][po]["hourly"]), 
                                             self.none_as_string(it["prices"][term][po]["upfront"])])
        elif u=="all":
            if name is None:
                name="FULL_all_pricing.csv"
            
            ec2_data_od=self.ec2.get_ondemand_instances_prices()
            elc_data_od=self.elc.get_ondemand_instances_prices()
            rds_data_od=self.rds.get_ondemand_instances_prices()
            rs_data_od=self.rs.get_ondemand_instances_prices()
            ec2_data_r=self.ec2.get_reserved_instances_prices()
            elc_data_r=self.elc.get_reserved_instances_prices()
            rds_data_r=self.rds.get_reserved_instances_prices()
            rs_data_r=self.rs.get_reserved_instances_prices()
                       
            writer = csv.writer(open(path+name, 'wb'))
            print "reserved_od,service,region,type,multiaz,license,db,os,utilization,term,payment_type,price,upfront"
            
            
            
            writer.writerow(["reserved_od",
                             "service",
                             "region",
                             "type",
                             "multiaz",
                             "license",
                             "db",
                             "os",
                             "utilization",
                             "term",
                             "payment_type",
                             "price",
                             "upfront"])

           
            
            for r in ec2_data_od["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow(["ondemand",
                                      "ec2",
                                      region_name, 
                                      it["type"], 
                                      "",
                                      "",
                                      "",
                                      it["os"], 
                                      "", 
                                      "", 
                                      "", 
                                      self.none_as_string(it["price"]), 
                                      ""])
                    
                    print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("ondemand",
                                                                      "ec2",
                                                                      region_name, 
                                                                      it["type"], 
                                                                      "",
                                                                      "",
                                                                      "",
                                                                      it["os"], 
                                                                      "", 
                                                                      "", 
                                                                      "", 
                                                                      self.none_as_string(it["price"]), 
                                                                      "")
            
            for r in elc_data_od["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("ondemand",
                                                                      "elasticache",
                                                                      region_name, 
                                                                      it["type"],
                                                                      "",
                                                                      "",
                                                                      "",
                                                                      "", 
                                                                      "", 
                                                                      "", 
                                                                      "",
                                                                      self.none_as_string(it["price"]), 
                                                                      "")
                    writer.writerow(["ondemand",
                                      "elasticache",
                                      region_name, 
                                      it["type"],
                                      "",
                                      "",
                                      "",
                                      "", 
                                      "", 
                                      "", 
                                      "",
                                      self.none_as_string(it["price"]), 
                                      ""])
                        
            for r in rds_data_od["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("ondemand",
                                                                      "rds",
                                                                      region_name, 
                                                                      it["type"], 
                                                                      it["multiaz"], 
                                                                      it["license"], 
                                                                      it["db"], 
                                                                      "", 
                                                                      "", 
                                                                      "", 
                                                                      "",
                                                                      self.none_as_string(it["price"]), 
                                                                      "")
                    writer.writerow(["ondemand",
                                      "rds",
                                      region_name, 
                                      it["type"], 
                                      it["multiaz"], 
                                      it["license"], 
                                      it["db"], 
                                      "", 
                                      "", 
                                      "", 
                                      "",
                                      self.none_as_string(it["price"]), 
                                      ""])
                        
                
            for r in rs_data_od["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    writer.writerow(["ondemand",
                                      "redshift",
                                      region_name, 
                                      it["type"], 
                                      "",
                                      "",
                                      "",
                                      "", 
                                      "", 
                                      "", 
                                      "", 
                                      self.none_as_string(it["price"]), 
                                      ""])
                    
                    print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("ondemand",
                                                                      "redshift",
                                                                      region_name, 
                                                                      it["type"], 
                                                                      "",
                                                                      "",
                                                                      "",
                                                                      "", 
                                                                      "", 
                                                                      "", 
                                                                      "", 
                                                                      self.none_as_string(it["price"]), 
                                                                      "")

            
            
            for r in ec2_data_r["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        for po in it["prices"][term]:
                            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("reserved",
                                                                              "ec2",
                                                                              region_name, 
                                                                              it["type"], 
                                                                              "",
                                                                              "",
                                                                              "",
                                                                              it["os"], 
                                                                              "heavy", 
                                                                              term, 
                                                                              po, 
                                                                              self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                                              self.none_as_string(it["prices"][term][po]["upfront"]))
                            writer.writerow(["reserved",
                                             "ec2",
                                             region_name, 
                                             it["type"], 
                                             "",
                                             "",
                                             "",
                                             it["os"], 
                                             "heavy", 
                                             term, 
                                             po, 
                                             self.none_as_string(it["prices"][term][po]["hourly"]), 
                                             self.none_as_string(it["prices"][term][po]["upfront"])])
            
            for r in elc_data_r["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("reserved",
                                                                          "elasticache",
                                                                          region_name, 
                                                                          it["type"],
                                                                          "",
                                                                          "",
                                                                          "",
                                                                          "", 
                                                                          it["utilization"], 
                                                                          term, 
                                                                          "",
                                                                          self.none_as_string(it["prices"][term]["hourly"]), 
                                                                          self.none_as_string(it["prices"][term]["upfront"]))
                        writer.writerow(["reserved",
                                         "elasticache",
                                         region_name, 
                                         it["type"],
                                         "",
                                         "",
                                         "",
                                         "", 
                                         it["utilization"], 
                                         term,
                                         "", 
                                         self.none_as_string(it["prices"][term]["hourly"]), 
                                         self.none_as_string(it["prices"][term]["upfront"])])
                        
            for r in rds_data_r["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        if "noUpfront" in it["prices"][term] or "partialUpfront" in it["prices"][term] or "allUpfront" in it["prices"][term]:
                            for po in it["prices"][term]:
                                print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ( "reserved",
                                                                                   "rds",
                                                                                   region_name, 
                                                                                   it["type"], 
                                                                                   it["multiaz"], 
                                                                                   it["license"], 
                                                                                   it["db"], 
                                                                                   "", 
                                                                                   it["utilization"], 
                                                                                   term, 
                                                                                   po,
                                                                                   self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                                                   self.none_as_string(it["prices"][term][po]["upfront"]))
                                writer.writerow(["reserved",
                                                 "rds",
                                                 region_name, 
                                                 it["type"], 
                                                 it["multiaz"], 
                                                 it["license"], 
                                                 it["db"],
                                                 "", 
                                                 it["utilization"], 
                                                 term, 
                                                 po,
                                                 self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                 self.none_as_string(it["prices"][term][po]["upfront"])])
                        else:
                            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ( "reserved",
                                                                               "rds",
                                                                               region_name,
                                                                               it["type"],
                                                                               it["multiaz"],
                                                                               it["license"],
                                                                               it["db"],
                                                                               "",
                                                                               it["utilization"],
                                                                               term,
                                                                               "",
                                                                               self.none_as_string(it["prices"][term]["hourly"]),
                                                                               self.none_as_string(it["prices"][term]["upfront"]))
                            writer.writerow(["reserved",
                                             "rds",
                                             region_name,
                                             it["type"],
                                             it["multiaz"],
                                             it["license"],
                                             it["db"],
                                             "",
                                             it["utilization"],
                                             term,
                                             "",
                                             self.none_as_string(it["prices"][term]["hourly"]),
                                             self.none_as_string(it["prices"][term]["upfront"])])
                        
                
            for r in rs_data_r["regions"]:
                region_name = r["region"]
                for it in r["instanceTypes"]:
                    for term in it["prices"]:
                        for po in it["prices"][term]:
                            print "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % ("reserved",
                                                                              "redshift",
                                                                              region_name, 
                                                                              it["type"], 
                                                                              "",
                                                                              "",
                                                                              "",
                                                                              "", 
                                                                              "heavy", 
                                                                              term, 
                                                                              po, 
                                                                              self.none_as_string(it["prices"][term][po]["hourly"]), 
                                                                              self.none_as_string(it["prices"][term][po]["upfront"]))
                            writer.writerow(["reserved",
                                             "redshift",
                                             region_name, 
                                             it["type"], 
                                             "",
                                             "",
                                             "",
                                             "", 
                                             "heavy", 
                                             term, 
                                             po, 
                                             self.none_as_string(it["prices"][term][po]["hourly"]), 
                                             self.none_as_string(it["prices"][term][po]["upfront"])])
    
    
    
