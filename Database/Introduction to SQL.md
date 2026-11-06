# Introduction to SQL – Comprehensive Notes

These notes follow the learning sequence from your DataCamp lessons, starting with database fundamentals and progressing through SQL queries.

Database system used in examples: PostgreSQL

The goal is to understand each concept, why it is used, and how to write the corresponding SQL query.

# 1. Database Fundamentals

## 1.1 What is a Database?

A database is a system for storing, managing, retrieving, and manipulating data efficiently.

Databases are used in:

- Web applications
- Mobile applications
- E-commerce platforms
- Data analysis and reporting
- Machine Learning and MLOps pipelines

Real-world example:

An e-commerce application stores information about customers, products, orders, and payments in a database.

## 1.2 How is Data Organized?

A database organizes data into tables.

A table consists of two main components:

- Rows: Represent individual records or entities.
- Columns: Represent attributes or properties of those records.

Example: `products` table

| product_id | product_name | category    | price |
| ---------- | ------------ | ----------- | ----- |
| 1          | Python Book  | Books       | 500   |
| 2          | Laptop       | Electronics | 65000 |
| 3          | SQL Book     | Books       | 700   |
| 4          | Mouse        | Electronics | 800   |
| 5          | T-Shirt      | Clothing    | 1200  |

Here:

- Table name: `products`
- Rows: Individual products
- Columns: Product ID, name, category, and price.

# 2. SQL Fundamentals

## 2.1 What is SQL?

SQL stands for Structured Query Language.

It is used to communicate with relational databases.

You can use SQL to:

- Retrieve data.
- Filter data.
- Sort data.
- Insert new records.
- Update existing records.
- Delete records.

A SQL query is an instruction sent to a database to perform an operation.

For example:

```
SELECT * FROM products;
```

This requests all columns and rows from the `products` table.

# 3. SELECT – Selecting Data

First query concept

## 3.1 What is SELECT?

`SELECT` specifies which columns you want to retrieve from a database table.

There are two common ways to use it.

A. Select specific columns

```
SELECT product_name, price
FROM products;
```

This retrieves only the product name and price columns.

B. Select all columns

```
SELECT *
FROM products;
```

The `*` (asterisk) represents all columns.

### Important points

- `SELECT` specifies the columns.
- `FROM` specifies the source table.
- `*` selects every column.
- A SELECT query does not modify the original database.

Real-world example: If you only need product names and prices for a report, you don't need to retrieve every column.

# 4. ORDER BY – Sorting Data

Second query concept

## 4.1 What is ORDER BY?

`ORDER BY` sorts query results based on one or more columns.

For example, an e-commerce company wants to see its products ordered by price.

### A. Ascending order (ASC)

```
SELECT *
FROM products
ORDER BY price ASC;
```

This sorts prices from lowest to highest.

Example:

| Product     | Price |
| ----------- | ----- |
| Python Book | 500   |
| Mouse       | 800   |
| T-Shirt     | 1200  |
| Laptop      | 65000 |

`ASC` means ascending order.

It is the default sorting behavior, so you can also write:

```
SELECT *
FROM products
ORDER BY price;
```

### B. Descending order (DESC)

```
SELECT *
FROM products
ORDER BY price DESC;
```

This sorts prices from highest to lowest.

Example:

| Product     | Price |
| ----------- | ----- |
| Laptop      | 65000 |
| T-Shirt     | 1200  |
| Mouse       | 800   |
| Python Book | 500   |

`DESC` means descending order.

### ASC vs DESC

| ASC               | DESC              |
| ----------------- | ----------------- |
| Ascending         | Descending        |
| Lowest to highest | Highest to lowest |
| A to Z            | Z to A            |
| 0 to 9            | 9 to 0            |

### Real-world applications

- Finding the most expensive products.
- Finding the cheapest products.
- Ranking customers by spending.
- Sorting employees by salary.
- Sorting transactions by date.

# 5. LIMIT – Restricting Results

Third query concept

## 5.1 What is LIMIT?

`LIMIT` restricts the number of rows returned by a query.

For example, imagine your products table contains 10,000 records, but you only want to see 10.

```
SELECT *
FROM products
LIMIT 10;
```

This returns a maximum of 10 rows.

### Why do we use LIMIT?

1. Avoid displaying unnecessarily large results.
2. Make initial data exploration easier.
3. Reduce the amount of data transferred to the client.
4. Help inspect large datasets safely.

### LIMIT with ORDER BY

These two concepts become more useful when combined.

Example: Find the five most expensive products.

```
SELECT *
FROM products
ORDER BY price DESC
LIMIT 5;
```

Execution logic:

1. Retrieve product records.
2. Sort them by price in descending order.
3. Return only the first five rows.

PostgreSQL note

`LIMIT` is supported in PostgreSQL and is generally placed at the end of a SELECT query.

# 6. DISTINCT – Finding Unique Values

Fourth query concept

## 6.1 What is DISTINCT?

`DISTINCT` removes duplicate values from the query results.

Imagine the following `products` table:

| product_id | product_name | category    |
| ---------- | ------------ | ----------- |
| 1          | Python Book  | Books       |
| 2          | Laptop       | Electronics |
| 3          | SQL Book     | Books       |
| 4          | Mouse        | Electronics |
| 5          | T-Shirt      | Clothing    |

Suppose you want to identify all available product categories.

### Without DISTINCT

```
SELECT category
FROM products;
```

Output:

| category    |
| ----------- |
| Books       |
| Electronics |
| Books       |
| Electronics |
| Clothing    |

Notice that some categories appear more than once.

### With DISTINCT

```
SELECT DISTINCT category
FROM products;
```

Output:

| category    |
| ----------- |
| Books       |
| Electronics |
| Clothing    |

Now each category appears only once.

### Important rules

- `DISTINCT` is placed immediately after `SELECT`.
- It eliminates duplicate rows from the selected result.
- It does not delete duplicate records from the original database.

### DISTINCT with multiple columns

You can also use DISTINCT with multiple columns.

```
SELECT DISTINCT category, price
FROM products;
```

Here, SQL checks the combination of `category` and `price`.

A row is considered duplicate only when both selected values match.

Real-world applications:

- Finding unique customer cities.
- Identifying available product categories.
- Finding unique transaction types.
- Discovering distinct countries in a dataset.

# 7. AS – Column Aliasing

Fifth query concept

## 7.1 What is an Alias?

An alias is a temporary alternative name given to a column or table in a SQL query.

Think of it as a nickname.

For example, your database has a column named `category`, but you want the result header to display `unique_categories`.

You can use `AS`.

```
SELECT category AS unique_categories
FROM products;
```

Output:

| unique_categories |
| ----------------- |
| Books             |
| Electronics       |
| Books             |
| Electronics       |
| Clothing          |

The original database column is still named `category`.

Only the output column header changes.

## 7.2 AS with DISTINCT

You can combine DISTINCT and AS.

```
SELECT DISTINCT category AS unique_categories
FROM products;
```

Output:

| unique_categories |
| ----------------- |
| Books             |
| Electronics       |
| Clothing          |

This query performs two operations:

1. `DISTINCT` removes duplicate categories.
2. `AS` gives the result column a descriptive name.

## 7.3 Why do we use aliases?

Aliases make query results easier to understand.

For example:

Instead of:

```
SELECT category
FROM products;
```

You can write:

```
SELECT DISTINCT category AS unique_categories
FROM products;
```

This makes the purpose of the output clearer.

### Alias naming conventions

Use descriptive names.

| Good alias        | Poor alias |
| ----------------- | ---------- |
| unique_categories | x          |
| customer_cities   | a          |
| total_revenue     | t          |
| average_price     | p          |

Prefer `snake_case`:

- Use lowercase letters.
- Separate words with underscores.
- Keep names meaningful.

Important: An alias does not permanently rename a database column. It only changes its name in the query result.

# 8. SQL Query Execution Order

Understanding the logical execution order helps you understand how SQL combines different clauses.

Consider:

```
SELECT DISTINCT category AS unique_categories
FROM products
ORDER BY category DESC
LIMIT 3;
```

The logical processing order is:

## SQL logical execution order

1. FROM

   Identifies the source table (`products`).
2. SELECT / DISTINCT processing

   Selects the required column and removes duplicate result rows.
3. ORDER BY

   Sorts the unique categories in descending order.
4. LIMIT

   Restricts the final result to three rows.

Note: This is a simplified logical order for the clauses covered here, not the complete SQL execution model.

# 9. SQL Style Conventions

SQL keywords can be written in uppercase or lowercase.

Both queries are valid:

```
select * from products;
```

```
SELECT * FROM products;
```

However, uppercase SQL keywords are a common convention.

### Recommended style

```
SELECT product_name, price
FROM products
ORDER BY price DESC
LIMIT 5;
```

Why?

- Keywords are easy to identify.
- Queries become easier to read.
- Code becomes easier to maintain.
- Team collaboration becomes easier.

Best practice: Write SQL keywords in uppercase and table/column names in lowercase.

# 10. PostgreSQL and SQL Flavors

## 10.1 What is PostgreSQL?

PostgreSQL is an open-source relational database management system.

It allows applications to store, retrieve, and manage structured data using SQL.

You can use PostgreSQL for:

- Backend applications.
- Data engineering.
- Analytics.
- Machine Learning pipelines.
- Feature stores and MLOps systems.

## 10.2 What are SQL Flavors?

Different database systems implement SQL with some differences.

For example:

| Database             | SQL implementation |
| -------------------- | ------------------ |
| PostgreSQL           | PostgreSQL SQL     |
| MySQL                | MySQL SQL          |
| SQLite               | SQLite SQL         |
| Microsoft SQL Server | T-SQL              |
| Oracle Database      | Oracle SQL         |

The core SQL concepts are transferable between these systems.

However, some syntax and database-specific features differ.

### PostgreSQL example

```
SELECT *
FROM products
LIMIT 10;
```

This retrieves the first 10 rows produced by the query.

### PostgreSQL naming convention

PostgreSQL treats unquoted table and column identifiers as case-insensitive.

For example:

```
SELECT * FROM products;
```

And:

```
SELECT * FROM PRODUCTS;
```

These refer to the same table, assuming it was created without quoted case-sensitive identifiers.

# 11. Client-Server Architecture

## 11.1 What is Client-Server Architecture?

A database connection has two important components:

Database Server

- Stores and manages databases.
- Processes SQL queries.
- Manages data access.
- Handles multiple client connections.

Database Client

- Connects to the database server.
- Sends SQL queries.
- Displays query results.
- Provides an interface for interacting with the database.

## 11.2 How does it work?

[Understanding Databases and SQL: How It Works](https://images.openai.com/static-rsc-4/GlE5ZofaJ-MZboQP9nqpOozvMleVtf6NjiN3xXD-5kQO5M2D8ek-AiW36D2ztziM6Mfce9_d7GZ6vSo8fcreMk8xpGH-WmUIhWS_QGPMd3mQcXZDyIVvZaXSlXRgLFzdZnCWpFpWCNNYnpkFpsArcgQkY4huAvmD5nnafCevHSA?purpose=inline)

[programiz.pro](https://programiz.pro/resources/understanding-databases-sql/?utm_source=chatgpt.com)

Example workflow:

1. You open a SQL client.
2. You connect to a PostgreSQL server.
3. You write a SQL query.
4. The client sends the query to the server.
5. The server processes the query.
6. The server returns the result.
7. The client displays the result.

Multiple clients can connect to the same database server simultaneously, subject to permissions.

## 11.3 PostgreSQL SQL Clients

Two common PostgreSQL clients are:

[Setting up PostgreSQL database in a Docker Container | by Anji Keesari | Medium](https://images.openai.com/static-rsc-4/O_Cond2i2KjEcuE4bViA_IZVBYsCXs8gnOOmY-uBcEdtVgYdewQJiONmQHun1z0_-VeFfgMtxOrmLj2FIuoEGkcihqP7vHS5MPA5TEbB4re_E0HKruuN0azPI9qnJSl7yGJFWPYUGMuvdjvUtVR814BSPQWmL9zz38O-McXlWhc?purpose=inline)

psql

PostgreSQL's command-line client. You interact with the database using terminal commands.

Useful for scripting and command-line workflows.

[Official psql documentation](https://www.postgresql.org/docs/current/app-psql.html?utm_source=chatgpt.com)

[Connect PostgreSQL via PgAdmin 4 SSH Tunnel](https://images.openai.com/static-rsc-4/CwKWaXMrk5kuLMjjd5KRYkC8jObTHDGn0HDsPl6_cYram1p1BnsKhpIx-7UfrNQdOn8pVJTJxJL9LloRd_qn83LZAA7MaFHs97mm2ptaFLbgD15oXXlr9eBy29qj5A7eQEzCYD8YGdY0wnbu5t8sUQ_OuLwoYORUeqtjYN0flog?purpose=inline)

pgAdmin

A graphical interface for managing PostgreSQL databases and executing SQL queries.

Useful for visual database management.

[Official pgAdmin documentation](https://www.pgadmin.org/docs/?utm_source=chatgpt.com)

## 11.4 What information is required to connect?

Typically, you need:

| Parameter | Meaning                                 |
| --------- | --------------------------------------- |
| Host      | Database server address                 |
| Port      | Network port (PostgreSQL default: 5432) |
| Username  | Database user                           |
| Password  | User authentication                     |
| Database  | Database name                           |

For example:

```
psql -h localhost -p 5432 -U postgres -d ecommerce
```

This connects to the `ecommerce` database on the local PostgreSQL server.

# 12. Complete SQL Query Cheat Sheet

Here are the concepts in their learning sequence.

| Serial | Concept  | Purpose                      |
| ------ | -------- | ---------------------------- |
| 1      | SELECT   | Select specific columns      |
| 2      | FROM     | Specify the source table     |
| 3      | ORDER BY | Sort query results           |
| 4      | ASC      | Sort in ascending order      |
| 5      | DESC     | Sort in descending order     |
| 6      | LIMIT    | Restrict the number of rows  |
| 7      | DISTINCT | Remove duplicate result rows |
| 8      | AS       | Assign a temporary alias     |

## One example for each query

1\. SELECT – Retrieve specific columns

```
SELECT product_name
FROM products;
```

2\. SELECT \* – Retrieve all columns

```
SELECT *
FROM products;
```

3\. ORDER BY – Sort data

```
SELECT *
FROM products
ORDER BY price;
```

4\. DESC – Sort from highest to lowest

```
SELECT *
FROM products
ORDER BY price DESC;
```

5\. LIMIT – Return only five rows

```
SELECT *
FROM products
LIMIT 5;
```

6\. DISTINCT – Retrieve unique categories

```
SELECT DISTINCT category
FROM products;
```

7\. AS – Rename an output column

```
SELECT category AS product_category
FROM products;
```

8\. Combined query – Apply multiple concepts

```
SELECT DISTINCT category AS unique_categories
FROM products
ORDER BY category ASC
LIMIT 5;
```

# 13. Practice Exercises

Try these exercises using PostgreSQL.

Assume you have a table called `products`.

| product_id | product_name | category    | price |
| ---------- | ------------ | ----------- | ----- |
| 1          | Python Book  | Books       | 500   |
| 2          | Laptop       | Electronics | 65000 |
| 3          | SQL Book     | Books       | 700   |
| 4          | Mouse        | Electronics | 800   |
| 5          | T-Shirt      | Clothing    | 1200  |
| 6          | Keyboard     | Electronics | 1500  |

Test your SQL knowledge

0/7 revealed

Exercise 1. Retrieve all columns from the products table.

Show solution

Exercise 2. Retrieve only product_name and price.

Show solution

Exercise 3. Sort products by price from highest to lowest.

Show solution

Exercise 4. Show only the first three products.

Show solution

Exercise 5. Find all unique product categories.

Show solution

Exercise 6. Find unique categories and name the output column unique_categories.

Show solution

Exercise 7. Find the three cheapest products.

Show solution

# 14. Key Takeaways

1. SELECT retrieves the columns you need.
2. FROM identifies the table.
3. ORDER BY sorts the returned rows.
4. DESC sorts from highest to lowest.
5. LIMIT controls how many rows are returned.
6. DISTINCT removes duplicate result rows.
7. AS provides temporary names for columns or tables.
8. SQL keywords are conventionally written in uppercase.
9. PostgreSQL is one implementation of SQL.
10. A database server processes queries, while a client sends queries and displays results.

Recommended learning order: Master SELECT and FROM first, then ORDER BY, ASC/DESC, LIMIT, DISTINCT, and finally AS. After that, practice combining them into a single query.

For your MLOps and DataOps work, these are foundational skills for exploring datasets, inspecting feature tables, and querying information from PostgreSQL.