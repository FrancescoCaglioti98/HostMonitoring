Monitoring hosts on a network using Python, PostgreSQL and NCPA.
------------------------------
Required libraries: requests, psycopg2
-


First of all, we need to create an instance in the database, which contains two tables.

  -One for the list of all the IPs to be monitored, with various information
  
  -One for all the checks made on those devices.

--------------------------

Then install the native NCPA agent on the hosts concerned, noting the KEY used and the IP of the machine.

Enter the information in the first table, the one that stores the information about the hosts, and modify the Python file accordingly, changing the "myToken" value to the one chosen and the information for the connection to the Database created, in my case i created a config.ini file to where i parse in all the data i need

At this point, once the program has been started, it should automatically retrieve the information on the IPs entered in the first table and carry out checks on each individual IP entered.


IMPORTANT
---

To ensure that the system allows the saving of an error log I added paths for writing these errors in txt files. Change the path with a link to a folder in the device to make sure this function works properly

There are two in the request phase to the hosts (in the two except blocks)

In addition, for the export phase, make sure you also change the folder indicated in the path, because it is the one where the reports will be saved in CSV divided according to the IP





TO DO:
-
-Add the possibility of making simultaneous calls.
