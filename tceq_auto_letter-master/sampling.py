import pickle

a = open('approved.pkl', 'rb')
approved = pickle.load(a)

e = open('edge.pkl', 'rb')
edge_case = pickle.load(e)

d = open('deny.pkl', 'rb')
deny = pickle.load(d)


def req_sites(pop):
    # Checks population to determine reduced monitoring sample sites required and verifies if there are enough listed
    # samples sites
    if pop > 100000:
        return 50
    elif pop > 10000:
        return 30
    elif pop > 3300:
        return 20
    elif pop > 500:
        return 10
    elif pop > 100:
        return 5
    else:
        return 5


def edge_roll(dct):
    # PRINTS OUT ALL THE EDGE CASE PWSs IN A STEP-BY-STEP ORDER AND ALLOWS DECISION INPUT
    # DECISION INPUT WILL DETERMINE APPROVED OR DENIED
    a = {}
    d = {}
    for item in dct:
        lst = dct[item]
        print("PWS ID: ", lst[0])
        print("PWS NAME: ", lst[1])
        print("POPULATION: ", lst[2])
        print("REQ SITES: ", req_sites(lst[2]))
        for i in range(len(lst[3])):
            sample = lst[3][i]
            id = sample[0]
            activity = sample[1]
            tier = sample[3]
            update = sample[4]
            creation = sample[5]
            print(id, ": ", activity, " - ", tier, " By: ", update, " On: ", creation)

        # FUNCTION WILL CRASH IF ANYTHING OTHER THAN A OR B IS INPUT
        val = input("A/D? ")
        val.lower()
        """while val.isdigit():
            val = input("A/D? ")
        while val != 'a' or 'd':
            val = input("A/D? ")"""
        if val == 'a':
            a[item] = lst
        elif val == 'd':
            d[item] = lst
    ad = [a, d]
    return ad


def sampling(dct):
    # PRINTS OUT ALL THE EDGE CASE PWSs IN A STEP-BY-STEP ORDER AND ALLOWS DECISION INPUT
    # DECISION INPUT WILL DETERMINE APPROVED OR DENIED
    a = {}
    d = {}
    l = len(dct)
    count = 0
    for item in dct:
        if count == 20:
            lst = dct[item]
            print("PWS ID: ", lst[0])
            print("PWS NAME: ", lst[1])
            print("POPULATION: ", lst[2])
            print("REQ SITES: ", req_sites(lst[2]))
            for i in range(len(lst[3])):
                sample = lst[3][i]
                id = sample[0]
                activity = sample[1]
                tier = sample[3]
                update = sample[4]
                creation = sample[5]
                print(id, ": ", activity, " - ", tier, " By: ", update, " On: ", creation)
            # FUNCTION WILL CRASH IF ANYTHING OTHER THAN A OR B IS INPUT
            val = input("A/D? ")
            val.lower()
            """while val.isdigit():
                val = input("A/D? ")
            while val != 'a' or 'd':
                val = input("A/D? ")"""
            if val == 'a':
                a[item] = lst
            elif val == 'd':
                d[item] = lst
        else:
            count += 1
    ad = [a, d]
    return ad


lst = edge_roll(edge_case)
# lst = sampling(deny)
a = lst[0]

d = lst[1]

print(len(a))
