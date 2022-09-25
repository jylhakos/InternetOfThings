// $ go run mqtt/client <NUMBER>

package main

import (
    mqtt "github.com/eclipse/paho.mqtt.golang"
    "time"
    "os"
    //"os/signal"
    //"syscall"
    "math/rand"
    "strconv"
    "fmt"
    "log"
)

var messageHandler mqtt.MessageHandler = func(client mqtt.Client, msg mqtt.Message) {
    fmt.Printf("Received: %s from topic: %s\n", msg.Payload(), msg.Topic())
}

var connectionHandler mqtt.OnConnectHandler = func(client mqtt.Client) {
    fmt.Println("Connected\n")
}

var connectionLostHandler mqtt.ConnectionLostHandler = func(client mqtt.Client, err error) {
    fmt.Printf("Connect lost: %v\n", err)
}

func publish(client mqtt.Client, msg string ) {
    text := fmt.Sprintf("message %s", msg)
    token := client.Publish("topic/mqtt_test", 0, false, text)
    fmt.Printf("Publish: %s\n", text)
    token.Wait()
}

func subscribe(client mqtt.Client) {
    topic := "topic/mqtt_test"
    token := client.Subscribe(topic, 1, nil)
    fmt.Printf("Subscribe: %s\n", topic)
    token.Wait()  
}

func main() {

    //var broker = "broker.emqx.io"

    var broker = "test.mosquitto.org"

    var port = 1883

    var id string = ""

    //keepAlive := make(chan os.Signal, 1)

    //signal.Notify(keepAlive, os.Interrupt, syscall.SIGTERM)

    //mqtt.DEBUG = log.New(os.Stdout, "", 0)

    mqtt.ERROR = log.New(os.Stdout, "", 0)

    if len(os.Args) > 1 {
        var arg string = os.Args[1]
        fmt.Printf("arg: %s\n", arg)
        id = id + arg
        
    } else {
        rand.Seed(time.Now().UnixNano())
        var random int = rand.Intn(1024)
        var value string = strconv.Itoa(random)
        fmt.Printf("random: %s\n", value)
        id = value
    }
 
    fmt.Printf("id: %s\n", id)

    opts := mqtt.NewClientOptions()

    opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, port))

    var client_id = "mqtt_client_" + id

    opts.SetClientID(client_id)

    //opts.SetUsername("emqx")

    //opts.SetPassword("public")

    opts.SetKeepAlive(60 * time.Second)

    opts.SetDefaultPublishHandler(messageHandler)

    opts.OnConnect = connectionHandler

    opts.OnConnectionLost = connectionLostHandler

    client := mqtt.NewClient(opts)

    if token := client.Connect(); token.Wait() && token.Error() != nil {
        panic(token.Error())
    }

    var text string = "Hello " + id

    fmt.Printf("text: %s\n", text)

    subscribe(client)

    publish(client, text)

    time.Sleep(60 * time.Second)

    client.Disconnect(1000)

    time.Sleep(1 * time.Second)

    //<- keepAlive

    //fmt.Printf("Ctrl-C\n")
}