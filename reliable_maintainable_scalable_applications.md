# Reliable, maintainable and scalable applications

**Functional requirements** are what a system should do (e.g., "allowing data to be stored, retrieved, searched and processed in various ways").

**Non-functional requirements** are "general properties like security, reliability, compliance, scalability, compatibility, and maintainability".

We focus on 3 non-functional requirements:
* Reliability: "The system should continue to work correctly (performing the correct function at the desired level of performance) even in the face of adversity (hardware or software faults, and even human error)"
* Scalability: "As the system grows (in data volume, traffic volume, or complexity), there should be reasonable ways of dealing with that growth."
* Maintainability: "Over time, many different people will work on the system (engineering and operations, both maintaining current behavior and adapting the system to new use cases), and they should all be able to work on it productively"

For **reliability**, we aim to guard against:
* hardware failures ("Hard disks are reported as having a mean time to failure (MTTF) of about 10 to 50 years...Thus, on a storage cluster with 10,000 disks, we should expect on average one disk to die per day.")
* software bugs
* human error

We employ various fault tolerance strategies to prevent the failure of the system ("A **fault** is usually defined as one component of the system deviating from its spec, whereas a **failure** is when the system as a whole stops providing the required service to the user").

For **scalability**, we first to need to describe **load**. Load is described in terms of load parameters, where the "best choice of parameters depends on the architecture of your system: it may be requests per second to a web server, the ratio of reads to writes in a database, the number of simultaneously active users in a chat room, the hit rate on a cache, or something else".

We can then look at the relationship between load and performance in 2 ways:
* "When you increase a load parameter and keep the system resources (CPU, memory, network bandwidth, etc.) unchanged, how is the performance of your system affected?"
* "When you increase a load parameter, how much do you need to increase the resources if you want to keep performance unchanged?"

The performance we want to measure also depends on the application. For a batch processing system, we "we usually care about throughput—the number of records we can process per second, or the total time it takes to run a job on a dataset of a certain size". In contrast, for online systems "what’s usually more important is the service's response time—that is, the time between a client sending a request and receiving a response."

Note that "Latency and response time are often used synonymously, but they are not the same. The response time is what the client sees: besides the actual time to process the request (the service time), it includes network delays and queueing delays. Latency is the duration that a request is waiting to be handled—during which it is latent, awaiting service".

We usually measure response time in terms of percentiles. High percentiles of response times are known as tail latencies. For example, a service level agreement "may state that the service is considered to be up if it has a median response time of less than 200 ms and a 99th percentile under 1 s (if the response time is longer, it might as well be down), and the service may be required to be up at least 99.9% of the time."

As systems scales, there can be a number of problems, including, for example: "the volume of reads, the volume of writes, the volume of data to store, the complexity of the data, the response time requirements, the access patterns, or (usually) some mixture of all of these plus many more issues."

We can break **maintainability** further into:
* Operability
* Simplicity
* Evolvability

## Sources

* Chapter 1, DDIA