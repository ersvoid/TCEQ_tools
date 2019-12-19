import pickle

# LOAD PICKLE FILES AND CONVERT TO DICTIONARIES
f = open('pws_list.pkl', 'rb')
pws_list = pickle.load(f)

a = open('approved.pkl', 'rb')
approved = pickle.load(a)

e = open('edge.pkl', 'rb')
edge_case = pickle.load(e)

d = open('deny.pkl', 'rb')
deny = pickle.load(d)

# ADD DICTIONARIES TO LIST OBJECT FOR THE FOLLOWING FUNCTION
result = [approved, edge_case, deny, pws_list]


def check(result):
    # CHECKS THE LENGTH OF EACH DICTIONARY AND DETERMINES IF ANY SYSTEMS WERE NOT ANALYZED PROPERLY
    # THE APPROVED, EDGE, AND DENY DICTIONARY LENGTHS SHOULD EQUAL THE ORIGINAL PWS DICTIONARY LENGTH
    app = result[0]
    edge = result[1]
    deny = result[2]
    pws = result[3]
    amt_app = len(app)
    amt_edge = len(edge)
    amt_deny = len(deny)
    amt_pws = len(pws)
    if amt_pws == amt_app + amt_edge + amt_deny:
        print("Success!")
        print(amt_app, amt_edge, amt_deny, amt_pws)
    else:
        print("Nope")
        print(amt_app, amt_edge, amt_deny, amt_pws)


check(result)


def check_samples(d):
    # PRINTS ALL THE SAMPLE SITES FROM EVERY PWS IN A DICTIONARY
    for key in d:
        val = d[key]
        print(val[3])
