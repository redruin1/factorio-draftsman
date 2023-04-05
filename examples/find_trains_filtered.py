# find_trains_filtered.py

"""
TODO
"""

from draftsman.blueprintable import Blueprint


def main():
    bp = Blueprint("0eNqdldtu4yAQht+Fa8diOAzgV6lWlZugFMnBEXayjSK/+07sbtqqtMK5sOTDzDfDzz/myl66kz+mEEfWXFnY9nFgzdOVDWEf2+72brwcPWtYGP2BVSy2h9tTakPHpoqFuPNvrIHpT8V8HMMY/JI/P1ye4+nw4hMF3DO7ftsf+jGcPdGO/UApfbzVIcwGtKzY5XajaiGtsCA0VelTIF67RPKaXn0rIO4FhpGa27+Om7nH32qYKQOSD4B0DqQeAMkcSD8AghwI76Btm/b95m+7p9wspuYABqzRC8/8thucOym0UcII0Nrg/8QQzxTXJwLEU9dlGjLrV+ZyC7PrOdm9dx8CndLZ736mqIUiSI5dSH67fM0ZE3ix6qq2gksSeYHzGp2Wec0dcroo2nLFAQHkvDslogOUrhL53Ij6ukiRY64ZPzNT4StV5qiyWDpXW2eVfPerrMmA31VDY8mbZFZ0RjgERa4tVm3FOJvFY7pAtxWzbaCYioV/W8QakYPGd8tlNDNZT68YXHTFba8YYzTFVLeCqvNUOtzm46/5dFpW7OzTsARYUMYJg6gtWjtN/wAFLVWc")

    trains = bp.find_trains_filtered()
    print("num_trains:", len(trains))
    for train in trains:
        print("\t", train)

if __name__ == "__main__":
    main()