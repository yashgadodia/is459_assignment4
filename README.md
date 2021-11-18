# SMU-IS459

- I have decided to use mongodb as the data store for the top author per window, similar to in assignment 3 before visualising it in the django application

- Ensure you have Kafka, Zookeeper, DFS, Mongodb and any other 'base' dependencies up


Assignment 4:

- Run the Scrapy crawler by running ```scrapy crawl hardwarezone``` from hardwarezone folder
- Run ```/usr/local/bin/spark-submit  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2 --class mongo-java-driver-3.9.0,mongo-spark-connector_2.12-3.0.1 assignment_4.py``` from the spark folder to get the author in batches.
- Run ```pip install pymongo && pip install mongoengine``` 
- Run ```python manage.py runserver``` from hwz_monitor folder to start the django app.
- From your localhost:8000 navigate to /dashboard/barchart path to see the visualisations.