from confluent_kafka import Consumer, KafkaException, KafkaError

# Configure the Kafka consumer
conf = {
    'bootstrap.servers': '0.tcp.ngrok.io:11281',  # Use your ngrok address without 'tcp://'
    'group.id': 'my_consumer_group',              # Set a consumer group ID
    'auto.offset.reset': 'earliest'                # Start reading at the earliest message
}

# Create a Kafka consumer
consumer = Consumer(conf)

# Subscribe to the desired Kafka topic
topic = 'postgres.public.checking_account'  # Replace with your topic name
consumer.subscribe([topic])

try:
    while True:
        # Poll for new messages
        msg = consumer.poll(1.0)  # Wait for a message for 1 second
        if msg is None:
            continue  # No message available
        if msg.error():
            # Handle any error that occurs
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition, continue
                continue
            else:
                raise KafkaException(msg.error())

        # Print the message
        print(f"Received message: {msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    print("Consumer interrupted by user.")

finally:
    # Close the consumer to release resources
    consumer.close()