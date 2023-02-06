# Kubernetes

## Overview

Kubernetes is a "platform for managing containerized workloads and services".

We can divide the history of deployment into 3 eras:
* Traditional deployment
* Virtualized deployment
* Container deployment

In traditional deployment, applications ran on physical servers with no way to define resource boundaries for an application except to run each application on its own server, which is expensive. In virtualized deployment, an application can run within its own virtual machine with resource boundaries. In container deployment, an application within its own container with resource boundaries giving the same benefits as virtual machines, while being lighter weight, because containers share an operating system.

Kubernetes provides the following features:
* Service discovery
* Load balancing
* Storage orchestration
* Automated rollouts and rollbacks
* Automatic bin packing
* Self-healing
* Secret and configuration management

## Kubernetes components

A Kubernetes cluster consists of a set of machines called nodes ("A node may be a virtual or physical machine, depending on the cluster").

Each node runs:

* kubelet: an agent that checks that the containers on the node are running and healthy.
* kube-proxy: a network proxy.
* container runtime: the software responsible for running containers.

The control plane is a set of components that "make global decisions about the cluster (for example, scheduling), as well as detecting and responding to cluster events".

The control plane components are:

* kube-apiserver: Runs an API server. The kubelet and the kube-proxy on each node communicate with the API server. We can run multiple instances of the kube-apiserver behind a load balancer.
* etcd: Stores all cluster data.
* kube-scheduler: "watches for newly created Pods with no assigned node, and selects a node for them to run on"
* kube-controller-manager: Runs controller processes, which consist of a "loop that watches the shared state of the cluster through the apiserver and makes changes attempting to move the current state towards the desired state". For example, the node controller is "responsible for noticing and responding when nodes go down".
* cloud-controller-manager: "link your cluster into your cloud provider's API, and separates out the components that interact with that cloud platform from components that only interact with your cluster." For example, the node controller is responsible for "checking the cloud provider to determine if a node has been deleted in the cloud after it stops responding".

Add-on components include:
* Cluster DNS
* Dashboard for "users to manage and troubleshoot applications running in the cluster"
* Container resource monitoring
* Cluster-level logging

## Nodes

Kubernetes runs an application "by placing containers into Pods to run on Nodes." A pod is set of running containers in the cluster.

There are 2 ways to add a node to the API server:
1) "The kubelet on a node self-registers to the control plane"
2) "You (or another human user) manually add a Node object"

Each node has a unique name.

A node's status includes:
* Addresses: The hostname of the node, the external IP and the internal IP.
* Conditions: Ready, DiskPressure (disk capacity is low), MemoryPressure (node's memory is low), PIDPressure (too many processes on the node), NetworkUnavailable (node's network is misconfigured)
* Capacity and allocatable: "Describes the resources available on the node: CPU, memory, and the maximum number of pods that can be scheduled onto the node."
* Info: "Describes general information about the node, such as kernel version, Kubernetes version (kubelet and kube-proxy version), container runtime details, and which operating system the node uses."

Each node sends heartbeats to "help your cluster determine the availability of each node, and to take action when failures are detected."

## Sources

* http://web.archive.org/web/20230206022632/https://kubernetes.io/docs/concepts/overview/
* http://web.archive.org/web/20230206022653/https://kubernetes.io/docs/concepts/overview/components/
* http://web.archive.org/web/20230204231709/https://kubernetes.io/docs/concepts/architecture/nodes/