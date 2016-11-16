'''
Simple main routine for `awspricingfull` module.

Call the class corresponding to your needs (EC2Prices(), RDSPrices(), etc.), 
and use any method with parameters needed. See the awspricingfull documentation for reference.

In a nutshell: To save CSV use save_csv method for instance of any of the functional classes 
(EC2Prices() - EC2, RDSPrices() - RDS, ELCPrices() - ElastiCache, RSPrices() - Redshift, DDBPrices() - DynamoDB). 
With save_csv use "reserved" or "ondemand" as first parameter, your path as second (home 
dir by default) and file name as third (conventional default). Also, to save prices for all 
the products use AllAWSPrices() class and same save_csv method with small difference - you 
can set the first parameter to "all" which will return all the pricing (reserved and on-demand 
for all the services).

Method print_table is available for EC2Prices(), RDSPrices(), ELCPrices(), RSPrices(), DDBPrices(). It outputs 
the pricing in a table format to console. Prettytable library is required. Method takes only one parameter:
"reserved" or "ondemand". Not available for AllAWSPrices().

Method print_json is available for all classes. It returns the pricing in a JSON format 
and does not output it to console. Method takes only one parameter: "reserved" or "ondemand" 
and additional "all" for AllAWSPrices().

Created: Mar 26, 2015

Updated: Nov 16, 2016

@author: Ilia Semenov

@version: 3.1
'''
import awspricingfull


if __name__ == '__main__':
    
    '''
    1. Create 1nstance of the class needed: EC2Prices() - EC2, RDSPrices() - RDS, 
    ELCPrices() - ElastiCache, RSPrices() - Redshift, DDBPrices - DynamoDB, AllAWSPrices() - full pricing.
    2. Run the method needed: return_json, print_table, save_csv.
    '''
    
    '''
    FULL PRICING
    '''
    
    allpricing=awspricingfull.AllAWSPrices2() #Full Pricing class instance
    
    #print (allpricing.return_json("ondemand")) #JSON - On-Demand Pricing: All Services
    #print (allpricing.return_json("reserved"))  #JSON - Reserved Pricing: All Services
    #print (allpricing.return_json("all")) #JSON - Full Pricing: All Services
    #allpricing.save_csv("ondemand") #CSV - On-Demand Pricing: All Services
    #allpricing.save_csv("reserved") #CSV - Reserved Pricing: All Services
    allpricing.save_csv("all") #CSV - Full Pricing: All Services
    
    '''
    EC2
    '''
    #ec2pricing=awspricingfull.EC2Prices() #EC2 Pricing class instance         
    
    #print (ec2pricing.return_json("ondemand")) #JSON - On-Demand Pricing: EC2
    #print (ec2pricing.return_json("reserved")) #JSON - Reserved Pricing: EC2
    #ec2pricing.print_table("ondemand") #PrettyTable - On-Demand Pricing: EC2
    #ec2pricing.print_table("reserved") #PrettyTable - Reserved Pricing: EC2
    #ec2pricing.save_csv("ondemand") #CSV - On-Demand Pricing: EC2
    #ec2pricing.save_csv("reserved") #CSV - Reserved Pricing: EC2

    '''
    RDS
    '''
    #rdspricing=awspricingfull.RDSPrices() #RDS Pricing class instance         
    
    #print (rdspricing.return_json("ondemand")) #JSON - On-Demand Pricing: RDS
    #print (rdspricing.return_json("reserved")) #JSON - Reserved Pricing: RDS
    #rdspricing.print_table("ondemand") #PrettyTable - On-Demand Pricing: RDS
    #rdspricing.print_table("reserved") #PrettyTable - Reserved Pricing: RDS
    #rdspricing.save_csv("ondemand") #CSV - On-Demand Pricing: RDS
    #rdspricing.save_csv("reserved") #CSV - Reserved Pricing: RDS

    '''
    ELASTICACHE
    '''
    #elcpricing=awspricingfull.ELCPrices() #ElastiCache Pricing class instance         
    
    #print (elcpricing.return_json("ondemand")) #JSON - On-Demand Pricing: ElastiCache
    #print (elcpricing.return_json("reserved")) #JSON - Reserved Pricing: ElastiCache
    #elcpricing.print_table("ondemand") #PrettyTable - On-Demand Pricing: ElastiCache
    #elcpricing.print_table("reserved") #PrettyTable - Reserved Pricing: ElastiCache
    #elcpricing.save_csv("ondemand") #CSV - On-Demand Pricing: ElastiCache
    #elcpricing.save_csv("reserved") #CSV - Reserved Pricing: ElastiCache

    '''
    REDSHIFT
    '''    
    #rspricing=awspricingfull.RSPrices() #Redshift Pricing class instance         
    
    #print (rspricing.return_json("ondemand")) #JSON - On-Demand Pricing: Redshift
    #print (rspricing.return_json("reserved")) #JSON - Reserved Pricing: Redshift
    #rspricing.print_table("ondemand") #PrettyTable - On-Demand Pricing: Redshift
    #rspricing.print_table("reserved") #PrettyTable - Reserved Pricing: Redshift
    #rspricing.save_csv("ondemand") #CSV - On-Demand Pricing: Redshift
    #rspricing.save_csv("reserved") #CSV - Reserved Pricing: Redshift

    '''
    DYNAMODB
    '''    
    #ddbpricing=awspricingfull.DDBPrices() #DynamoDB Pricing class instance         
    
    #print (ddbpricing.return_json("ondemand")) #JSON - On-Demand Pricing: DynamoDB
    #print (ddbpricing.return_json("reserved")) #JSON - Reserved Pricing: DynamoDB
    #ddbpricing.print_table("ondemand") #PrettyTable - On-Demand Pricing: DynamoDB
    #ddbpricing.print_table("reserved") #PrettyTable - Reserved Pricing: DynamoDB
    #ddbpricing.save_csv("ondemand") #CSV - On-Demand Pricing: DynamoDB
    #ddbpricing.save_csv("reserved") #CSV - Reserved Pricing: DynamoDB    

