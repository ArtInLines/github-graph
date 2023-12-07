# Github Graph

This project was created for uni course "Big Data".

The idea is to create a graph of all Github users and their (public) repositories. The edges in said graph would represent relations between these entities (for example a "a-follows-b" or "a-forked-repository-owned-by-b" relationship). The goal is to collect and store the data for this network graph and then allow the user to query certain statistics about this graph via a web-interface. We specifically, want to show the following information:
- The shortest path between two users
- The [n-clique](https://de.wikipedia.org/wiki/Cliquenanalyse#n-Clique) of a user

## Disclaimer

This project is still a Work-in-Progress. This means, not everything might work and the documentation might quickly become outdated.

## Architecture

This project contains several independent parts:

- Data Collector
- Server
- Frontend

The Data-Collector deals with getting all the required data from the Github-API and stores the data in a remote Neo4j database.

The Server connects to the same Neo4j database and offers a REST-API for accessing relevant data via HTTP.

The Frontend is a website, that visualizes the above mentioned statistics dynamically.

## Data Model

neo4j is a schema-free graph database. Regardless of formally required schema, it is still useful to document the data model, that is used by the application. For that, a primer on modelling data for graph-based databases like neo4j is given first, before this application's data model is specified

### Primer on Graph Databases

Graph Databases like neo4j store 4 kinds of information:

1. Nodes
2. Edges/Relations
3. Labels
4. Properties/Attributes

Each shall be explained shortly now.

Nodes are conceptually the primary data that is stored in your database. Coming from relational databases, you can imagine each row of each table to become its own node.

Where in relational databases though, you require primary and foreign keys to create relationships between rows, here you simply declare an Edge between two nodes. An Edge is always directed.

Both nodes and edges can have labels. A label is conceptually the data type of the node/edge. Compared with relational databases again, a label can be seen as specifying the table that the node/row is from.

Lastly, each node and edge can contain several properties or attributes. These are simple key-value pairs. Every node/edge of one label has the same properties (with independent values of course). The analog to relational databases here would be a table's columns.

### Data Model Specification

If the following notation for the models specification is unclear, take a look at [Model-Notation](#model-notation)

We specify the following labels with their specific attributes for nodes:

- User
  - name: string (unique)
  - avatar: string
  - visted: int [how often the account was already visited in the process of looking for nodes]
- Repo
  - name: string [this is the repo's full name which includes the owner account's username]
  - visited: int
- Lang
  - name: string [Name of the Language]

We specify the following labels with their specific attributes for edges:

- OWNS
  - (User) -> (Repo)
- FOLLOWS
  - (User) -> (User)
- FORKED_TO
  - (Repo) -> (Repo)
- STARRED
  - (User) -> (Repo)
- CONTRIBUTED
  - (User) -> (Repo)
  -
- WRITTEN_IN
  - (Repo) -> (Lang)
  - abs: int [Lines of Code in the Repo that were written in the Language]
  - rel: float [Percentage (0 to 1) of code in the Repo that were written in the Language]

Lastly, we shall give some examples to illustrate this Data Model:

### Model Notation

Our notation for specifying the model is as follows:

- <Label1>
  - <Key1>: <Value-Type1> (<Optional Constraint>) [<Optional Documentation>]
  - <Key2>: <Value-Type2> [<Optional Documentation>]
- <Label2>
  - <Key3>: <Value-Type3>

For edges, we expand this notation to also specify the labels of nodes that sit on either side of the relation:

- <Label1>
  - (<Node-Label-From1>) -> (<Node-Label-To1>)
  - <Key1>: <Value-Type1>
  - <Key2>: <Value-Type2>
- <Label2>
  - (<Node-Label-From2>) -> (<Node-Label-To2>)
  - <Key3>: <Value-Type3>
