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
Data is retrieved from the AFP webservice (see [api.afp.com](https://api.afp.com)) with an *anonymous* login (*not* todays news) and an embedded request (see code). 

### Launch and manage the newsboard

Call the newsboard once and let it live until you're bored:
```
# CLI on Windows and Linux like
python newsboard.py
```

Data is loaded from `afp_poller.json` in local dir.
A random selection of 10 headlines from the dataset is drawn and displayed at startup.
1 random headline is deleted and replaced each 30 seconds by another randomly drawn headline from the dataset.
Headline's display size is also randomly choosen.

The newsboard can be managed with the keyboard:
* `Esc`: quit,
* `space`: random delete of a displayed headline,
* `Enter`: add a randomly selected headline to the display,
* `Tab`: delete and add a headline.

On Linux systems, the newsboard can also be managed with POSIX signals (** to be tested **):
* `SIGUSR1`: refresh GUI content (equiv. `Tab` key),
* `SIGUSR2`: (re)load data from `afp_poller.json`.

Headlines are moving from right to left:
![newsboard](img/newsboard_2020-11-14_17-14-00.png)

### Automated launch and periodic update
*Under development*.

### Remote control
*Under development*.

## Project history and features

This project has been launched when my son and I received a [Chameleon96](https://www.96boards.org/product/chameleon96/) board.
We were thinking about a quick, easy and fun app that could be developped and launched from this board before going deeper into SoC-FPGA topics.

The app prototype has been developped on a Win10-Python3 system.
The app is de facto compatible outside the initial targetted system, and can run as a standalone app on other platforms.

Main features:

* [X] AFP news poller
* [X] Newsboard app
* [X] Documentation
* [ ] Posix signal handling
* [ ] cron example files
* [ ] Complementary webservice for remote management
* [ ] Linux testing
* [ ] Unit testing


## Contribute

You may,
* Fork and create a merge-request,
* add an issue,
* or [buy me a coffee](https://www.buymeacoffee.com/genears) :coffee: to support my work :wink:

## Licence

Please keep track of the original author's name when copying, forking or citing.

See [LICENSE](LICENSE).
