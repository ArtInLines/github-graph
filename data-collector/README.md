## Setup

To run the project locally, you need to have a [neo4j](https://neo4j.com/) database and [python](https://www.python.org/) installed.

Next, you need to install all required python dependencies. You can optionally also setup and activate a virtual environment first. In any case, you should run:

```console
> python -m pip install -r requirements.txt
```

Next, you need to setup the environment variables. To do so, create a file named `.env` in the root folder of this project. You need to provide the following variables in that file:

```env
API_TOKEN=<Your Github API Tokens seperated by commas>
DB_URI=<Your neo4j's URI>
DB_USER=<Your Username for accessing the neo4j Database>
DB_PASS=<Your Password for accessing the neo4j Database>
```

With this setup complete, you can finally run the program then:

```console
> python main.py
```