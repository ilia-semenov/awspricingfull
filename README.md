# awspricingfull.py

------------------------------------------

**MINOR UPDATE 03/24/2016 AND FUTURE DEVELOPMENT ROADMAP**

**Update**

* Seoul region (ap-northeast-2) is added to dictionaries
* Tool is tested to produce accurate up-to-date results

**Roadmap**

As there had been no AWS updates affecting pricing sheets since June 2015, I stopped the active development of the script and was just checking it from time to time. Moreover, **in December 2015 AWS introduced their own pricing API** which was a great thing.
However, yesterday I had to update my work-related DBs with the new Seoul region pricing, and found out that AWS API implementation is not straightforward:

* Every region should be accessed separately
* Parsing needed
* Overall, major development effort is neded to use the API

That is why I came back to my good old tool, added Seoul region into it, and found out that it still produces the top-notch results that I was able to use right away. At the sam=e time I decided to continue the development of the tool, and here is the roadmap for the nearest time:

* DynamoDB pricing - OD and Reservations
* Dictionary dependency fix - make the tool tolerate AWS changes (such as new regions introductions)

**Please, let me know what else would be good to have in the resulting uniform output of the tool.**


**P.S. Program is fully functional and up-to-date.**


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

Compatibility: Python 2

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


More information and description of classes contained in the module can be found in Sphinx documentation HTML located at https://github.com/ilia-semenov/awspricingfull/tree/master/docs_html folder.

