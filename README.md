# Ping-Pong Service for Apache Kafka

Ping-Pong Service is a very simple software application for testing stream processing with [Apache Kafka](https://kafka.apache.org/).

The service is in charge of listening to any Kafka event from the
following topic `dev.pingpong.requested` and it will send a Kafka event to another topic:
`dev.pingpong.succeeded` or `dev.pingpong.failed` depending on the payload of the Kafka event.

For this proof of concept, the service is composed by three components, three new services: the
`producer`, the `validator` and the `reader`. Each of them performs a different role:
* `producer`: Dummy service that sends Kafka messages to first Topic. This component is the "source" of messages.
* `validator`: Service that validates the schema of input messages from first Topic. When the input is right, this component sends a new message to Topic `dev.pingpong.succeeded`, otherwise the message is sent to the Topic `dev.pingpong.failed`.    
* `reader`: Final endpoint that digests `dev.pingpong.succeeded` and `dev.pingpong.failed` Topics.

![Alt text](docs/images/diagram.png?raw=true "PingPong Services")

### Setup

Next guide shows how to deploy everything on a Kubernetes cluster or using Docker compose.

#### Prerequisites

- **Docker**

  [Docker]((https://www.docker.com/)) is an open-source platform for building, deploying, and managing containerized applications.
  
  *Docker* packages software into standardized units called containers that have everything the software needs to run including libraries, system tools, code, and runtime. Using *Docker*, you can quickly deploy and scale applications into any environment and know your code will run.

- **Kubernetes** or **Docker compose**

  [Kubernetes](https://kubernetes.io/) is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. 

  [Docker Compose](https://docs.docker.com/compose/) is a tool for running multi-container applications on [Docker]((https://www.docker.com/)) defined using the *Compose file format*. A Compose file is used to define how the one or more containers that make up your application are configured. Once you have a Compose file, you can create and start your application with a single command: `docker compose up`.
  
- **Apache Kafka**

  [Apache Kafka](https://kafka.apache.org/) is a distributed streaming platform designed to build real-time pipelines and can be used as a message broker or as a replacement for a log aggregation solution for big data applications.

  *Apache Kafka* is packaged by [Bitnami](https://bitnami.com/) for both infrastructures, [Kubernetes](https://bitnami.com/stack/kafka/helm) and [Docker](https://hub.docker.com/r/bitnami/kafka/). If you do not have Kafka running yet, deploying applications as Helm Charts is the easiest way to get started with our applications on Kubernetes. 

For this demo I am using Kafka packaged by Bitnami and deployed in a Kubernetes cluster.

#### Kafka Topics

The service set is in charge of listening to any Kafka event from the
following topic `dev.pingpong.requested` and it will send a Kafka event to another topic:
`dev.pingpong.succeeded` or `dev.pingpong.failed` depending on the payload of the Kafka event.

You can create that three Kafka Topics using the kafka-client that you can add to the cluster:

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

Now use `--list` option of `kafka-topics` to view the list of registered Topics:

```bash
> kafka-topics.sh \
   --bootstrap-server <kafka-service-name>.default.svc.cluster.local:9092 \
   --list
```

#### Docker images

The Dockerfile in the root folder builds a Docker image with the service. Run in the Docker host:

```bash
> docker build -f ./Dockerfile -t pingpong/dummyapp:1.0.0 .
```

When you want to delete the image, run:

```bash
> docker image rmi pingpong/dummyapp:1.0.0
```

#### Deploying with Helm

Helm is a tool for managing Kubernetes packages called Charts. This resource configures the Services, Pods, number of replicas. 
As usual using Helm packages, the “values.yml” file of the project describes all settings of the deployment and a set of specific entries that configure the services using environment variables.

Deploying PingPong Service with Helm on Kubernetes is easy:

```bash
> helm install --name-template kfpingpong-platform \
    --set producer.image.tag=1.0.0 \
    --set validator.image.tag=1.0.0 \
    --set reader.image.tag=1.0.0 \
    ./pingpong
```

If you want to render templates before deploying the stack of pods and services, run:

```bash
> helm install --name-template kfpingpong-platform --dry-run --debug \
    --set producer.image.tag=1.0.0 \
    --set validator.image.tag=1.0.0 \
    --set reader.image.tag=1.0.0 \
    ./pingpong
```

And that's all!

#### Deploying with Docker compose

Docker Compose is a tool that was developed to help define and share multi-container applications. With Compose, we can create a YAML file to define the services and with a single command, can spin everything up or tear it all down.

Deploying PingPong Service with Docker compose is easy:

```bash
> docker-compose -f docker-compose.yaml up
```

### Results

To test that everything is running in Kubernetes:

```bash
> kubectl get all
```

![Alt text](docs/images/results-k8s-01.png?raw=true "Kubectl get all")

```bash
> kubectl logs kfpingpong-producer-xxx
```

![Alt text](docs/images/results-k8s-02.png?raw=true "producer")

```bash
> kubectl logs kfpingpong-validator-xxx
```

![Alt text](docs/images/results-k8s-03.png?raw=true "validator")

```bash
> kubectl logs kfpingpong-reader-xxx
```

![Alt text](docs/images/results-k8s-04.png?raw=true "reader")

Enjoy!
