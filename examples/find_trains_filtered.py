# find_trains_filtered.py

"""
TODO
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Orientation, WaitConditionType
from draftsman.rail import TrainConfiguration, Schedule, WaitCondition


def main():
    # A whole bunch of trains in some hypothetical depot
    bp = Blueprint(
        """0eNqdmUtz2jAUhf9KR2uTsV6Wza5ddNVdlx0m44BCNDUyY0xSJsN/r4xJoI3DnHt3tpE/Pe6951joVTw0e7/tQuzF/FWEZRt3Yv7rVezCOtbN8Kw/bL2Yi9D7jchErDfDXVeHRhwzEeLK/xFzeVxkwsc+9MGP759uDvdxv3nwXWrw/uauT++un/rZCZGJbbtLb7Vx6CqRZsqktgcx15VM/FXo/HL8WR2zD1iFY3WFYzUB63CsIWAtjrUErMaxBQFLCJnDsYoQspKAJYSsImAJIZM5gUuImbzUWdMu203bh2c/BZXlFbTtQuLUY4P8TtkpMqHUFCEdJKHWJCEfJKHYJCEhJKHaJCUjLuU2YONs17fbm1D9HzRLAzrHUPyof/sv35tDjGKqLwf29S7F9t++iuu+fo5XX75NdlWCCanfEtJ9TEg3mZAVw1IcYCk5w1MQrmSYCsJVDFdBuJfCXNbdup291OvU9pb6T4Zu+EZ4To/aLrWJ+6aZ6sswLAyZg2V4GMItGCaGcB1YLcOCfbbkk/KtOP6IjJhjkABXcwwS4UqGjSFcxbAxhKsZNoZwDcPGEK4lq7LJNcAtyKqMcR1ZlTFuCaunuqKy1FNXZAeA5mBysipjXElWZYyryKqMcTWqyvbzUE6qsjFkVcZGbMmqjHELsipjXEfbthBWuCTrPTbiiqz3ENfmZL3HuJKs9xhX0bYtJrc3ti1vW4mvU1sJqxnWUgFTMAxrQbiXIqy7PjSN7w43bMDclUY7e8VH8tsWDP9CBu8YnoJwS4anINxLPT42+7D6fKGVYy10kTNMCxh4IRmmhXAVw1oQrmZYC8I1qMnmvPhZhnUh4y4YBoNwHcNgEG7JMBiEWzEM5gN3kdxg+eRX++Z8jHDJheE+fYkZd9VmPKmYsI9MvNShv1+2cXXqeoQl1Lbu/P35RKPtUrvz9WP6tBbHxTCxqX+2yDy/2faHAbgY5nQ6O5lfHbVk4tl3u3HSpTSuUs5pV9nSHI9/Ad/ZT18="""
    )

    trains = bp.find_trains_filtered()
    print("Total trains: {}".format(len(trains)))

    trains = bp.find_trains_filtered(train_length=3)
    print("Trains with length 3: {}".format(len(trains)))

    trains = bp.find_trains_filtered(orientation=Orientation.EAST)
    print("Trains facing east: {}".format(len(trains)))

    trains = bp.find_trains_filtered(orientation=Orientation.EAST, invert=True)
    print("Trains not facing east: {}".format(len(trains)))

    trains = bp.find_trains_filtered(at_station=True)
    print("Trains at stations: {}".format(len(trains)))

    trains = bp.find_trains_filtered(at_station=True, invert=True)
    print("Trains not at stations: {}".format(len(trains)))

    trains = bp.find_trains_filtered(at_station="Station A")
    print("Trains at 'Station A': {}".format(len(trains)))

    trains = bp.find_trains_filtered(at_station={"Station A", "Station B"})
    print("Trains at 'Station A' or 'Station B': {}".format(len(trains)))

    trains = bp.find_trains_filtered(num_type={"locomotive": 2, "cargo-wagon": 1})
    print("Trains with 2 locomotives and 1 cargo wagon: {}".format(len(trains)))

    config = TrainConfiguration("2-1")
    print("config.cars: {}".format(config.cars))
    trains = bp.find_trains_filtered(config=config)
    print("Trains with 2 locomotives followed by 1 cargo wagon: {}".format(len(trains)))

    schedule = Schedule()
    schedule.append_stop("Station A", WaitCondition(WaitConditionType.FULL_CARGO))
    schedule.append_stop("Station B", WaitCondition(WaitConditionType.EMPTY_CARGO))
    trains = bp.find_trains_filtered(schedule=schedule)
    print("Trains that pickup at 'Station A' and dropoff at 'Station B': {}".format(len(trains)))


if __name__ == "__main__":
    main()
