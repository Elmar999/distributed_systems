# Distributed Systems

### Introduction
In this repository, I used Mininet, "instant virtual network on the laptop", to apply different distributed systems techniques such as centralized distributed system, eventual consistency, strong consistency between N number of servers.


### Centralized Blackboard - Strong consistency

When there are several servers in the system, due to concurrent updates there can be inconsistencies between servers. To overcome this problem, I have applied "Bully" leader election algorithm which makes system strongly consistent.

Brief description for Bully election algorithm:

* Servers in the network participate in leader election.
* They elect one leader, Each post is sent to the leader which distributes it to the network.
* Once election finishes, the leader is established and everyone agrees on it.
* The leader can serve as a centralized sequencer:
    * Leader decides the correct, global order of all messages.
    * Everybody else follows that order.

After Bully election algorithm:
* concurrent submissions do not lead to problems anymore.
* all blackboard entries always appear in the same
order.
* the leader can handle modified &
deleted posts.

If network crashes, vessels again selects a new leader using Bully election algorithm.


### Eventually Consistent Blackboard
In eventual consistency messages can appear in different order temporarily and it can be inconsistent for a while. Eventually, they will converge to the same order.
Boards are distributed:
* No centralized leader
* Each post is updated to the local board, then
propagated to other boards
* All boards are eventually consistent. 
* Used in many applications like Google File System (GFS) and Facebook’s Cassandra

In order to make system eventually consistent, logical clocks and server id has been used. Initially each server has its own logical clock (counter value). When server updates its local board, it propogates the message to other servers with its logical clock and id.

#### Eventual consistency protocol

* Each post has a logical clock number:
* logical clcok number of a new post: the last sequence number received + 1
* On a server:
* Posts are ordered by (logical clock numbers, server id)
* If two posts have the same logical clock number (it can happen when messages has been sent concurrently), system is still consistent since it will differ with sever ids.

