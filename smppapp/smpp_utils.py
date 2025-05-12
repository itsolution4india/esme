import smpplib.client
import smpplib.consts
import threading
import logging

# Enable debug logging for troubleshooting
logging.basicConfig(level=logging.DEBUG)

def smpp_bind(ip, port, username, password, system_type, bind_mode):
    client = smpplib.client.Client(ip, port, allow_unknown_opt_params=True)
    try:
        client.connect()
        
        # Bind as Transceiver (Preferred)
        if bind_mode == 'TX':
            response = client.bind_transmitter(system_id=username, password=password, system_type=system_type)
        elif bind_mode == 'RX':
            response = client.bind_receiver(system_id=username, password=password, system_type=system_type)
        else:  # TRX mode
            response = client.bind_transceiver(system_id=username, password=password, system_type=system_type)
        
        if response:
            print(f"Bind Success: {response}")
            
            # Start listening thread for incoming PDUs (automatically handles enquire_link)
            start_listener(client)
            
            return client
        else:
            raise Exception("Failed to bind the SMPP client.")
    except Exception as e:
        print(f"Error during SMPP binding: {e}")
        return None

def start_listener(client):
    """Starts the listener thread which handles incoming PDUs and processes delivery reports."""
    
    def handle_deliver_sm(pdu):
        """Handles incoming delivery receipts and extracts status information."""
        try:
            message_status = None
            short_message = pdu.short_message.decode(errors="ignore")

            # Extract delivery receipt details
            if 'stat:' in short_message:
                parts = short_message.split()
                for part in parts:
                    if part.startswith('stat:'):
                        message_status = part.split(':')[1]
                        break

            print(f"Received DLR: Status={message_status}, Full Response={short_message}")

        except Exception as e:
            print(f"Error processing DLR: {e}")

    def custom_error_handler(pdu):
        if pdu.status == 901:
            print(f"Custom error handler: Received error code 901: {pdu}")
        else:
            print(f"Unhandled error PDU received: {pdu}")

    client.error_pdu_handler = custom_error_handler
    # Assign the custom deliver_sm handler
    client.set_message_received_handler(handle_deliver_sm)

    # Start listening for incoming PDUs
    thread = threading.Thread(target=client.listen, kwargs={'auto_send_enquire_link': True}, daemon=True)
    thread.start()
    print("Listener thread started, waiting for DLRs...")


def send_sms(client, sender, recipient, message, entity_id, template_id):
    try:
        print(f"Sending SMS from {sender} to {recipient}: {message}")

        # Include Entity ID and Template ID in the message payload
        
        encoded_entity_id = entity_id.encode('ascii')
        encoded_template_id = template_id.encode('ascii')
        print(len(encoded_entity_id))
        tlv_data = {
            5120: encoded_entity_id,  # Entity ID (0x1400)
            5121: encoded_template_id,  # Template ID (0x1401)
        }

        pdu = client.send_message(
            source_addr_ton=smpplib.consts.SMPP_TON_NATNL,
            source_addr=sender,
            dest_addr_ton=smpplib.consts.SMPP_TON_NATNL,
            destination_addr=recipient,
            short_message=message.encode('utf-8'),
            data_coding=0,
            esm_class=0,
            registered_delivery=True,

            optional_parameters=[
                {'tag': 0x1400, 'value': encoded_entity_id},  # Entity ID
                {'tag': 0x1401, 'value': encoded_template_id},  # Template ID
            ]
        )

        print(f"Message sent successfully! Response: {pdu}")
        return pdu

    except Exception as e:
        print(f"An error occurred while sending SMS: {e}")
        return f"Error: {str(e)}"