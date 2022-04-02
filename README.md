# SIoT DE4 project repository

This repository contains all the code required to run the IoT sleep monitoring system designed and is divided in the following folders

## API_PHP
This folder contains PHP scripts that connect to the Withings API in order to obtain access keys and tokens as well as data from the Sleep Analyzer.

## Arduino
This folder contains the scripts that acquire data from a photoresistor (light) and a DHT22 sensor (temperature and humidity) and connect to a MongoDB database.

## Data_analysis
This folder contains the data cleaning pipeline as well as all the data anlaysis scripts and notebooks.

## Flask
Unfinished flask code to create a web app.

## Output_data
This folder contains the local versions of the datasets stored on the Cloud in order to perform analytics when offline.

## Scraping
This folder contains the scraping script used to retrieve information from the Withings web app.
