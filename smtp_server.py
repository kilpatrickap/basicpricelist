from aiosmtpd.controller import Controller

class PrintMessageHandler:
    async def handle_DATA(self, server, session, envelope):
        print(f"Message from {envelope.mail_from} to {envelope.rcpt_tos}")
        print("Message content:")
        print(envelope.content.decode('utf8', errors='replace'))  # Decoding the message
        return '250 Message accepted for delivery'

# Set up and start the server
handler = PrintMessageHandler()
controller = Controller(handler, hostname='localhost', port=1025)
controller.start()

print("SMTP server is running on localhost:1025...")
try:
    input("Press Enter to stop the server...\n")
finally:
    controller.stop()
