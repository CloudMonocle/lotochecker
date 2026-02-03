# Loto Checker

[![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
[![Build Status](https://img.shields.io/github/workflow/status/CloudMonocle/lotochecker/CI)](https://github.com/CloudMonocle/lotochecker/actions)

## 🚀 Overview

An fun little project for me to, send notifications to my AWS SNS (Simple Notifcation Service) with the winning nummbers from the Lottory but then compare them to my numners stored in an SSM pramater.

### YouTube Video

!!!Linkt to Video !!!

## 🛠️ Features

- Returning Data from the lottry site
- Checking Numbers
- Sending to my AWS SNS service (created else where)

## 📦 Installation

Deployed using Terrform envirouments, but is setup to run in my enviroument, so you need to update/disable the backend and update the terraform.tfvars

- Create an sns topic and secription
- cd to terraform
- terraform init -backend-config=config/**enviroument**/backend.conf
- terraform paln/apply -backend-config=config/**enviroument**/terraform.tfvars

## 📝 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

> ⭐️ Don’t forget to star this repo if you like it!
