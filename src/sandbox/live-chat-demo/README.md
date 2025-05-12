# Live Chat Demo

This is a demo of a live chat Django application. This was the initial implementation of what is now the `/chat` app.

If you'd like to better understand how the `/chat` app works, this is a good place to start. It covers the basics of `consumers.py` as well as channel configuration without all of the additional complexity of the `/chat` app.

## Libraries

`channels` was used to handle the WebSocket connections.

`daphne` was used to run the development server.

## Views

`index` - The main page for the chat.

## How to Demo

1. `python manage.py runserver`

2. Open `http://localhost:8000/`

3. Open multiple tabs

4. Send messages from one tab and see them in the other tabs.
