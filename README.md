[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
## octopus-energy-sql
Grabs data from the Octopus Energy Public API, a UK energy supplier and puts it into an SQL Table.
From there I'm using [Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/) to make pretty graphs. I will also include the config JSON for Grafana and provided all the table names and columns match the below, then yours will look like mine as a baseline for you to edit.

## Getting started
Inspiration for the project was found reading [Octopus' Blog](https://octopus.energy/blog/agile-smart-home-diy/).

Most of this was enabled by this fantastic [handy API guide](https://www.guylipman.com/octopus/api_guide.html) by Guy Lipman.
There you will find concise information on how the finer nuances of the API works, issues with BST vs GMT times and lots of other useful information. 
As well as where to find all the account information the _config.py file needs to make it work for your unique details.
Octopus Energy also have their own API documentation [found here](https://developer.octopus.energy/docs/api/), but every now and again the site errors out with a 500 server error. Just try again in a few minutes.

### I am by no means a professional programmer. Infact, I am a rank amateur and just have access to a linux based home server that I play with for fun home-automation projects.
This means that I make no guarantees on the security, viability or suitability of the code in any capacity. You should never blindly copy and paste code from the internet that you do not fully understand.
That being said, I'm making some assumptions of your preparation and this readme is in no way a complete guide in how to get all this off of the ground.

## Octopus Information
Your API KEY is found here on [Octopus' Website](https://octopus.energy/dashboard/new/accounts/personal-details/api-access).
Your Octopus Account number is a code like A-ABCD1234
When figuring out your product and tariff codes, remember that they _are different_ and when you summon your account details first with:
https://api.octopus.energy/v1/products/GO-VAR-BB-23-02-07/ (if you're on octopus GO)
Then the tariff code is contained in your customer data, which you will need you API KEY to access.
In my case "E-1R-GO-VAR-BB-23-02-07-D"

You can use, again, Guy Lipman's [web tool for requesting your account data](https://www.guylipman.com/octopus/generic.html), if you're unfamiliar with curl requests. 
Paste the output on the page into a code prettifier like [this one](https://jsonbeautifier.org/) to make it a little more human readable.

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
[JSON File for Import](https://github.com/milkandbourbons/octopus-energy-sql/blob/main/grafana_graphs.json)

