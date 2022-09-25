# MQTT

MQTT is a publish/subscribe messaging transport protocol. 

## How to use MQTT in Golang?

This page introduces how to use paho.mqtt.golang client library in the Golang project, and implement the connection, to publish messages, subscribe to topics and receive the published messages from the MQTT broker.

### Project initialization

The Go application uses the paho.mqtt.golang as MQTT client library.

```

$ go get github.com/eclipse/paho.mqtt.golang

```

### Connect to the MQTT broker

A client sends MQTT messages (publish) and the same way, another client can receive MQTT messages (subscribe).

In this way, to send or to receive messages, the publishers and subscribers only need to know the MQTT broker address.

All the options needed depends on the broker we are connected.

The MQTT broker can be configured to require client authentication using a username and password before a connection is permitted.

To test the Go application, we need to connect a MQTT server, either using own for example, Mosquitto or use a public MQTT server. 

### Subscription

A client can subscribe to a topic in the broker. 

### Publish

To send a message (publish) we need to use the method client.Publish with parameters.

![alt text](https://github.com/jylhakos/InternetOfThings/blob/main/Messaging/MQTT/MQTT.png?raw=true)

Figure: Golang application sending and receiving messages using MQTT.

## References

Eclipse Paho MQTT Go client https://github.com/eclipse/paho.mqtt.golang

EMQX public MQTT broker https://www.emqx.com/en/mqtt/public-mqtt5-broker

Eclipse Mosquitto https://test.mosquitto.org/
