import sys
import pandas as pd
import numpy as np


tax_free_allowance = 12_300
tax_factor = 0.2

tax_y_21 = "2021-04-06"
tax_y_22 = "2022-04-06"

##
# Rules:
# 1. Pooling (section 104) - The beneficial owner of the tokens will have a
# 		single pooled asset for Capital Gains Tax purposes that will increase
# 		or decrease with each acquisition, part disposal or disposal
# 2. Records - Individuals must still keep a record of the amount spent
# 		on each type of token, as well as the pooled allowable cost of each pool
# 3. Same day rule - When tokens of the same type are acquired and disposed of by
# 		the same individual on the same day and in the same capacity then:
#	-	all the tokens acquired shall be treated as acquired in a single transaction
#	-	all the tokens disposed of shall be treated as disposed of in a single transaction
#	The tokens acquired will, as far as possible, be matched with the tokens disposed of
# 		so that those tokens don’t go into the section 104 pool:
#	-	if the quantity of tokens acquired exceeds the number disposed of then the excess
# 		tokens will then be considered for the 30 day rule (covered below) and if that doesn’t
# 		apply then they will go into the section 104 pool
#	-	if the quantity of tokens disposed of exceeds the number acquired then the excess
# 		tokens will then be considered for the 30 day rule (covered below) and if that doesn’t
# 		apply then they will be treated as a disposal from the section 104 pool.
# 4. Acquiring tokens within 30 days of selling -
#		If an individual disposes of tokens and then acquires, in the same capacity,
# 		tokens of the same type within the next 30 days then:
#	-	the same day rule (covered above) is applied first if applicable
#	-	the tokens acquired to which the 30 day rule applies don’t go into the section 104 pool
# 		but instead are matched to the earlier disposal (or disposals) of tokens
#	-	the tokens acquired to which the 30 day rule applies are matched to disposals on
# 		the basis of earliest disposal first
#	-	if the quantity of tokens so acquired exceeds the number of tokens disposed of in the
# 		preceding 30 days then the excess tokens will go into the section 104 pool.
#
#	If there is an acquisition and a disposal on the same day the disposal is identified
# 	first against the acquisition on the same day


def insert_df(df, row):
    df.loc[-1] = row
    df.index = df.index + 1
    df = df.sort_index()


def calculate_tax(csv, tax_year_start, tax_year_end):
    table = pd.read_csv(csv)[['time', 'pair', 'type',
                              'price', 'cost', 'fee', 'vol']]

    ada = table[table['pair'].str.contains('ADA')]
    print(ada)

    running_total_ada = 0
    pooled_allowable_costs = 0
    total_rows = 0
    total_gain = 0

    tax_year_gain = 0
    print("Date \t\t Qty ADA \t\t Pooled Allowable Costs")
    for index, row in ada.iterrows():
        date = row['time'][:10]
        if row['type'] == 'buy':
            total_rows += 1
            running_total_ada += row['vol']
            pooled_allowable_costs += row['cost']
            print(f"{date} \t +{row['vol']} \t +£{row['cost']}")

        elif row['type'] == 'sell':
            less_allowable_costs = pooled_allowable_costs * \
                (float(row['vol']) / float(running_total_ada))

            gain = row['cost'] - less_allowable_costs
            print(f"{date} \t ({row['vol']}) \t (£{row['cost']})")
            print(f"Gain: \t £{gain}")

            if date >= tax_year_start and date < tax_year_end:
                tax_year_gain += gain

            total_gain += gain

            pooled_allowable_costs -= less_allowable_costs
            running_total_ada -= row['vol']

            total_rows += 1

    print("Rows considered:", total_rows)
    print("Final ada balance", running_total_ada)
    print("Final pooled allowable costs", pooled_allowable_costs)
    print(f"Total gain £{total_gain}")
    print(
        f"Tax year {tax_year_start} to {tax_year_end} gain: £{tax_year_gain}")
    print(
        f"Taxable gains for tax year {tax_year_start} to {tax_year_end}: £{tax_year_gain - tax_free_allowance}")
    print(
        f"Total tax owed for tax year {tax_year_start} to {tax_year_end}: £{(tax_year_gain - tax_free_allowance) * tax_factor}")


def trades(csv):
    table = pd.read_csv(csv)[['time', 'pair', 'type', 'cost', 'vol']]
    print(table)

    table = table[table['pair'] != 'EURGBP']

    print("Table showing all buys:")
    print(table[table['type'] == "buy"])
    amount_bought = sum(table[table['type'] == "buy"]['cost'])
    print("Total amount bought: {0}".format(amount_bought))

    print("")

    print("Table showing all sells:")
    print(table[table['type'] == "sell"])
    amount_sold = sum(table[table['type'] == "sell"]['cost'])
    print("Total amount sold: {0}".format(amount_sold))

    tax_y_21 = table[table['time'] > '2021-04-06']

    buy = tax_y_21[tax_y_21['type'] == 'buy']
    sell = tax_y_21[tax_y_21['type'] == 'sell']
    total_bought = sum(buy['cost'])
    total_sold = sum(sell['cost'])

    print(total_bought)
    print(total_sold)


if __name__ == "__main__":
    assert len(
        sys.argv) == 2, "Usage: python {0} [path-to-kraken-trades-csv]".format(sys.argv[0])

    calculate_tax(sys.argv[1], tax_y_21, tax_y_22)
