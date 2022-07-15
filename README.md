# Wifi-Bezel Emulator

## Description

The Wifi-Bezel Emulator allows a user to partially emulate Wifi-Bezel functionality for testing purposes.
It is designed to listen for and respond to incoming events as they are published to an MQTT broker.
The WBE will build and publish responses based on the contents of an incoming payload.

Its current implementation allows for the processing of CONTROL events, namely the handling
of a BLINK_REQUEST payload. WORKFLOW events will be
implemented at a later date. 

## Dependencies
* **WSL2/Ubuntu 20.04.4 LTS (Focal Fossa)/Ubuntu 18.04 LTS (Bionic)**
* **Python 3.10.2+**
* **git**

## Installation

### Recommended Prerequisites
This application was developed using **WSL2** with **Ubuntu 20.04 LTS (Focal Fossa)**, but will
also run in native **Ubuntu 20.04 LTS (Focal Fossa)** as well as **native Ubuntu 18.04 LTS (Bionic)**

For complete installation and configuration of WSL2, please review the following documentation.

* Official windows [documentation](https://docs.microsoft.com/en-us/windows/wsl/install) for installing WSL2.


**Installation with install.sh**

Clone into the repository, and navigate to the project directory.
```
git clone http://sckgit.fastinc.com/wi-fi-bezel/emulator.git
cd emulator
```
Run **install.sh**.

```
chmod 755 install.sh
./install.sh
```
You will be prompted for an administrator password.
```
user@ubuntu:~/Repos/emulator$ ./install.sh
UNIX Password: 
```
Once the installation script has run, activate the newly created virtual environment.
```
source venv/bin/activate
```

### Usage - Blink Request

Running the application with the **--help** || **-h** switch will show the following:

```
user@ubuntu:$ python main.py -h

                        ___________              
                __  _  _\_   _____/ _____  __ __ 
                \ \/ \/ /|    __)_ /     \|  |  \
                 \     / |        \  Y Y  \  |  /
                  \/\_/ /_______  /__|_|  /____/ 
                                \/      \/       
                                                 
                     | Wifi-Bezel Emulator |     

usage: main.py [-h] [--default-config DEFAULT_CONFIG] [--blink-config BLINK_CONFIG] [--cook-config COOK_CONFIG] [--show-config SHOW_CONFIG] [--heart-beat-interval HEART_BEAT_INTERVAL] --mqtt-broker MQTT_BROKER --mqtt-port MQTT_PORT --mqtt-control-subscribe-topic MQTT_CONTROL_SUBSCRIBE_TOPIC
               --mqtt-control-publish-topic MQTT_CONTROL_PUBLISH_TOPIC --mqtt-workflow-subscribe-topic MQTT_WORKFLOW_SUBSCRIBE_TOPIC --mqtt-workflow-publish-topic MQTT_WORKFLOW_PUBLISH_TOPIC --mqtt-monitor-publish-topic MQTT_MONITOR_PUBLISH_TOPIC --mode MODE [--blink-ack BLINK_ACK]
               [--blink-success BLINK_SUCCESS] [--blink-fail BLINK_FAIL] [--cook-start COOK_START] [--cook-quantity COOK_QUANTITY] [--cook-complete COOK_COMPLETE] [--cook-cancel COOK_CANCEL] [--cook-complete-ack COOK_COMPLETE_ACK] [--recipe-instance-id RECIPE_INSTANCE_ID] [--recipe-name RECIPE_NAME]
               [--remaining-time REMAINING_TIME] [--product-quantity PRODUCT_QUANTITY] [--flow FLOW] [--bezel-mac BEZEL_MAC] [--dest-mac DEST_MAC] [--retry-interval RETRY_INTERVAL] [--loop-interval LOOP_INTERVAL] [--loop LOOP]

options:
  -h, --help            show this help message and exit
  --default-config DEFAULT_CONFIG
                        Default config file (default: config/defaults.ini)
  --blink-config BLINK_CONFIG
                        Blink request config file (optional). (default: config/blink-defaults.ini)
  --cook-config COOK_CONFIG
                        Cook flow config file (optional). (default: config/cook-defaults.ini)
  --show-config SHOW_CONFIG
                        Shows the current configuration if set to True. (default: False)
  --heart-beat-interval HEART_BEAT_INTERVAL
                        The interval in seconds at which the emulator will send a HEARTBEAT event to maintainits connection to mqtt (default: 900)
  --mqtt-broker MQTT_BROKER
                        Target MQTT broker IP. (default: 127.0.0.1)
  --mqtt-port MQTT_PORT
                        Target MQTT broker port. (default: 1883)
  --mqtt-control-subscribe-topic MQTT_CONTROL_SUBSCRIBE_TOPIC
                        MQTT Fire and Forget (F&F) subscription topic. (default: /iot/device/control)
  --mqtt-control-publish-topic MQTT_CONTROL_PUBLISH_TOPIC
                        MQTT Fire and Forget (F&F) publish topic. (default: /iot/client/control)
  --mqtt-workflow-subscribe-topic MQTT_WORKFLOW_SUBSCRIBE_TOPIC
                        MQTT Workflow subscription topic. (default: /iot/device/workflow)
  --mqtt-workflow-publish-topic MQTT_WORKFLOW_PUBLISH_TOPIC
                        MQTT Workflow publish topic. (default: /iot/client/workflow)
  --mqtt-monitor-publish-topic MQTT_MONITOR_PUBLISH_TOPIC
                        MQTT Monitor publish topic. (default: /iot/client/monitor)
  --mode MODE           Emulation mode blink | cook. (default: blink)
  --blink-ack BLINK_ACK
                        Number of blink ack payloads to send. MIN: 0 MAX: 3 (default: 1)
  --blink-success BLINK_SUCCESS
                        Number of blink success payloads to send. MIN: 0 MAX: 3 (default: 1)
  --blink-fail BLINK_FAIL
                        Number of blink fail payloads to send. MIN: 0 MAX: 3 (default: 0)
  --cook-start COOK_START
                        Number of cook start payloads to send. MIN: 0 MAX: 3 (default: 1)
  --cook-quantity COOK_QUANTITY
                        Number of cook quantity payloads to send. MIN: 0 MAX: 3 (default: 1)
  --cook-complete COOK_COMPLETE
                        Number of cook complete payloads to send. MIN: 0 MAX: 3 (default: 1)
  --cook-cancel COOK_CANCEL
                        Number of cook cancel payloads to send. MIN: 0 MAX: 3 (default: 0)
  --cook-complete-ack COOK_COMPLETE_ACK
                        Number of cook complete ack payloads to send. MIN: 0 MAX: 3 (default: 1)
  --recipe-instance-id RECIPE_INSTANCE_ID
                        The recipe instance identifier. (default: 1)
  --recipe-name RECIPE_NAME
                        The recipe name. (default: OR Chicken)
  --remaining-time REMAINING_TIME
                        The cook time for the current recipe. (default: 5)
  --product-quantity PRODUCT_QUANTITY
                        The product quantity to be cooked. (default: 1)
  --flow FLOW           The sequence of cook events to send to MQTT in any order separated by a pipe "|" character.Valid input events: 1. cook_start 2. cook_quantity 3.cook_complete 4. cook_cancel 5. cook_complete_ack (default: "cook_start | cook_quantity | cook_complete | cook_complete_ack")
  --bezel-mac BEZEL_MAC
                        Bezel mac address- will be generated randomly if not provided. (default: 5E:0E:53:4F:51:56)
  --dest-mac DEST_MAC   Destination mac address- will be generated randomly if not provided. (default: 33:09:02:73:89:33)
  --retry-interval RETRY_INTERVAL
                        Interval between sent response payloads within each iteration. Cannot be less than 0 (default: 1)
  --loop-interval LOOP_INTERVAL
                        The period of time between loop iterations. Cannot be less than 0 (default: 1)
  --loop LOOP           How many times to run the given process. Cannot be less than 0 (default: 1)

Args that start with '--' (eg. --show-config) can also be set in a config file (specified via --default-config or --blink-config or --cook-config). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). If an arg is specified in more than one place,   
then commandline values override config file values which override defaults.
```

The above arguments may be passed as command line parameters or 
read from within a configuration file. Please ensure a functioning **MQTT broker** is online and correctly configured. The IP address 
of this machine must be specified, along with the emulator's MAC address, or
the application will default to **localhost (127.0.0.1)** and a randomly generated MAC.

```
user@ubuntu:$ python main.py --mqtt-broker <ip address> --bezel-mac 11:22:33:44:55:66
```

###Showing the current configuration
You may provide the **--show-config** to view the application's configuration values at startup by setting it
to **True**, e.g.:

```
user@ubuntu:$ python main.py --mqtt-broker <ip address> --bezel-mac 11:22:33:44:55:66 --show-config True


                        ___________              
                __  _  _\_   _____/ _____  __ __ 
                \ \/ \/ /|    __)_ /     \|  |  \
                 \     / |        \  Y Y  \  |  /
                  \/\_/ /_______  /__|_|  /____/ 
                                \/      \/       
                                                 
                     | Wifi-Bezel Emulator |     

337 - 05-23-2022-12:28:52 - INFO: Configuration: {
    "default_config": "config/defaults.ini",      
    "blink_config": "config/blink-defaults.ini",  
    "cook_config": "config/cook-defaults.ini",    
    "show_config": true,                          
    "heart_beat_interval": -5,                    
    "mqtt_broker": "10.0.0.108",
    "mqtt_port": 1883,
    "mqtt_control_subscribe_topic": "/iot/device/control",
    "mqtt_control_publish_topic": "/iot/client/control",
    "mqtt_workflow_subscribe_topic": "/iot/device/workflow",
    "mqtt_workflow_publish_topic": "/iot/client/workflow",
    "mqtt_monitor_publish_topic": "/iot/client/monitor",
    "mode": "blink",
    "blink_ack": 1,
    "blink_success": 1,
    "blink_fail": 0,
    "cook_start": 1,
    "cook_quantity": 1,
    "cook_complete": 1,
    "cook_cancel": 0,
    "cook_complete_ack": 1,
    "recipe_instance_id": 0,
    "recipe_name": "OR Chicken",
    "remaining_time": 10,
    "product_quantity": 1,
    "flow": "cook_start | cook_quantity | cook_complete | cook_complete_ack",
    "bezel_mac": "11:22:33:44:55:66",
    "dest_mac": "86:31:5B:7B:7C:7C",
    "retry_interval": 2,
    "loop_interval": 3,
    "loop": 1
}
337 - 05-23-2022-12:28:52 - INFO: Starting Wi-fi Bezel Emulator | Version: 4.2.12 | API Version: 3.2.0
337 - 05-23-2022-12:28:52 - INFO: Bezel MAC Address: 11:22:33:44:55:66
```


###Using the configuration file
Navigate to the **config/** directory and create a file called **defaults.ini**.
Populate it with the following parameters, replacing the values within **<>** with your own.

```
mqtt-broker=<str: xxx.xxx.xxx.xxx>
mqtt-port=<int: xxxx>
mode=<str: blink | cook>
mqtt-control-subscribe-topic=/iot/device/control
mqtt-control-publish-topic=/iot/client/control
mqtt-workflow-subscribe-topic=/iot/device/workflow
mqtt-workflow-publish-topic=/iot/client/workflow
mqtt-monitor-publish-topic=/iot/client/monitor
retry-interval=<int>
loop-interval=<int>
loop=<int>
```

This will serve as the default configuration file, and must be present within the **config/**
directory in order to be read. A secondary configuration file,
which will override the defaults for **blink-ack**, **blink-success** and **blink-fail** can also be provided,
and can be passed using the optional **--blink-config** switch when running
the application. An example of the contents of this file can be seen below:

```
blink-ack=<int [0-3]>
blink-success=<int [0-3]>
blink-fail=<int [0-3]>
```

**Note**: defining these values as commandline parameters will override the values set in all
configuration files.

###Running the application

**Example 1**: Basic usage with a configuration file

```
python main.py
```

On startup, the application will create a client instance.
Note that the **Bezel MAC Address** will be displayed in the initial output. Any payloads intended for this
instance must have the **payload['header']['destination']** attributes
set to this address, or they will be ignored. This address can be configured within the **configuration file**
or passed to the application using the **--bezel-mac** command-line argument.

Note that the Wi-Fi Bezel Emulator will send a single HEARTBEAT event at startup. This payload posts to the
**/iot/client/monitor** topic, and post again every 15 minutes (900s) by default. This value may be changed by
additionally providing the **--heart-beat-interval** parameter and setting it to a value greater than 0 (x > 0).

```
(venv) user@ubuntu:$ python main.py --bezel-mac 11:22:33:44:55:66 --mqtt-broker 10.0.0.108 --mode blink --heart-beat-interval 5

                        ___________              
                __  _  _\_   _____/ _____  __ __ 
                \ \/ \/ /|    __)_ /     \|  |  \
                 \     / |        \  Y Y  \  |  /
                  \/\_/ /_______  /__|_|  /____/ 
                                \/      \/       
                                                 
                     | Wifi-Bezel Emulator |     

349 - 05-23-2022-12:35:10 - INFO: Configuration: {          
    "default_config": "config/defaults.ini",                
    "blink_config": "config/blink-defaults.ini",            
    "cook_config": "config/cook-defaults.ini",              
    "show_config": true,                                    
    "heart_beat_interval": 900,                             
    "mqtt_broker": "10.0.0.108",                            
    "mqtt_port": 1883,                                      
    "mqtt_control_subscribe_topic": "/iot/device/control",  
    "mqtt_control_publish_topic": "/iot/client/control",    
    "mqtt_workflow_subscribe_topic": "/iot/device/workflow",
    "mqtt_workflow_publish_topic": "/iot/client/workflow",  
    "mqtt_monitor_publish_topic": "/iot/client/monitor",    
    "mode": "blink",                                        
    "blink_ack": 1,                                         
    "blink_success": 1,                                     
    "blink_fail": 0,                                        
    "cook_start": 1,                                        
    "cook_quantity": 1,                                     
    "cook_complete": 1,                                     
349 - 05-23-2022-12:35:10 - INFO: Payload content:
{
    "header": {
        "versionInfo": {
            "api": "3.2.0",
            "applianceType": "Emulator",
            "applianceSpec": "4.2.12"
        },
        "equipmentInfo": {
            "type": "FRYER"
        },
        "guid": "0420b306-9713-4e44-0cb2-acbd1143adb7",
        "destination": "0",
        "source": "11:22:33:44:55:66",
        "correlationId": "0420b306-9713-4e44-0cb2-acbd1143adb7",
        "type": "HEARTBEAT",
        "dateTime": "2022-05-23T12:35:10-0400"
    }
}
349 - 05-23-2022-12:35:10 - INFO: Connected to MQTT Broker.
349 - 05-23-2022-12:35:10 - INFO: Ready.

```

**Note** that the **--mode** flag was passed in the above example. This is not necessary as the default for mode is "blink",
but must be passed as "cook" when running the cook cycle.

The emulator will remain on standby until a **blink request** addressed to it
is published to the target MQTT Broker:

```
13488 - 03-09-2022-12:39:43 - INFO: Incoming payload validated.
13488 - 03-09-2022-12:39:43 - INFO: Blink attributes validated.
13488 - 03-09-2022-12:39:43 - INFO: Received BLINK_REQUEST:
13488 - 03-09-2022-12:39:43 - INFO: bezel (11:22:33:44:55:66) <-|BLINK_REQUEST|<- api (82:56:30:16:84:66)
13488 - 03-09-2022-12:39:43 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: e6687d1997f24411a34979b30c7d47f1
13488 - 03-09-2022-12:39:43 - INFO: Initializing loop 1.
13488 - 03-09-2022-12:39:43 - INFO: Sending BLINK_ACK | Loop: 1:
13488 - 03-09-2022-12:39:43 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_ACK|-> api (82:56:30:16:84:66)
13488 - 03-09-2022-12:39:43 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: 3101cccf-dfaa-4118-9014-a6e0983aaa6a
13488 - 03-09-2022-12:39:44 - INFO: Sending BLINK_SUCCESS | Loop: 1:
13488 - 03-09-2022-12:39:44 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_SUCCESS|-> api (82:56:30:16:84:66)
13488 - 03-09-2022-12:39:44 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: c6b753c7-3c6a-46f0-a964-ff7c1cd6cd98
13488 - 03-09-2022-12:39:45 - INFO: Sending BLINK_FAIL | Loop: 1:
13488 - 03-09-2022-12:39:45 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_FAIL|-> api (82:56:30:16:84:66)
13488 - 03-09-2022-12:39:45 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: 2654ea1e-a14e-4ef5-92b8-90dfd1033172
13488 - 03-09-2022-12:39:47 - INFO: Initializing loop 2.
13488 - 03-09-2022-12:39:47 - INFO: Sending BLINK_ACK | Loop: 2:
13488 - 03-09-2022-12:39:47 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_ACK|-> api (82:56:30:16:84:66)
13488 - 03-09-2022-12:39:47 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: cdd9f4b5-83f9-4ce7-bd91-e65fe19b634f
13488 - 03-09-2022-12:39:49 - INFO: Sending BLINK_SUCCESS | Loop: 2:
13488 - 03-09-2022-12:39:49 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_SUCCESS|-> api (82:56:30:16:84:66)
13488 - 03-09-2022-12:39:49 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: ae084d38-8c4d-4b4f-808d-11eda5b592af
13488 - 03-09-2022-12:39:50 - INFO: Sending BLINK_FAIL | Loop: 2:
13488 - 03-09-2022-12:39:50 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_FAIL|-> api (82:56:30:16:84:66)
13488 - 03-09-2022-12:39:50 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: 4db213b7-2f81-446c-9f47-ab5e65c8b3fe

```

The application will accept and parse the blink request 
and send any number of **BLINK_ACK, BLINK_SUCCESS and BLINK_FAIL** payloads based on the quantities
delineated within the configuration
file(s) and/or command line parameters. It will repeat any number of iterations delineated within the **loop** parameter
at an interval set within the **loop-interval** parameter in seconds.

**Example 2**: Using the **blink config** configuration file.

Create a file in the **config/** directory, and call it whatever you wish, 
but be sure to give it a **.ini** file extension and populate it with the
following:

```
blink-ack=1
blink-success=1
blink-fail=1
```

**Note** that the value for these parameters cannot be **less than 0** or **greater than 3**.

Run the application using the **--blink-config** switch, passing it the path of the file:
```
python main.py --blink-config ./config/<config-file-name>.ini
```

The application will send the desired number of payloads to the MQTT broker upon receiving a 
**blink request** payload:
```
(venv) user@Ubuntu:$ python main.py --blink-config ./config/blink.ini

...
3928 - 04-07-2022-12:00:20 - INFO: Incoming payload validated.
3928 - 04-07-2022-12:00:20 - INFO: Blink attributes validated.
3928 - 04-07-2022-12:00:20 - INFO: Received BLINK_REQUEST:
3928 - 04-07-2022-12:00:20 - INFO: bezel (11:22:33:44:55:66) <-|BLINK_REQUEST|<- mqtt (82:56:30:16:84:66)
3928 - 04-07-2022-12:00:20 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: e6687d1997f24411a34979b30c7d47f1
3928 - 04-07-2022-12:00:20 - INFO: Initializing loop 1.
3928 - 04-07-2022-12:00:20 - INFO: Sending BLINK_ACK | Loop: 1:
3928 - 04-07-2022-12:00:20 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_ACK|-> mqtt (82:56:30:16:84:66)
3928 - 04-07-2022-12:00:20 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: d36b9834-b68b-11ec-93b9-00155db1dd6d
3928 - 04-07-2022-12:00:20 - INFO: Blink Time: 5
3928 - 04-07-2022-12:00:25 - INFO: Sending BLINK_SUCCESS | Loop: 1:
3928 - 04-07-2022-12:00:25 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_SUCCESS|-> mqtt (82:56:30:16:84:66)
3928 - 04-07-2022-12:00:25 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: d36b9d8e-b68b-11ec-93b9-00155db1dd6d
3928 - 04-07-2022-12:00:25 - INFO: Loop Interval: 5s
3928 - 04-07-2022-12:00:30 - INFO: Initializing loop 2.
3928 - 04-07-2022-12:00:30 - INFO: Sending BLINK_ACK | Loop: 2:
3928 - 04-07-2022-12:00:30 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_ACK|-> mqtt (82:56:30:16:84:66)
3928 - 04-07-2022-12:00:30 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: d98bfb46-b68b-11ec-93b9-00155db1dd6d
3928 - 04-07-2022-12:00:31 - INFO: Blink Time: 5
3928 - 04-07-2022-12:00:36 - INFO: Sending BLINK_SUCCESS | Loop: 2:
3928 - 04-07-2022-12:00:36 - INFO: bezel (11:22:33:44:55:66) ->|BLINK_SUCCESS|-> mqtt (82:56:30:16:84:66)
3928 - 04-07-2022-12:00:36 - INFO: cid: e6687d1997f24411a34979b30c7d47f1 | guid: d98c0e2e-b68b-11ec-93b9-00155db1dd6d
3928 - 04-07-2022-12:00:36 - INFO: Ready.

```

**Example 3**: Passing arguments as command line parameters:

You may manually specify any number of arguments when running the application.


```
python main.py --blink-ack 1 --blink-success 1 --blink-fail 1 --retry-interval 2 --loop 3 --loop-interval 5
```

This will send **1 BLINK_ACK**, **1 BLINK_SUCCESS** and **1 BLINK_FAIL** **3 times**, **waiting 2 seconds** between each publish and waiting
an additional **5 seconds between** each **loop**.

### Usage - Cook Cycle

Running the cook cycle bares close resemblance to running the blink flow. The difference here will be that the cook cycle
will actually initiate a dialogue instead of listening for incoming payloads. That is not to say that it will not register responses
to the sent payloads in the form of **ACK**.

Example usage with default parameters is as follows:

```
python main.py --bezel-mac 11:22:33:44:55:66 --mqtt-broker 10.0.0.108 --mode cook
```

This will initiate a cook cycle, sending the events delineated in the **flow** parameter.

```
3932 - 04-07-2022-12:29:31 - INFO: Starting Wi-fi Bezel Emulator | Version: 3.0.2.
3932 - 04-07-2022-12:29:31 - INFO: Bezel MAC Address: 11:22:33:44:55:66
3932 - 04-07-2022-12:29:31 - INFO: Validating flow.
3932 - 04-07-2022-12:29:31 - INFO: Flow string validated.
3932 - 04-07-2022-12:29:31 - INFO: Total payloads to send: 16
3932 - 04-07-2022-12:29:31 - INFO: Sending COOK_START events.
3932 - 04-07-2022-12:29:31 - INFO: Generating new CID.
3932 - 04-07-2022-12:29:31 - INFO: Publishing to /iot/client/workflow
3932 - 04-07-2022-12:29:31 - INFO: Sending COOK_START | Loop: 1:
3932 - 04-07-2022-12:29:31 - INFO: bezel (11:22:33:44:55:66) ->|COOK_START|-> mqtt (86:1A:32:3F:02:10)
3932 - 04-07-2022-12:29:31 - INFO: cid: e6d5ac6c-b68f-11ec-959e-00155db1dd6d | guid: e6d5ac6c-b68f-11ec-959e-00155db1dd6d
3932 - 04-07-2022-12:29:31 - INFO: Connected to MQTT Broker.
3932 - 04-07-2022-12:29:31 - INFO: Ready.
3932 - 04-07-2022-12:29:31 - INFO: Retry Interval: 2
3932 - 04-07-2022-12:29:31 - INFO: Incoming payload validated.
3932 - 04-07-2022-12:29:31 - INFO: Received ACK:
3932 - 04-07-2022-12:29:31 - INFO: bezel (11:22:33:44:55:66) <-|ACK|<- mqtt (86:1A:32:3F:02:10)
3932 - 04-07-2022-12:29:31 - INFO: cid: e6d5ac6c-b68f-11ec-959e-00155db1dd6d | guid: d9777319-d81e-af18-2b46-ea50701ac144
3932 - 04-07-2022-12:29:34 - INFO: Publishing to /iot/client/workflow
3932 - 04-07-2022-12:29:34 - INFO: Sending COOK_START | Loop: 1:
3932 - 04-07-2022-12:29:34 - INFO: bezel (11:22:33:44:55:66) ->|COOK_START|-> mqtt (86:1A:32:3F:02:10)
3932 - 04-07-2022-12:29:34 - INFO: cid: e6d5ac6c-b68f-11ec-959e-00155db1dd6d | guid: e8b54556-b68f-11ec-959e-00155db1dd6d
3932 - 04-07-2022-12:29:34 - INFO: Incoming payload validated.
3932 - 04-07-2022-12:29:34 - INFO: Received ACK:
3932 - 04-07-2022-12:29:34 - INFO: bezel (11:22:33:44:55:66) <-|ACK|<- mqtt (86:1A:32:3F:02:10)
3932 - 04-07-2022-12:29:34 - INFO: cid: e6d5ac6c-b68f-11ec-959e-00155db1dd6d | guid: f6b12b6d-b3e4-57d9-8e9f-0f612881ef2f
3932 - 04-07-2022-12:29:35 - INFO: Sending COOK_QUANTITY events.
3932 - 04-07-2022-12:29:35 - INFO: Publishing to /iot/client/workflow
3932 - 04-07-2022-12:29:35 - INFO: Sending COOK_QUANTITY | Loop: 1:
3932 - 04-07-2022-12:29:35 - INFO: bezel (11:22:33:44:55:66) ->|COOK_QUANTITY|-> mqtt (86:1A:32:3F:02:10)
3932 - 04-07-2022-12:29:35 - INFO: cid: e6d5ac6c-b68f-11ec-959e-00155db1dd6d | guid: e963b474-b68f-11ec-959e-00155db1dd6d
```

### Using the Configuration File

Like the Blink flow, the Cook Cycle can also be configured either with command-line
parameters, or by the usage of a configuration file, called **cook-defaults.ini** by default.

```
cook-start=<int: [0-3]>
cook-quantity=<int: [0-3]>
cook-complete=<int: [0-3]>
cook-cancel=<int: [0-3]>
cook-complete-ack=<int: [0-3]>
recipe-instance-id=<int>
recipe-name=<str>
remaining-time=<int>
product-quantity=<int>
flow=<str: 'cook_start | cook_quantity | cook_complete | cook_complete_ack'>
```

Note the last parameter, **flow** - this parameter must be set, and can contain any
of the values shown, delimited by ' | ' - failure to follow this format will result in
a thrown exception. This parameter essentially delineates the sequence in which these
events will be sent. Their corresponding integer values in the parameters above denote how
many times each will be sent. These values can also be passed as command-line arguments,
or as a custom configuration file.

**Example 1: Command-line parameters:**
```
python main.py --bezel-mac 11:22:33:44:55:66 --mqtt-broker 10.0.0.108 --mode cook \
    --cook-start 1 \
    --cook-quantity 2 \
    --cook-complete 0 \
    --cook-cancel 1 \
    --cook-complete-ack 0 \
    --recipe-name 'OR Chicken' \
    --recipe-instance-id 5 \
    --remaining-time 2 \
    --product-quantity 1 \
    --flow 'cook_cancel | cook_start | cook_complete | cook_complete_ack'
```

**Example 2: Configuration file:**

Configuration file: _./config/custom_cook.ini_:
```
cook-start=2
cook-quantity=2
cook-complete=2
cook-cancel=0
cook-complete-ack=2
recipe-instance-id=1
recipe-name='OR Chicken'
remaining-time=3
product-quantity=1
flow='cook_start | cook_quantity | cook_complete | cook_complete_ack'
```

```
python main.py --bezel-mac 11:22:33:44:55:66 --mqtt-broker 10.0.0.108 --mode cook --cook-config ./config/custom_cook.ini
```

You may also edit the default configuration _cook-defaults.ini_.

Once the cook cycle has run, the application will display basic statistics
as well as the contents of every payload sent and received:

```
3932 - 04-07-2022-12:30:16 - INFO: {
    "header": {
        "versionInfo": {
            "api": "3.x.x",
            "applianceType": "FRYER-1.0.0",
            "applianceSpec": "Sub1-1.x.x"
        },
        "equipmentType": "FRYER",
        "destination": "11:22:33:44:55:66",
        "source": "86:1A:32:3F:02:10",
        "type": "ACK",
        "dateTime": "2022-04-07T16:30:13.901+0000",
        "correlationId": "f5d562c0-b68f-11ec-959e-00155db1dd6d",
        "guid": "8457e970-c15d-91e0-9a5f-e75bbfd2b7a2"
    },
    "errorCode": 0
}
3932 - 04-07-2022-12:30:16 - INFO: Total payloads processed: 32
3932 - 04-07-2022-12:30:16 - INFO: Total payloads sent: 16
3932 - 04-07-2022-12:30:16 - INFO: Total payloads received: 16
3932 - 04-07-2022-12:30:16 - INFO: Events sent: ['COOK_START', 'COOK_QUANTITY', 'COOK_COMPLETE', 'COOK_COMPLETE_ACK']
3932 - 04-07-2022-12:30:16 - INFO: Total execution time: 45.37s
3932 - 04-07-2022-12:30:16 - INFO: Flow completed successfully.
```