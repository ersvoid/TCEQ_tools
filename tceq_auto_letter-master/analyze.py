import pickle

# LOADS THE EXTERNAL PICKLE FILE AND CONVERTS TO A PYTHON DICTIONARY OBJECT
f = open('pws_list.pkl', 'rb')
pws_list = pickle.load(f)


def red_population_check(pop, count):
    # Checks population to determine reduced monitoring sample sites required and verifies if there are enough listed
    # samples sites
    if pop > 100000:
        if count >= 50:
            return True
        else:
            return False
    elif pop > 10000:
        if count >= 30:
            return True
        else:
            return False
    elif pop > 3300:
        if count >= 20:
            return True
        else:
            return False
    elif pop > 500:
        if count >= 10:
            return True
        else:
            return False
    elif pop > 100:
        if count >= 5:
            return True
        else:
            return False
    else:
        if count >= 5:
            return True
        else:
            return False


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


def analyze_pws(dct):
    # TAKES DICTIONARY OF PWS DATA AND DETERMINES WHICH SYSTEMS HAVE AN APPROVED PLAN
    print("ANALYZING PUBLIC WATER SYSTEM DATA")
    edge_case = {}
    approved = {}
    denied = {}
    for key in dct:
        val = dct[key]
        pop = val[2]
        samples = val[3]
        active_site_count = 0
        sample_tier = 0
        sample_creation_sum = 0
        for i in range(len(samples)):
            sample = samples[i]
            tier = sample[3]
            activity = sample[1]
            creation_date = sample[5]
            if activity == "A":
                active_site_count += 1
                if creation_date is not None:
                    sample_creation_sum += 1
                if tier is not None:
                    sample_tier += 1
        # REQUIRED NUMBER OF ACTIVE SAMPLE SITES
        if red_population_check(pop, active_site_count):
            # REQUIRED NUMBER OF SITES WITH CREATED DATE
            if red_population_check(pop, sample_creation_sum):
                # REQUIRED NUMBER OF SITES WITH TIER DATA
                if red_population_check(pop, sample_tier):
                    approved[key] = val
                # NUMBER OF SITES WITH TIER DATA LESS THAN NUMBER OF REQUIRED SITES
                else:
                    edge_case[key] = val
            # NO SITES WITH CREATED DATE
            else:
                if red_population_check(pop, sample_tier):
                    approved[key] = val
            # elif sample_creation_sum == 0:
                # ALL SITES HAVE TIER DATA
                # if sample_tier == active_site_count:
                #    approved[key] = val
                # REQUIRED NUMBER OF SITES WITH TIER DATA
                # elif sample_tier >= req_sites(pop):
                #    approved[key] = val
                # NO SITES WITH TIER DATA
                elif sample_tier == 0:
                    denied[key] = val
                # NUMBER OF SITES WITH TIER DATA LESS THAN NUMBER OF REQUIRED SITES
                else:
                    edge_case[key] = val
            # SOME SITES WITH CREATED DATES
            # else:
            #    edge_case[key] = val
        # NOT ENOUGH SAMPLE SITES
        else:
            # LESS THAN FIVE ACTIVE SAMPLE SITES
            if len(samples) < 5:
                edge_case[key] = val
            else:
                denied[key] = val
    lst = [approved, edge_case, denied]
    print("ANALYZATION COMPLETE")
    return lst


# BREAK UP THE ANALYZED PWS LIST INTO SEPARATE PYTHON DICTIONARY OBJECTS AND CONVERT TO EXTERNAL PICKLE FILES
result = analyze_pws(pws_list)
app = result[0]
edge = result[1]
deny = result[2]
print("PICKLING...")
a = open("approved.pkl", "wb")
pickle.dump(app, a)
a.close()
print("...")
e = open("edge.pkl", "wb")
pickle.dump(edge, e)
e.close()
print("...")
d = open("deny.pkl", "wb")
pickle.dump(deny, d)
d.close()
print("PICKLING COMPLETE")
