[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
## octopus-energy-sql
Grabs data from the Octopus Energy Public API, a UK energy supplier and puts it into an SQL Table.
From there I'm using [Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/) to make pretty graphs. I will also include the config JSON for Grafana and provided all the table names and columns match the below, then yours will look like mine as a baseline for you to edit.

## Getting started
Most of this was inspired by this fantastic tutorial by Guy Lipman [guylipman.medium.com](https://guylipman.medium.com/accessing-your-octopus-smart-meter-data-3f3905ca8fec).
There you will find concise information on how the finer nuances of the API works, issues with BST vs GMT times and lots of other useful information. 
As well as where to find all the account information the _config.py file needs to make it work for your unique details.

### I am by no means a professional programmer. Infact, I am a rank amateur and just have access to a linux based home server that I play with for fun home-automation projects.
This means that I make no guarantees on the security, viability or suitability of the code in any capacity. You should never blindly copy and paste code from the internet that you do not fully understand.
That being said, I'm making some assumptions of your preparation and this readme is in no way a complete guide in how to get all this off of the ground.

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
## Grafana JSON
This is the JSON that I'm using for my graphs
[JSON File for Import()

