Monitoring hosts on a network using Python, PostgreSQL and NCPA.


Required libraries: requests, psycopg2

First of all, we need to create an instance in the database, which contains two tables.
  -One for the list of all the IPs to be monitored, with various information
  -One for all the checks made on those devices.

Then install the native NCPA agent on the hosts concerned, noting the KEY used and the IP of the machine.

Enter the information in the first table and modify the Python file accordingly, changing the "myToken" value to the one chosen and the information for the connection to the Database created.

At this point, once the program has been started, it should automatically retrieve the information on the IPs entered in the first table and carry out checks on each individual IP entered.


TO DO:
-Add the possibility of making simultaneous calls.
-Add the possibility of automatic checks on the expiry of a TimeOut.
-Improve the part relating to the management of errors in calls.
