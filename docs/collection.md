# Data Collection Strategy

## Introduction
This tool opts to use a "direct collection" strategy, rather than a "proxy collection" strategy. The differences are illustrated below:

### Proxy Collection
![Proxy Collection](media/picollect.png)

The Raspberry Pi collects and stores data from the radar, and then sends it to the PC for processing. This is the traditional and simplest method of data collection.

#### Pros
+ Simple
+ Easy to implement
+ Virtually no packet loss

#### Cons
- Pi has limited storage space and processing power
- Pi has very limited memory (1 GB) 
- Requires more time for data transfer

### Direct Collection
![Direct Collection](media/cpcollect.png)

The Raspberry Pi is used as a "router" for the radar, and the PC collects data directly from the radar. This allows for more complex real-time processing, but requires more complex networking.

#### Pros
+ More processing power
+ More memory (32 GB)
+ Real-time processing possible

#### Cons
- More complex networking
- More difficult to implement
- packet loss (~5% of scans lost)

## Implementation
The direct collection strategy requires only a socket client, and is implemented in [radioio.py](/src/lib/radario.py)
