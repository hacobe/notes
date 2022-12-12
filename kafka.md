# Kafka

## Background

Kafka is a distributed messaging system for log processing.

Log data includes:
* User activity (e.g., logins, pageviews, clicks, etc)
* Operational metrics (e.g., call latency, errors, and system metrics like CPU, memory, network and disk utilization)

Log data is used in production for:
* Search relevance
* Recommendations
* Ad targeting
* Spam detection

Log aggregators are "primarily designed for collecting and loading the log data into a data warehouse or Hadoop".

The downsides of log aggregators are:
* They mostly focus on consuming log data offline rather than in real-time applications
* They mostly focus on a push model "in which the broker forwards data to consumers" rather than a pull model where "each consumer can retrieve the messages at the maximum rate it can sustain and avoid being flooded by messages pushed faster than it can handle."

The downsides of traditional messaging systems are:
* They offer delivery guarantees that increase the complexity of the system ("For instance, losing a few pageview events occasionally is certainly not the end of the world.")
* They do not focus on high throughput ("For example, JMS has no API to allow the producer to explicitly batch multiple messages into a single request. This means each message requires a full TCP/IP roundtrip, which is not feasible for the throughput requirements of our domain")
* They are not distributed systems ("There is no easy way to partition and store messages on multiple machines.")
* They expect immediate consumption of messages and thus a small queue and slow down a lot when messages accumulate in the queue

Kafka has the strengths of log aggregators in that it's a scalable, distributed system that can offer high throughput with an API similar to the traditional messaging systems. It is a "messaging-based log aggregator".

## APIs

A producer publishes a set of messages to a particular topic.

Sample producer code:
```
producer = new Producer(...);
message = new Message("test message str".getBytes());
set = new MessageSet(message);
producer.send("topic1", set);
```

A consumer subscribes to a topic by creating "one or more message streams for the topic", where each message stream "provides an iterator interface over the continual stream of messages being produced". If there are multiple message streams, then the messages are evenly divided among them. The iterator never terminates, but instead blocks when empty.

Sample consumer code:
```
streams[] = Consumer.createMessageStreams("topic1", 1)
for (message : streams[0]) {
	bytes = message.payload();
	// do something with the bytes
}
```

## Design

A Kafka cluster consists of multiple brokers and multiple producers and consumers interacting with the brokers. Each broker stores one or more partitions of a topic. A partition of a topic corresponds to a log. A log consists of a set of segment files. When a producer publishes a message to a partition of a topic, the broker appends the message to the last segment file. The partition is choosen either randomly or via a partitioning function.

The messages from a partition are consumed by a single consumer at a time (if multiple consumers were used, then we would have to use synchronization to ensure that a message only gets processed once). The consumer consumes messages sequentially.

## Usage

Kafka is used for both "online and offline consumption of the log data of all types".

For online consumption, the frontend services are the publishers, there is a load balancer that distributes the publish requests to the brokers and the real-time services are the consumers.

For offline consumption, consumers pull data from the Kafka instances used for online consumption to the Kafka instance used for offline consumption. The data from the Kafka instance used for offline consumption is then loaded into Hadoop and the data warehouse. 

## Sources

* "Kafka: a Distributed Messaging System for Log Processing" (https://s3.amazonaws.com/systemsandpapers/papers/Kafka.pdf)
