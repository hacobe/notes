# Data warehousing

There are 2 major categories of storage engines:
* Online transaction processing (OTLP)
* Online analytic processing (OLAP)

The difference between the two categories is a little fuzzy, but here are their characteristics:
* Main read pattern
	* OTLP: "Small number of records per query, fetched by key"
	* OLAP: "Aggregate over large number of records"
* Main write pattern
	* OTLP: "Random-access, low-latency writes from user input"
	* OLAP: "Bulk import (ETL) or event stream"
* Primarily used by
	* OTLP: "End user/customer, via web application"
	* OLAP: "Internal analyst, for decision support"
* What data represents
	* OTLP: "Latest state of data (current point in time)"
	* OLAP: "History of events that happened over time"
* Dataset size
	* OTLP: "Gigabytes to terabytes"
	* OLAP: "Terabytes to petabytes"	
* Main bottleneck
	* OTLP: Disk seek time
	* OLAP: Disk bandwidth
* Query volume and demandingness
	* OTLP: High volume, Low demandingness
	* OLAP: Low volume, High demandingness

A data warehouse is "is an enterprise system used for the analysis and reporting of structured and semi-structured data from multiple sources" (https://cloud.google.com/learn/what-is-a-data-warehouse).

The process of getting data into the warehouse is known as Extract-Transform-Load (ETL): "Data is extracted from OLTP databases (using either a periodic data dump or a continuous stream of updates), transformed into an analysis-friendly schema, cleaned up, and then loaded into the data warehouse."

The advantages of a data warehouse are that:
* It can be optimized for analytic access patterns
* It does not interfere with production databases

The data model of a data warehouse is usually relational and the schema used is usually a star schema (i.e., dimensional modeling).

The star schema organizes data into fact tables and dimension tables.

Each row in a fact table represents an event. Each column in a fact table is a foreign key reference to a dimension table or a value.

Each row in a dimension table is the value of that dimension. Each column is an attribute of the dimension.

Data warehouses often use column-oriented storage, because then the data warehouse can retrieve all the values of a few columns very quickly rather than reading the values for all the columns in a row and discarding the values that do not belong to the columns of interest.

Column-oriented storage also enables column compression, because often a column has a lot of duplicate values. One approach is to use bitmap encoding, where we represent a column with multiple bitmaps (one for each distinct value of the column) and where each bitmap has 1 bit for each row in the column. We can use run-length encoding to compress the data. It's also easy to implement common analytics queries using bitmaps.

The sort order of the rows of each column can also speed up read queries.

Finally, materialized views store a copy of a query's results on disk. A data cube or an OLAP cube is a special case of a materialized view, where we store "a grid of aggregates grouped by different dimensions".

## Sources

* Chapter 3, DDIA