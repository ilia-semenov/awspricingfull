# awspricingfull.py

-------------------------------------

**MAJOR UPDATE 06/19/2015: Version 2.0 of program**

* New RDS pricing scheme is added (noUpfront, partialUpfront, allUpfront)
* Thorough testing is performed and major bugs fixed:
  * Redshift "clean" hourly price calculation (from monthly cost) is corrected following AWS correcting it on their pricing website
  * Output pricing is checked by random sampling and proven to be accurate
  * PrettyTable representation is now fully functional
  * JSON functionality now returns the JSON string instead of just printing it to console
  * Documentation is accurate and informative

**Program is fully functional and up-to-date.**

-------------------------------------


http://ilia-semenov.github.io/awspricingfull

Written by Ilia Semenov (@ilia-semenov)

Based on the project by Eran Sandler (@erans): https://github.com/erans/ec2instancespricing

AWS instance pricing retrieval for EC2, RDS, ElastiCache and Redshift. On-Demand and Reserved pricing schemes covered both for previous and current generation instance types. Contains the most recent updates (new EC2 Reservation pricing scheme, D2 instances and more).

Module is designed to retrieve the AWS prices for 
four major AWS services that have reserved instances involved: EC2, ElastiCache, 
RDS and Redshift. The prices either On-Demand or Reserved (specified by user) can 
be retrieved to Command Line in JSON, Table (Prettytable) or CSV formats. CSV format 
option also saves the csv file to the folder specified by user, which is the main 
use case.

The module also contains the class which consolidates all the pricing data into a single structured JSON, Table or CSV output: all 4 services, reserved and On-Demand.

The undocumented AWS pricing APIs are used as the sources. The same APIs  serve
the data to the AWS pricing pages.

Both current and previous generation instance prices are retrieved.


More information and description of classes contained in the module can be found in Sphinx documentation HTML located at https://github.com/ilia-semenov/awspricingfull/blob/master/docs/_build/html/ folder.

