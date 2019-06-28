# ttn2mysqlpi - RPi build for logging data from TTN
Set-up to configure a RPi 3b as parser from TTN GW to MySQL data store on RPi. As a starting point this example assumes you have:
* A vanilla RPi kit with Raspbian installed
* A TTN application set-up which is collecting data

It assumes that you have bunch of nodes pushing data through a gateway to thethingsnetwork. The focus of thus demo is on confuguring the RPi depicted in diagram below.
<img src="https://github.com/ucl-casa-ce/ttn2mysqlpi/blob/master/ttn.jpeg?raw=true" alt="TTN 2 RPI network" width="100%"/>

## Getting Started

First step is to setup the RPI. Plug in monitor keyboard mouse and boot up. Open terminal and check which version of OS installed:

```
cat /etc/os-release
```

The version used to create this example was built on Raspbian GNU/Linux 9 (stretch). Next set basic configuration settings

```
sudo raspi-config
```

From the menu select items: 1. set password, 2. configure wifi if using access point, 5. interfacing select SSH on (Note, I am just using basic password for security and am using default pi user)

I also changed the hostname since there are a few RPi’s on same network so this is good to do! I changed it to something identifiable - I used *cetoolspi90tcr* - edit the follwoing two files using nano or similar.

```
sudo nano /etc/hostname
sudo nano /etc/hosts
```

This creates a basic RPi setup on the network with ssh access either via ethernet or wifi. From terminal or putty you should be able to ssh in with this pattern:

```
ssh pi@cetoolspi90tcr.local
```

## Setting up MySQL / MariaDB

Next step is to set-up the MySQL/ MariaDB environment to connect to TTN and store the data. First check for any updates:

```
sudo apt-get update 
sudo apt-get upgrade
```

Install MariaDB (MySQL replacement) using the notes below based on the detailed instructions [at this guide](https://r00t4bl3.com/post/how-to-install-mysql-mariadb-server-on-raspberry-pi "how to install mysql on rpi")

```
sudo apt-get install mysql-server
sudo mysql_secure_installation
```
For latter I entered: no password, Y - cetools2019, Y, Y, Y, Y

Check that you server works and make a note of the credentials you just created.

```
sudo mysql -u root -p
```

The next step is to setup the mysql user and database for the TTN application - NOTE: define own database name, user and pass but don’t change the table name or structure if you want to use the example python script used in this demo. From the MySQL command prompt:

```
CREATE DATABASE ttnenviro90tcr;
CREATE USER ttn@localhost IDENTIFIED BY 'ttn2019’;
GRANT ALL PRIVILEGES ON ttnenviro90tcr.* TO ttn@localhost;
USE ttnenviro90tcr;
CREATE TABLE ttn_casaucl_ttnnodes (id INT AUTO_INCREMENT PRIMARY KEY, dev_id VARCHAR(255), payload_fields TEXT, time DATETIME);
SHOW COLUMNS FROM ttn_casaucl_enviro90tcr;
SELECT * FROM ttn_casaucl_enviro90tcr;
exit
```

## Setting up python environment to run script to push data into DB

Raspbian Stretch runs Python 2.7.3 by default - that is what this example is based on. From the command prompt install the libraries used by the python script and copy it onto the RPi:

```
python -m pip install mysql-connector
pip install python-dateutil 
pip install ttn
mkdir scripts
cd scripts
wget https://raw.githubusercontent.com/ucl-casa-ce/ttn2mysqlpi/master/ttn2mysql.py?token=AABDOUGDEGP23QMPMSHQJQK5D45DC
mv ttn2mysql.py\?token\=AABDOUGDEGP23QMPMSHQJQK5D45DC ttn2mysql.py
```

The next stage is configuring the script to parse data from your application on TTN. Open your [TTN Console](https://console.thethingsnetwork.org/applications "the things network") and browse to your applications page, select the app that you are using to get access to keys etc and edit the ttn2mysql.py file as follows:

```
nano ttn2mysql.py
```

Update the app_id, access_key and DB settings. Then test the script: 

```
python ttn2mysql.py
```

After initial connection you then should see data coming through (in my case in 5 minute intervals, so had to wait a while…) Once you see some data coming in you can CTRL+C to exit the script and then log back into MySQL DB to see if data is being stored as anticipated:

```
sudo mysql -u root -p
```

```
USE ttnenviro90tcr;
SELECT * FROM ttn_casaucl_enviro90tcr;
exit
```

## Automating to restart at bootup
The final step is to add the script into the reboot process. Simplest way to do this is using crontab. 

```
crontab -e
```

Then add the following line to the bottom of the file. Make sure to add line return at end of line so there is a blank line at end of file. Note: had to include a sleep function to delay start of script to after network connections are established other wise script fails (The python script being run should really be checking for network connection before trying to connect).

```
@reboot /bin/sleep 60 ; python /home/pi/scripts/ttn2mysql.py >  /home/pi/scripts/ttn2mysql.log 2>&1 &
```

Reboot the RPi to make sure the job runs automatically. You can check this by running (you should see 2 entries - one for this query and one for the actual job):

```
ps aux | grep /home/pi/scripts/ttn2mysql.py
```

All done. 
