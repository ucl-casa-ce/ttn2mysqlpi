import time
import ttn
import mysql.connector
from dateutil.parser import parse


app_id = "YOUR_APP_ID"
access_key = "YOUR_AK"

def uplink_callback(msg, client):
  print "Received uplink from: "
  print msg.dev_id
  print msg.app_id
  print msg.payload_fields
  print msg.metadata.time

  dt = parse(msg.metadata.time)
  dt = dt.strftime("%Y-%m-%d  %H:%M:%S")

  print dt

  try:
  	mydb = mysql.connector.connect(
  		host="localhost",
  		user="YOUR_MYSQL_USER",
  		passwd="YOUR_MYSQL_PASSWORD",
  		database="YOUR_MYSQL_DATABASE"
  		)

  	mycursor = mydb.cursor()

  	sql = "INSERT INTO ttn_casaucl_ttnnodes (dev_id, payload_fields, time) VALUES (%s, %s, %s)"
	val = (str(msg.dev_id), str(msg.payload_fields), str(dt))

  	result = mycursor.execute(sql,val)
  	mydb.commit()
  	print "Record inserted:"
  	print mycursor.rowcount

  except mysql.connector.Error as error :
  	mydb.rollback()
  	print("Failed to insert into MySQL table {}".format(error))

  finally:
  	if(mydb.is_connected()):
  		mycursor.close()
  		mydb.close()
  		print("MySQL connection closed")



def connect_callback(res, client):
  print "Connection to broker: "
  print res

def close_callback(res, client):
  print "Trying to reconnect"
  mqtt_client.connect()

# handlerclient class constructor
handler = ttn.HandlerClient(app_id, access_key)
print "Handler initialised"

# using mqtt client create an MQTTClient object
mqtt_client = handler.data()
print "MQTT client object created"

# set a connection callback function when client connects to broker
mqtt_client.set_connect_callback(connect_callback)

# set close_callback so that if connection lost we can reconect
mqtt_client.set_close_callback(close_callback)

# set uplink callback to be executed when message arrives
mqtt_client.set_uplink_callback(uplink_callback)
print "Callbacks assigned"

# connect to the application and listen for messages
mqtt_client.connect()

# keep program running - if connection lost should reconnect
while True:
  pass
