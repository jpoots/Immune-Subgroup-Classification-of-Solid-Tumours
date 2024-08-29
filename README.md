<div align="center">
    <img src="https://i.ibb.co/55DH349/logo.png" width=200 alt="logo" border="0"> 
</div>

# ICST: Immune Subgroup Classification for Solid Tumours

## Overview

ICST is a machine learning based web app for immune subgroup classification of solid tumour based upon 440 key genes developed by Jordan Poots in concert with research performed by Dr Reza Rafiee. This app was produced in partial fulfillment of MSc Software Development at Queen's University Belfast.

The <a href="http://analytics.eeecs.qub.ac.uk/icst">web app</a> and <a href="http://analytics.eeecs.qub.ac.uk:8080">API </a> may be accessed at the linked location when on a wired connection to the Queen's University network. Instructions for local usage are given below.

> **Note:** This repository contains large file. Make sure to use git lfs install, git lfs fetch and git lfs pull with git lfs installed to the system to pull large files.

## Table of Contents

1. [Description](#Description)
2. [Requirements](#Requirements)
3. [Installation](#Installation)
4. [Web App Usage](#Web-App-Usage)
5. [Model Development Usage](#Model-Development-Usage)
6. [Additional Folders](#Additional-Folders)
7. [Contact](#Contact)

## Description

Pioneering cancer research has identified six immune subgroups, clustered on tumour gene data including RNA-Seq gene expression using unsupervised machine learning clustering on over 10,000 samples taken from The Cancer Genome Atlas (TCGA) across 33 cancer types in the paper <a href="https://pubmed.ncbi.nlm.nih.gov/29628290/"> The Immune Landscape of Cancer</a>.

ICST is the first publicly available tool for classifying new samples based upon the 440 key genes identified in the above paper using a supervised gradient boosting machine learning model. In addition, Dr Rafiee suggests a 7th subgroup for samples which fall between subgroups. Contained in this repository is the model development scripts for reproduction of results, the Flask API and the React frontend. Setup and start scripts are also included for these along with some results produced by the model, test data and the models evaluation data as discussed in the accompanying report.

Full discussion of the function of each file is contained in the accompanying report.

## Requirements

The project has been tested for the following configurations. Additional configurations may function successfully but the developer does not guarentee this.

All requirements can be installed using the provided scripts. If a script fails for your system, you may manually install the requirements as below. It is assumed Python3 is already installed on the system along with the Brew package manager for MacOS and venv. The software was tested using Python 3.10.

- **OS:** Any system which supports Docker
- **Software:**
  - Node.js 20
  - Docker

## Installation
This tutorial assumes you have Docker installed on your system. Installation scripts are given in other/installation_scripts. All scripts must be made executable using the chmod +x command. All steps may be performed manually as desired. Scripts should be executed in the below order.

### install_node_OS.sh

Before installing the app, ensure the relevant version of node is installed. This can be manually installed or installed using the install_node_OS.sh for your OS.


### setupAPI.sh

This script builds the Docker contain and initalises the database with a gene list and legacy credentials of "admin" and "pass".

### setupFrontend.sh

This script installs the react apps requirements using NPM, builds the app and serves the build in preview mode.

## Web App Usage

Usage scripts are given in other/start_scripts. These scripts are used to start a celery worker, Redis, MySQL and the Flask API on a Gunicorn server as well as serve the React app. These actions may be performed manually if desired.

### api.sh

This script starts the API and serves it on port 3000 using Gunicorn. A Redis in-memory database is started and MySQL also listens.

### frontend.sh

This script serves the react front end

## Model Development Usage

Navigate to the model \_development folder and install the requirements.txt in your virtual environment of choice using

```bash
pip install -r requirements.txt
```

Navigate to the folder containing the relevant script and run using

```bash
python3 foo_bar.py
```

## Additional Folders

### prototype_web_apps

This is a small collection of trialled web app systems as discussed in the accompanying report. They are presevered as evidence of experimentation but do not reflect the developers best coding practices.

### other/test_data

A collection of CSV and JSON files for testing and demonstrating the functionality of the API and web app. An explanation of the contents of each file is given by its name. More detailed explanation can be found in the testing section of the accompanying report.

### other/unclassified_samples_results

The results produced by the app on over 1000 previously unclassifed samples across tow sets provided by Dr Reza Rafiee.

### model_development/probability_reports

Probability evaluation for the two gradient boosting models trialled in the model development process.

## Contact

Project Developer - Jordan Poots: jpoots04@qub.ac.uk

Project Supervisor - Dr Reza Rafiee: g.rafiee@qub.ac.uk
