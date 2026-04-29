# SQL Agent Example Questions

Below are example questions you can ask the SQL Agent about the Chinook database:

## Sales Analysis

- "Who was the best-selling sales agent in 2010?"
- "What are the total sales for each year?"
- "Which sales agent has the highest total sales across all time?"
- "Show me monthly sales for 2011"

## Customer Insights

- "How many customers are from Brazil?"
- "List the top 10 customers by total purchase amount"
- "Which country has the most customers?"
- "Show me customers who have spent more than $40"

## Music Catalog

- "List the top 3 albums by sales"
- "How many tracks are in the database?"
- "Which artist has the most albums?"
- "What are the different music genres available?"
- "Show me all albums by Led Zeppelin"

## Artist & Album Rankings

- "Who are the top 5 best-selling artists?"
- "Which album has the most tracks?"
- "List all albums released by year"

## Invoice Analysis

- "What is the average invoice total?"
- "Show me the largest invoice"
- "How many invoices were created in 2012?"
- "What is the total revenue for all time?"

## Geographic Analysis

- "Which countries generate the most revenue?"
- "List all cities with customers"
- "Show me sales by country"

## Format & Media

- "What media types are available?"
- "How many tracks are in MP3 format?"
- "Which playlist has the most tracks?"

## Custom Queries

You can also ask complex questions like:

- "Compare sales between USA and Canada"
- "Show me the 5 most expensive tracks"
- "Which genre generates the most revenue?"
- "List all employees and their titles"

## Modifying Questions

To change the default question, edit `compose.yaml`:

```yaml
agent:
  environment:
    - QUESTION=Your custom question here
```

Then restart the services:

```bash
docker compose down
docker compose up
```
