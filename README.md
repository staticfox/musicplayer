# Music player

### What is this?

Something I scraped together for the sole purpose of allowing a friend's holiday music to play on a schedule with a web UI. It basically reads MP3 files from a defined directory and plays them in a random order.

### What is missing?

The UI itself is extremely basic and there is no way to configure the schedule.

### Running

```
flask run --no-reload -h 0.0.0.0 -p 4300
```

### Notes

This project is not thread safe. It goes against a lot of best practicies as a trade off for simplicity. This project is meant to be run on a raspberry pi or home server.
