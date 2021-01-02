# Distributed Systems

### Introduction
In this repository, I used Mininet, "instant virtual network on the laptop", to apply different distributed systems techniques such as centralized distributed system, eventual consistency, strong consistency between N number of servers. Python programming language with Bottle API has been used to apply the techniques above.


### Centralized Blackboard - Strong consistency

When there are several servers in the system, due to concurrent updates there can be inconsistencies between servers. To overcome this problem, I have applied the "Bully" leader election algorithm which makes the system strongly consistent.

Brief description for Bully election algorithm:

* Servers in the network participate in leader election.
* They elect one leader, Each post is sent to the leader which distributes it to the network.
* Once the election finishes, the leader is established and everyone agrees on it.
* The leader can serve as a centralized sequencer:
    * Leader decides the correct, global order of all messages.
    * Everybody else follows that order.

After Bully election algorithm:
* concurrent submissions do not lead to problems anymore.
* all blackboard entries always appear in the same
order.
* the leader can handle modified &
deleted posts.

If the network crashes, vessels again select a new leader using the Bully election algorithm.


### Eventually Consistent Blackboard
In eventual consistency, messages can appear in different order temporarily and it can be inconsistent for a while. Eventually, they will converge to the same order.
Boards are distributed:
* No centralized leader
* Each post is updated to the local board, then
propagated to other boards
* All boards are eventually consistent. 
* Used in many applications like Google File System (GFS) and Facebook’s Cassandra

To make the system eventually consistent, logical clocks and server-id has been used. Initially, each server has its logical clock (counter value). When the server updates its local board, it propagates the message to other servers with its logical clock and id.

#### Eventual consistency protocol

* Each post has a logical clock number:
* logical clock number of a new post: the last sequence number received + 1
* On a server:
    * Posts are ordered by (logical clock numbers, server id)
    * If two posts have the same logical clock number (it can happen when messages have been sent concurrently), the system is still consistent since it will differ with sever ids.

### Installation

Install mininet: http://mininet.org/download/ <br/>
For centralized blackboard:
```sh
$ cd .../distributed_systems
$ sudo python lab1.py --vessels server/server.py
```

For eventually consistent blackboard:
```sh
$ sudo python lab1.py --vessels server/server1.py
```

You can also decide the number of servers that you want in your system, using *--servers*:

```sh
$ sudo python lab1.py --vessels server/server1.py --servers 8
```


