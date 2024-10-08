from confluent_kafka import Consumer, KafkaError
import json
import datetime
import struct

def hex_to_float(hex_string):
    # Remove the '0x' prefix if present
    hex_string = hex_string.lstrip('0x')

    # Ensure the length is even (hex strings are 2-char per byte)
    if len(hex_string) % 2 != 0:
        raise ValueError("Invalid hexadecimal string")

    # Convert hex string to bytes
    bytes_obj = bytes.fromhex(hex_string)

    # Use struct.unpack to convert bytes to float
    float_val = struct.unpack('<f', bytes_obj)[0]

    return float_val

# Kafka consumer configuration
conf = {
    'bootstrap.servers': '0.tcp.ngrok.io:11281',
    'group.id': 'group_file_saver',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

# Subscribe to the Kafka topics
topic = "postgres.public.checking_account"
consumer.subscribe([topic])

# Open a file to write the Kafka messages
with open('kafka_messages_checking_account.json', 'w') as file:
    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            # Parse the message value and write it to the file
            if msg.value() is not None:
                message_value = json.loads(msg.value().decode('utf-8'))
                payload = message_value.get('payload', {})
                after = payload.get('after', {})
                if 'date' in after:
                    after['date'] = str(datetime.datetime.utcfromtimestamp(after['date'] * 86400).date())
                if 'datetime_created' in after:
                    after['datetime_created'] = str(datetime.datetime.utcfromtimestamp(after['datetime_created'] / 1e6))
                if 'datetime_updated' in after:
                    after['datetime_updated'] = str(datetime.datetime.utcfromtimestamp(after['datetime_updated'] / 1e6))
                if 'updt_ts' in after:
                    after['updt_ts'] = str(datetime.datetime.utcfromtimestamp(after['updt_ts'] / 1e6))
                # if 'txn_amount' in after:
                #     after['txn_amount'] = hex_to_float(after['txn_amount'])
                # if 'initial_balance' in after:
                #     after['initial_balance'] = hex_to_float(after['initial_balance'])

                json.dump(message_value, file)
                file.write('\n')

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
