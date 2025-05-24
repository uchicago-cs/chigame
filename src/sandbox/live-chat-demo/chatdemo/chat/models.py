"""
No models are needed for the demo app as all of the messages are not stored but rather sent to the client.

This is done through Django channels and the `group_send` method.

Check out the `consumers.py` file to see how this is done.
"""
