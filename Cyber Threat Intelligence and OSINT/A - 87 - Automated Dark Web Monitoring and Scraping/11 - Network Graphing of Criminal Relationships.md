---
tags: [darkweb, scraping, automation, vapt]
difficulty: advanced
module: "87 - Automated Dark Web Monitoring and Scraping"
topic: "87.11 Network Graphing of Criminal Relationships"
---

# Network Graphing of Criminal Relationships

## 1. Introduction to Graph Theory in Cyber Threat Intelligence (CTI)

The dark web is inherently a network of interacting entities: vendors, buyers, forum administrators, ransomware operators, and initial access brokers (IABs). Traditional relational databases are poorly suited for modeling these multi-dimensional, heavily interconnected relationships. Graph theory provides a mathematical structure to model these interactions, representing entities as **nodes** (or vertices) and relationships as **edges**.

In the context of Automated Dark Web Monitoring, as your scrapers collect raw HTML, forum posts, and transaction logs, extracting the hidden relationships between threat actors is crucial for mapping out criminal syndicates. By employing network graphing, CTI analysts can uncover alias reuse, shared infrastructure, vendor supply chains, and the central figures in illicit operations.

### 1.1 The Shift from Tables to Graphs
Relational databases require complex `JOIN` operations to traverse relationships. If you want to find out "Which vendors shared a PGP key, and which forums do they both post on?", the SQL query becomes exponentially slow as data grows. Graph databases (like Neo4j, ArangoDB, or Amazon Neptune) use index-free adjacency, meaning traversing a relationship is a constant-time operation.

## 2. Technical Deep Dive: Extracting and Modeling Entities

Before graphing, unstructured text must be converted into structured graph data. This requires a robust Natural Language Processing (NLP) and regex pipeline.

### 2.1 Entity Extraction Pipeline
1. **Raw Scrape Data:** HTML from Tor forums, Telegram channel dumps, or market listings.
2. **Parsing:** Using `BeautifulSoup` or `lxml` to extract post author, timestamp, content, and thread context.
3. **Regex Extraction:** Extracting identifiers such as Bitcoin/Monero addresses, PGP keys, Jabber/XMPP IDs, Tox IDs, and email addresses.
4. **NLP / Named Entity Recognition (NER):** Identifying malware names, vulnerability CVEs, or victim company names using custom spaCy models.

### 2.2 The CTI Graph Data Model (Ontology)
A well-defined ontology ensures consistency. Consider the following Node labels and Edge types:

**Nodes:**
- `ThreatActor` (Username, Alias)
- `ContactInfo` (Email, Jabber, Tox)
- `CryptoAddress` (BTC, XMR)
- `PGPKey` (Fingerprint)
- `Forum` (Onion URL, Name)
- `Malware` (Family Name)
- `Victim` (Company Name, Domain)

**Edges (Relationships):**
- `(ThreatActor)-[:POSTED_ON]->(Forum)`
- `(ThreatActor)-[:USES_CONTACT]->(ContactInfo)`
- `(ThreatActor)-[:OWNS_WALLET]->(CryptoAddress)`
- `(ThreatActor)-[:SELLS]->(Malware)`
- `(PGPKey)-[:USED_BY]->(ThreatActor)`

## 3. Architecture Diagram

```ascii
+-------------------+        +---------------------+        +--------------------+
|                   |        |                     |        |                    |
|  Dark Web Scraper | -----> | NLP & Regex Engine  | -----> | Entity Resolution  |
| (Scrapy, Tor,     |        | (spaCy, YARA, RegEx)|        | (Deduplication)    |
|  Telegram API)    |        |                     |        |                    |
+-------------------+        +---------------------+        +---------+----------+
                                                                      |
                                                                      v
                                                            +--------------------+
                                                            |                    |
                                                            |   Graph Database   |
                                                            |   (Neo4j)          |
                                                            |                    |
                                                            +---------+----------+
                                                                      |
                   +--------------------------------------------------+
                   |
                   v
+------------------------------------+
|                                    |
|   Graph Analytics & Visualization  |
|   (Linkurious, Gephi, Neo4j Bloom) |
|                                    |
+------------------------------------+
```

## 4. Advanced Graph Analysis Techniques

Once the data is inside a graph database, advanced algorithmic analysis can be applied to extract actionable intelligence.

### 4.1 Centrality Algorithms
Centrality helps identify the most important nodes in the criminal network.
- **Degree Centrality:** Which threat actor has the most direct connections (e.g., interacts with the most unique users)?
- **Betweenness Centrality:** Identifies actors who act as bridges or brokers between isolated criminal groups. An IAB connecting ransomware groups to victim networks will have high betweenness.
- **PageRank:** Used to find the most influential actors or forums. A forum linked to by many reputable vendors will score highly.

### 4.2 Community Detection
Threat actors naturally form syndicates or cliques. Algorithms like **Louvain Modularity** or **Label Propagation** can automatically group nodes into distinct criminal organizations, revealing hidden sub-groups within a massive forum.

### 4.3 Pathfinding
When a new threat actor appears, pathfinding algorithms (like Dijkstra’s or A* Shortest Path) can answer: "What is the shortest path between this new actor and known APT groups?" If they are only two hops away (e.g., they use the same Jabber server as a known APT), the risk score increases.

## 5. Step-by-Step Implementation Guide

### Step 1: Setting up Neo4j
Launch a Neo4j instance using Docker:
```bash
docker run \
    --name neo4j-cti \
    -p 7474:7474 -p 7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/SuperSecretPassword \
    neo4j:latest
```

### Step 2: Ingesting Data with Cypher and Python
Using the `neo4j` Python driver to push scraped data into the graph.

```python
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "SuperSecretPassword")

def create_actor_and_crypto(tx, actor_name, crypto_address):
    query = """
    MERGE (a:ThreatActor {name: $actor_name})
    MERGE (w:CryptoAddress {address: $crypto_address})
    MERGE (a)-[r:OWNS_WALLET]->(w)
    RETURN a, w, r
    """
    tx.run(query, actor_name=actor_name, crypto_address=crypto_address)

# Example scraped data
scraped_data = [
    {"actor": "DarkOverlord", "btc": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"},
    {"actor": "LockBitSupp", "btc": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"} # Shared wallet!
]

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        for entry in scraped_data:
            session.write_transaction(create_actor_and_crypto, entry["actor"], entry["btc"])
```

### Step 3: Querying the Graph
To find threat actors sharing the same Bitcoin wallet (a strong indicator of shared identity or syndicate operation), use this Cypher query:
```cypher
MATCH (a1:ThreatActor)-[:OWNS_WALLET]->(w:CryptoAddress)<-[:OWNS_WALLET]-(a2:ThreatActor)
WHERE a1.name <> a2.name
RETURN a1.name, w.address, a2.name
```

## 6. Real-World Attack Scenario

### Scenario: Unmasking an Initial Access Broker (IAB)
A new user on the Exploit[.]in forum, operating under the alias `RDP_King`, begins selling access to a tier-1 European bank. A standard relational query might only show their activity on that specific forum.

However, the CTI team's automated graph platform ingests the scrape. `RDP_King` included a Tox ID in their signature. 
1. The graph traversal automatically maps the Tox ID node.
2. The database identifies a second link: The same Tox ID was used 18 months ago by an account named `SilentStrike` on a defunct dark web market.
3. Expanding `SilentStrike` reveals a PGP key associated with the account.
4. Expanding the PGP key reveals it was previously uploaded to a clear-web Ubuntu keyserver with an email address `j.doe@example.com`.
5. The CTI team has now correlated a highly anonymous dark web IAB to a clear-web identity, triggering a hand-off to law enforcement.

## 7. Operational Security (OpSec) & Challenges

- **Data Poisoning:** Threat actors are aware of scraping and may intentionally post fake IOCs, decoy PGP keys, or competitor's Jabber IDs to poison CTI databases.
- **Node Explosion:** Indiscriminate scraping of common strings (like a popular darknet forum URL) can create "super nodes" connected to millions of actors, rendering visualization tools useless (the "hairball" problem). Strict entity resolution is required.
- **Temporal Graphs:** Relationships change over time. A threat actor might abandon a PGP key. Edges in the graph must have `start_date` and `end_date` properties to reflect the temporal reality of the network.

## 8. Chaining Opportunities
- **[[12 - Automated PGP Key Discovery and Tracking]]:** PGP keys form the strongest, most mathematically verifiable edges in your graph database.
- **[[13 - Dark Web Data Enrichment using MISP]]:** Graph anomalies can trigger MISP events, exporting correlated IOCs to SIEMs.
- **[[14 - Building a Custom CTI Dashboard]]:** Graph metrics (e.g., sudden spikes in modularity) can be visualized as widgets on the main CTI dashboard.

## 9. Related Notes
- [[Graph Database Fundamentals]]
- [[Natural Language Processing for CTI]]
- [[Threat Actor Profiling and Attribution]]
- [[De-anonymization Techniques in Tor]]
