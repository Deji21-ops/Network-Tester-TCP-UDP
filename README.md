# Network-Tester-TCP-UDP
Developed a Python-based network testing tool using Mininet, TCP and UDP sockets. Implemented custom network topologies, multi-client TCP testing, UDP packet transmission, bandwidth measurement, packet loss, jitter and RTT calculations using acknowledgements (ACKs).

Project Overview

A Python-based network testing tool developed as part of my SCC.231 coursework. The project uses Mininet and socket programming to create network topologies and test network performance using TCP and UDP protocols.

The tool measures important network performance metrics, including bandwidth, jitter, packet loss and Round-Trip Time (RTT).

Technologies Used

* Python
* Mininet
* TCP and UDP sockets
* Network routing
* Socket programming
* Threading

Features

1. Custom Mininet Network Topology

* Created a custom network topology consisting of 5 hosts, 2 switches and 3 routers.
* Configured IP addresses and routing rules.
* Tested connectivity between hosts and routers using ping commands.

2. TCP Client and Server

* Implemented a TCP server capable of accepting multiple clients.
* Developed a TCP client that transmits data over a specified testing period.
* Measured and displayed bandwidth throughout testing.
* Implemented logging and test summaries.

3. UDP Client and Server (Without ACKs)

* Implemented UDP packet transmission at a fixed sending rate.
* Measured bandwidth, jitter and packet loss.
* Used packet IDs to identify missing packets and calculate packet loss.

4. UDP Client and Server (With ACKs)

* Added acknowledgement (ACK) functionality to UDP communication.
* Server returns packet IDs and timestamps to the client.
* Implemented Round-Trip Time (RTT) and jitter calculations.
* Improved network measurement through acknowledgement-based communication.

Testing and Results

The project was tested through multiple client-server configurations.

Testing demonstrated:

* TCP bandwidth measurements.
* UDP bandwidth and packet-loss calculations.
* UDP jitter measurements.
* RTT calculations using acknowledgements.
* Successful communication between devices within the Mininet topology.

Key Learning Outcomes

Through this project, I developed practical experience in:

* Socket programming and network communication.
* Understanding the differences between TCP and UDP.
* Implementing client-server architectures.
* Network topology creation and routing using Mininet.
* Measuring network performance and analysing packet transmission.
* Debugging networking applications and handling communication issues.

Project Context

Developed as part of the SCC.231 university coursework at Lancaster University.
