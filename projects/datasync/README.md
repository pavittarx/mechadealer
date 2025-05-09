# DataSyncer
This project layer deals will syncing maket data from multiple sources into QuestDB.

These sources are currently supported 
- Indian Markets: Upstox

- The project only stores 1M market data which can than be resampled into higher timeframes. 

## Instructions to run 
Run prefect server with

```sh
  prefect server start
```

and, while the server is running

```sh
  uv run main.py
```

Both of these processes needs to run, in order for the project to be working.  

## Technologies Used
- Python (Core Logic i.e, Pull Data, Interact with tooling)
- Prefect (Workflow Orchestration and Scheduling)
- QuestDB (Market Data Storage)

### Why QuestDb? 
QuestDb is super-fast and efficient way to store and quickly analyze large amounts of constantly updating financial information, like stock prices. 
It's designed specifically for this kind of data, making it much quicker to get insights compared to general-purpose databases, and it uses a familiar language (SQL) to access the information.


### Why Prefect?
Prefect is a workflow orchestration tool that allows you to easily create, schedule, and monitor complex data pipelines. 
It's designed to make it easy to build and maintain data pipelines, and it's built on top of Python, which makes it easy to integrate with your existing Python code.