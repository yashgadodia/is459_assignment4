from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import explode
from pyspark.sql.functions import split, concat_ws, substring, from_json, col, lower, regexp_replace, window, current_timestamp, desc
from pyspark.ml.feature import StopWordsRemover, RegexTokenizer, Tokenizer

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.users

# working_directory = ''

if __name__ == "__main__":
    
    spark = SparkSession.builder \
               .appName("KafkaWordCount") \
               .getOrCreate()

    #Read from Kafka's topic scrapy-output
    df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "scrapy-output") \
            .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", "false") \
            .load()

    #Parse the fields in the value column of the message
    lines = df.selectExpr("CAST(value AS STRING)", "timestamp")

    #Specify the schema of the fields
    hardwarezoneSchema = StructType([ \
        StructField("topic", StringType()), \
        StructField("author", StringType()), \
        StructField("content", StringType()) \
        ])

    #Use the function to parse the fields
    # lines = parse_data_from_kafka_message(lines, hardwarezoneSchema) \
    #     .select("topic","author","content","timestamp")
    lines = lines.withColumn('data', from_json(col("value"), schema=hardwarezoneSchema)).select('timestamp', 'data.*')


    # Top-10 users with most posts in 2 minutes

    users_df = lines.select("timestamp", "author") \
        .withWatermark('timestamp', "2 minutes") \
        .groupBy(window("timestamp", "2 minutes", "1 minute"), "author").count() \
        .withColumn("start", col("window")["start"]) \
        .withColumn("end", col("window")["end"]) \
        .withColumn("current_timestamp", current_timestamp())

    users_df = users_df.filter(users_df.end < users_df.current_timestamp)

    # # remove stop words and punctuations

    # punct = lines.select('timestamp', split(lower(regexp_replace('content', r'[^\w\s]',''))," ").alias('content'))
    # stopwordList = (["\n","\t", "content", "click", "expand", "", " ", "..."])
    # stopwordList.extend(StopWordsRemover().getStopWords())
    # stopwordList = list(set(stopwordList))
    # remover = StopWordsRemover(inputCol='content', outputCol="cleaned_content", stopWords=stopwordList)
    # cleaned_df = remover.transform(punct)


    # # Splitting into individual words
    # cleaned_df = cleaned_df.select("timestamp", concat_ws(" ", "cleaned_content").alias("individual_word")) \
    #     .select("timestamp", explode(split("individual_word", " ")).alias("content")) \
    #     .groupBy(window("timestamp", "2 minutes", "1 minute"), "content").count() \
    #     .withColumn("start", col('window')['start']) \
    #     .withColumn("end", col('window')['end']) \
    #     .withColumn("current_timestamp", current_timestamp()) 

    # cleaned_df = cleaned_df.filter(cleaned_df.end < cleaned_df.current_timestamp) \
    #     .orderBy('window', 'count', ascending=False).limit(10)

    # {'window': Row(start=datetime.datetime(2021, 11, 18, 21, 34), 
    #  end=datetime.datetime(2021, 11, 18, 21, 36)), 
    #  'author': 'stevenyeo123', 'count': 2, 
    # 'start': datetime.datetime(2021, 11, 18, 21, 34), 
    # 'end': datetime.datetime(2021, 11, 18, 21, 36),
    #  'current_timestamp': datetime.datetime(2021, 11, 18, 21, 44, 0, 75000)}

    # save to mongo db
    def save(users_df, epoch_id):
        list_df = map(lambda row: row.asDict(), users_df.collect())
        for row in list_df:
            author = row['author']
            count = row['count']
            collection = db.users
            collection.update_one({'author': author}, {'$inc': {'count': count}, '$set': {k:v for k,v in row.items() if k != "count"}}, upsert=True)
        
        # users_df.write \
        #     .format("com.mongodb.spark.sql.DefaultSource") \
        #     .mode("append") \
        #     .option("database", "users") \
        #     .option("collection", "users") \
        #     .save()

        pass

    # #Select the content field and output
    contents1 = users_df \
        .writeStream \
        .queryName("WriteContent1") \
        .trigger(processingTime="1 minute") \
        .outputMode("append") \
        .option("checkpointLocation", "/Users/yash/spark-checkpoint1") \
        .foreachBatch(save) \
        .start()
    
    #Start the job and wait for the incoming messages
    contents1.awaitTermination()
