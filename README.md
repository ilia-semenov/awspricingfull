# awspricingfull.py
Written by Ilia Semenov (@ilia-semenov)

Based on the project by Eran Sandler (@erans): https://github.com/erans/ec2instancespricing

AWS instance pricing retrieval for EC2, RDS, ElastiCache and Redshift. On-Demand and Reserved pricing schemes covered both for previous and current generation instance types.

Module is designed to retrieve the AWS prices for 
four major AWS services that have reserved instances involved: EC2, ElastiCache, 
RDS and Redshift. The prices either On-Demand or Reserved (specified by user) can 
be retrieved to Command Line in JSON, Table (Prettytable) or CSV formats. CSV format 
option also saves the csv file to the folder specified by user, which is the main 
use case.
The undocumented AWS pricing APIa are used as the sources. The same APIs  serve
the data to the AWS pricing pages.
Both current and previous generation instance prices are retrieved.

More information and description of classes contained in the module can be found in Sphinx documentation HTML: http://htmlpreview.github.io/?https://github.com/ilia-semenov/awspricingfull/blob/master/docs/_build/html/index.html
(the documentation from repository shown via http://htmlpreview.github.io/ tool).
