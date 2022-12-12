# Data models and query languages

We discuss 3 different data models:
* Relational
* Document
* Graph

We can divide these data models into 2 broad types
* SQL (Relational)
* NoSQL (Document, Graph)

We compare the relational model and the document model on:
* object-relational mismatch
* storage locality
* schema flexibility
* support for joins

The **object-relational mismatch**, or the **impedance mismatch**, is the degree of mismatch between the data structures used by application code and the data structures used by the database. A relational model tends to require a translation layer between the database and the application code (often facilitated by an **ORM framework**), while some developers feel that a document model requires less translation. See the section "The Object-Relational Mismatch" in DDIA for more details.

A document model tends to do better on **storage locality**, but only if the entire document is required on reads, because document stores typically require reading the entire document. However, some relational databases also have ways to implement storage locality. See the section "Data locality for queries" in DDIA for more details.

A document model has a more flexible schema than a relational model. We can think of a document model as requiring a **schema-on-read**, while a relational model requires a **schema-on-write**. The schema-on-read approach is helpful for very hetereogeneous data (e.g., when the structure of the data is determined by external systems). See the section "Schema flexibility in the document model" in DDIA for more details.

A document model tends to have weaker support for **joins**. We could always emulate a join using application code, but that is more difficult than relying on the highly optimized code for a join in a relational database. We could also try to avoid joins by storing all the information we need in the document, but this approach leads to a lot of redundant information and harder updates (we need to update the information in all the locations that it appears).

Here are a few types of relationships that we might want to model:
* one-to-many (e.g., a person to attributes of that person's resume)
* many-to-one (e.g., free text strings for a city name to a city ID)
* many-to-many (e.g., a person, an employer, a school and their relationships via job experience and education)

A document model tends to more naturally model one-to-many relationships and the other relationships poorly, because of lack of support for joins.

A relational model tends to more naturally model many-to-one or many-to-many relationships though we have a few options for modeling one-to-many relationships:
* Normalized representation with document attributes in separate tables
* A column with a JSON or XML data type in a relational database with some support for queries on the values of that column
* A column with a string data type where the application decodes it

## Sources

* Chapter 2, DDIA