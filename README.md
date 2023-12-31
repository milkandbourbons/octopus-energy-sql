
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
# octopus-energy-sql
***This is under heavy development.***

Grabs data from the Octopus Energy Public API, a UK energy supplier buit for EV's, and puts it into an SQL Table.
From there I'm using [Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/) to make pretty graphs. I will also include the config JSON for Grafana and provided all the table names and columns match the below, then yours will look like mine as a baseline for you to edit.
![Screenshot 2023-11-07 110212](https://github.com/milkandbourbons/octopus-energy-sql/assets/47081499/0f17c430-3cb8-4cbe-92a3-f225267fe566)
<sup>some data is missing from the screen shot on the previous month becuase I only joined Octopus in october 2023</sup>
## Getting started
Please see the [Releases](https://github.com/milkandbourbons/octopus-energy-sql/releases) page for the latest version. Each version has a grafana JSON file too as the graphs develop.
Inspiration for the project was found reading [Octopus' Blog](https://octopus.energy/blog/agile-smart-home-diy/).

## 3rd Party Software
As well as a place to run the Python script (Raspberry Pi or Home Server or "Linode" are popular options), you will also need access to these free bits of software:
- Basic webserver for accessing the below
- SQL Server / Database. My usecase is [phpmyadmin](https://www.phpmyadmin.net/) which is a lighweight and simple to use PHP based front end for interracting with your database
- [Grafana](https://grafana.com/grafana/). This uses a data connection to the SQL Database and draws pretty graphs in a webpage which can be accessed locally or globally. 

Most of this was enabled by this fantastic [handy API guide](https://www.guylipman.com/octopus/api_guide.html) by Guy Lipman.
There you will find concise information on how the finer nuances of the API works, issues with BST vs GMT times and lots of other useful information. 
As well as where to find all the account information the _config.py file needs to make it work for your unique details.
Octopus Energy also have their own API documentation [found here](https://developer.octopus.energy/docs/api/), but every now and again the site errors out with a 500 server error. Just try again in a few minutes.

***I am by no means a professional programmer. Infact, I am a rank amateur and just have access to a linux based home server that I play with for fun home-automation projects.
This means that I make no guarantees on the security, viability or suitability of the code in any capacity. You should never blindly copy and paste code from the internet that you do not fully understand.
That being said, I'm making some assumptions of your preparation and this readme is in no way a complete guide in how to get all this off of the ground.***

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
### Step 1
First navigate to [http://x.x.x.x/phpmyadmin/index.php?route=/server/databases&server=1](http://x.x.x.x/phpmyadmin/index.php?route=/server/databases&server=1)
and under "Create Database", type "octopus" and click "create".

![Screenshot 2023-11-07 132504](https://github.com/milkandbourbons/octopus-energy-sql/assets/47081499/1f81e26c-6854-44e1-acda-fc1eda45c2aa)

### Step 2
Navigate to [http://x.x.x.x/phpmyadmin/index.php?route=/database/structure&db=octopus](http://x.x.x.x/phpmyadmin/index.php?route=/database/structure&db=octopus)
And create a table called "electricity" with 14 columns.

![Screenshot 2023-11-07 132655](https://github.com/milkandbourbons/octopus-energy-sql/assets/47081499/2f515d1f-9935-4de9-ac6b-442278da7e9b)


### Step 3
Create the columns with the exact column names as shown, or if you're feeling a little more advanced, use the sql syntax below.
![Screenshot 2023-11-07 133315](https://github.com/milkandbourbons/octopus-energy-sql/assets/47081499/9a8fc1aa-9233-47df-be29-270aff1cb881)
>Hint:
>to enable "auto increment" on the id column, its the tickbox labelled "A_I", as you hover over it, a tooltip is displayed confirming "AutoIncrement"

### Step Advanced 1 <sub>(quicker, less prone to mitstakes)</sub>
At [http://x.x.x.x/phpmyadmin/index.php?route=/server/sql](http://x.x.x.x/phpmyadmin/index.php?route=/server/sql)
Enter:
``` sql
CREATE DATABASE octopus;
```
### Step Advanced 2
At [http://x.x.x.x/phpmyadmin/index.php?route=/server/sql&db=octopus](http://x.x.x.x/phpmyadmin/index.php?route=/server/sql&db=octopus)
To create the electricity storage table, enter:
``` sql
CREATE TABLE electricity (
    id int NOT NULL AUTO_INCREMENT,
    kwh float NULL,
    high_price float NULL,
    low_price float NULL,
    current_price float NULL,
    standing_charge float NULL,
    start_time datetime NULL,
    end_time datetime NULL,
    cost float NULL,
    rate TEXT NULL,
    car_charge_cost float NULL,
    bump_charge_cost float NULL,
    threshold float NULL,
    summer_time tinyint(1) NULL,
    
    PRIMARY KEY (id)
);
```
### Step Advanced 3
At [http://x.x.x.x/phpmyadmin/index.php?route=/server/sql&db=octopus](http://x.x.x.x/phpmyadmin/index.php?route=/server/sql&db=octopus)
To create the gas storage table, enter:
``` sql
CREATE TABLE gas (
    id int NOT NULL AUTO_INCREMENT,
    gas_kwh float NULL,
    start_time datetime NULL,
    end_time datetime NULL,
    standing_charge float NULL,
    cost float NULL,
    gas_price NULL,
    
    PRIMARY KEY (id)
);
```
## Grafana JSON
This is the JSON that I'm using for my graphs
[JSON File for Import](https://github.com/milkandbourbons/octopus-energy-sql/blob/main/grafana_graphs.json)

