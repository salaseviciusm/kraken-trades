import sys
import pandas as pd

if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: python {0} [path-to-kraken-trades-csv]".format(sys.argv[0])

    table = pd.read_csv(sys.argv[1])[['time', 'pair', 'type', 'cost', 'vol']]

    print("Table showing all buys:")
    print(table[table['type'] == "buy"])
    amount_bought = sum(table[table['type'] == "buy"]['cost'])
    print("Total amount bought: {0}".format(amount_bought))

    print("")

    print("Table showing all sells:")
    print(table[table['type'] == "sell"])
    amount_sold = sum(table[table['type'] == "sell"]['cost'])
    print("Total amount sold: {0}".format(amount_sold))

