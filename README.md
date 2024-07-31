
# Project 12 python : EPIC

Epic is a command line application for an event society. Depending on their roles, users will have the option to create clients, contracts or events. 



## Installation

Install Epic Project with with git clone

```bash
  git clone https://github.com/elchoup/Epic.git
```

Then go in the repository 

```bash
cd Epic
```

Start your virtual env and install the requirements 

```bash
pip install -r requirements.txt
```

Initialize the database 

```bash
python -m crm.create_table.py
```


    
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file.
You can use the .env_exemple file recalling it .env

`SECRET_KEY`



## Run

To run this project

```bash
  python -m crm --help
```

Then you have access to the differents command line you can use in this app

