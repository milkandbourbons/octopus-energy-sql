[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
## octopus-energy-sql
Grabs data from the Octopus Energy Public API, a UK energy supplier and puts it into an SQL Table.
From there I'm using [Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/) to make pretty graphs. I will also include the config JSON for Grafana and provided all the table names and columns match the below, then yours will look like mine as a baseline for you to edit.

## Creating the SQL Table

``` sql
CREATE DATABASE octopus;
```
## Creating the required tables and columns
Execute this inside the octopus database you created in the previous step.
``` sql
CREATE TABLE electricity (
    id int NOT NULL AUTO_INCREMENT,
    kwh float,
    high_price float,
    low_price float,
    standing_charge float,
    start_time datetime,
    end_time datetime,
    cost float,
    rate TEXT,
    car_charge_cost float NULL,
    summer_time tinyint(1).
    
    PRIMARY KEY (id)
);
```


