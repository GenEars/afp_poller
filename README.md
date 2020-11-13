# afp_poller

Gathering and displaying AFP news on an local newsboard.

Targetted systems:
* [X] Windows10,
* [ ] Linux Ubuntu,
* [ ] Angstrom v2016.12 on Chameleon96 board.

## Usage

### Get news

Call the poller each time you need:
```
# CLI on Windows and Linux like
python afp_poller.py
```

Data is saved on local dir in `afp_poller.json`.
Data is retrieved from the AFP webservice (see `https://api.afp.com`) with an *anonymous* login (not todays news) and an embedded request (see code). 

### Launch and manage the newsboard

```
python afp_poller.py
```


## Features

[X] AFP news poller
[X] Newsboard app
[ ] cron files
[ ] External webservice
[ ] Linux testing
[ ] Unit testing
[ ] Documentation

## Contribute

Fork and create a merge-request, add an issue, or buy me a coffee :)

## Licence

See [LICENSE](LICENSE).
