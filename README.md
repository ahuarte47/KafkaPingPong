# Ping-Pong Service for Apache Kafka

Ping-Pong Service is a very simple software application for testing stream processing with [Apache Kafka](https://kafka.apache.org/).

The service is in charge of listening to any Kafka event from the
following topic `dev.pingpong.requested` and it will send a Kafka event to another topic:
`dev.pingpong.succeeded` or `dev.pingpong.failed` depending on the payload of the Kafka event.

For this proof of concept, the service is composed by three components, three new services: the
`producer`, the `validator` and the `reader`. Each of them performs a different role:
* `producer`: Dummy service that sends Kafka messages to first topic. This component is the "source" of messages.
* `validator`: Service that validates the schema of input messages from first topic. When the input is right, this component sends a new message to topic `dev.pingpong.succeeded`, otherwise the message is sent to the topic `dev.pingpong.failed`.    
* `reader`: Final endpoint that digests `dev.pingpong.succeeded` and `dev.pingpong.failed` topics.

![Alt text](docs/images/diagram.png?raw=true "PingPong Services")

### Setup

Next guide shows how to deploy everything on a Kubernetes cluster or using Docker compose.

#### Prerequisites

- **Docker**

  [Docker](https://www.docker.com/) is an open-source platform for building, deploying, and managing containerized applications.
  
  *Docker* packages software into standardized units called containers that have everything the software needs to run including libraries, system tools, code, and runtime. Using *Docker*, you can quickly deploy and scale applications into any environment and know your code will run.

- **Kubernetes** or **Docker compose**

  [Kubernetes](https://kubernetes.io/) is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. 
  
  Don't you have a Kubernetes instance running?, [Kind](https://kind.sigs.k8s.io/) is a tool for running local Kubernetes clusters using Docker container “nodes”. Kind was primarily designed for testing Kubernetes itself, but may be used for local development. 

  [Docker Compose](https://docs.docker.com/compose/) is a tool for running multi-container applications on [Docker]((https://www.docker.com/)) defined using the *Compose file format*. A Compose file is used to define how the one or more containers that make up your application are configured. Once you have a Compose file, you can create and start your application with a single command: `docker compose up`.
  
- **Apache Kafka**

  [Apache Kafka](https://kafka.apache.org/) is a distributed streaming platform designed to build real-time pipelines and can be used as a message broker or as a replacement for a log aggregation solution for big data applications.

  *Apache Kafka* is packaged by [Bitnami](https://bitnami.com/) for both infrastructures, [Kubernetes](https://bitnami.com/stack/kafka/helm) and [Docker](https://hub.docker.com/r/bitnami/kafka/). If you do not have Kafka running yet, deploying applications as Helm Charts is the easiest way to get started with our applications on Kubernetes. 

For this demo I am using Kafka packaged by Bitnami and deployed in a Kubernetes cluster.

#### Kafka Topics

The service set is in charge of listening to any Kafka event from the
following topic `dev.pingpong.requested` and it will send a Kafka event to another topic:
`dev.pingpong.succeeded` or `dev.pingpong.failed` depending on the payload of the Kafka event.

The service automatically creates all necessary topics, but you can create yourself that three Kafka topics using a kafka-client:

```bash
> kafka-topics.sh \
   --bootstrap-server <kafka-service-name>.default.svc.cluster.local:9092 \
   --create --topic dev.pingpong.requested \
   --partitions 2

> kafka-topics.sh \
   --bootstrap-server <kafka-service-name>.default.svc.cluster.local:9092 \
   --create --topic dev.pingpong.succeeded \
   --partitions 2

> kafka-topics.sh \
   --bootstrap-server <kafka-service-name>.default.svc.cluster.local:9092 \
   --create --topic dev.pingpong.failed \
   --partitions 2
```

Read [here](https://kafka.apache.org/documentation/#topicconfigs) to learn about Topic's settings.

`bootstrap-server` provides the initial hosts that act as the starting point for a Kafka client to discover the full 
set of alive servers in the cluster.

Use `--list` option to view the list of registered topics:

```bash
> kafka-topics.sh \
   --bootstrap-server <kafka-service-name>.default.svc.cluster.local:9092 \
   --list
```

#### Docker images

The Dockerfile in the root folder builds a Docker image with the service. Run in the Docker host:

```bash
> docker build -f ./Dockerfile -t pingpong/serviceapp:1.0.0 .
```

When you want to delete the image, run:

```bash
> docker image rmi pingpong/serviceapp:1.0.0
```

#### Deploying with Helm

[Helm](https://helm.sh/) is a tool for managing Kubernetes packages called Charts. This resource configures the Services, Pods, number of replicas. 
As usual using Helm packages, the “values.yml” file of the project describes all settings of the deployment and a set of specific entries that configure the services using environment variables.

If you are using Kind, you can need before uploading the Docker image:

```bash
> kind load docker-image pingpong/serviceapp:1.0.0
```

Now, deploying PingPong Service with Helm on Kubernetes is easy, goto `deployment/Helm` subfolder and run:

```bash
> helm install --name-template kfpingpong-platform ./pingpong
```

If you want to render templates before deploying the stack of pods and services, run:

```bash
> helm install --name-template kfpingpong-platform --dry-run --debug ./pingpong
```

For uninstalling the software:

```bash
> helm delete kfpingpong-platform
```

And to remove the Docker image from Kind:

```bash
> docker exec -it "kind-control-plane" crictl rmi docker.io/pingpong/serviceapp:1.0.0
```

And that's all!

#### Deploying with Docker compose

[Docker Compose](https://docs.docker.com/compose/) is a tool that was developed to help define and share multi-container applications. With Compose, we can create a YAML file to define the services and with a single command, can spin everything up or tear it all down.

Deploying PingPong Service with Docker compose is easy:

```bash
> docker-compose -f docker-compose.yaml up
```

For uninstalling the software:

```bash
> docker-compose -f docker-compose.yaml down
```

### Results

To test that everything is running in Kubernetes:

```bash
> kubectl get all
```

![Alt text](docs/images/results-k8s-get-all.png?raw=true "Kubectl get all")

```bash
> kubectl logs kfpingpong-producer-xxx
```

![Alt text](docs/images/results-k8s-log-producer.png?raw=true "producer")

```bash
> kubectl logs kfpingpong-validator-xxx
```

![Alt text](docs/images/results-k8s-log-validator.png?raw=true "validator")

```bash
> kubectl logs kfpingpong-reader-xxx
```

![Alt text](docs/images/results-k8s-log-reader.png?raw=true "reader")

You can disable the "producer" and send messages by yourself. Set "dummy" in its `SERVICE_IMPL` setting, this empty implementation really does nothing. 

For sending a new input message, run from a kafla-client:

```bash
> cat message.json | jq
{
  "transaction-id": "ID01", 
  "payload": {
    "message": "ping"
  }
}

> kafla-console-producer.sh \
   --bootstrap-server localhost:9092 \
   --topic dev.pingpong.requested < message.json
```

Enjoy!

### Known issues / TODO

* The services are not working when using the [confluent-kafka](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html) package. Producer and Consumer instances are not be able to connect with the brokers. 
Further research is necessary to figure out what is happening.

### Contribute
Have you spotted a typo in our documentation? Have you observed a bug while running Ping-Pong Service? Do you have a suggestion for a new feature?

Don't hesitate and open an issue or submit a pull request, contributions are most welcome!

### License
Ping-Pong Service is licensed under Apache License v2.0. See LICENSE file for details.