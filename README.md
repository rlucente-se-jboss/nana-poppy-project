# The Nana and Poppy Project
This is a customized Google Assistant with push button activation.
What makes it special is [here](https://youtu.be/Co7rigJRNUM).

## Configuration
Follow the instructions for the Google AIY Voice Kit and get an
initial working configuration. Next, install python modules for the
Open Weather Map API wrapper and the inflect project.

    pip3 install inflect pyowm

Copy the contents of this repository to /home/pi on the Raspberry
Pi.

## Get the audio clips
The `phrase-list.txt` file contains all the words and phrases for
which you'll need audio clips. Make sure that these are in Waveform
Audio File Format (WAV) and that the filenames exactly match the
words and phrases in the `phrase-list.txt` file, sans the `.wav`
extension.

You can confirm the audio clips are fully populated and properly
named using the `check-file.sh` bash script.

    ./check-files.sh child1 wav
    ./check-files.sh child2 wav

## Enable service start at boot
Install the service unit file and enable the service to start when
the device boots.

    sudo ln -s `pwd`/assistant_grpc_demo.service /lib/systemd/system
    sudo systemctl daemon-reload
    sudo systemctl enable assistant_grpc_demo.service

