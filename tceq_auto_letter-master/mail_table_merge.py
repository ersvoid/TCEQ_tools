import mailmerge
import pickle
import datetime

a = open('approved.pkl', 'rb')
approved = pickle.load(a)

e = open('edge.pkl', 'rb')
edge_case = pickle.load(e)
"""
d = open('deny.pkl', 'rb')
deny = pickle.load(d)

 EXAMPLE OF DICTIONARY BEING PASSED THROUGH TO EACH PAGE

pws_list = [{
    'today_date': datetime object,
    'pws_id': 'TX######',
    'pws-name': 'NAME',
    'samp_id': [{
    'samp_id': 'Red Shoes',
    'activity': '$10.00',
    'loc': '2500',
    'create_date': '$25,000.00'}, {
    'samp_id': 'Red Shoes',
    'activity': '$10.00',
    'loc': '2500',
    'create_date': '$25,000.00'
}]}]
"""


def table_merge(dct):
    lst = []
    c = 0
    for item in dct:
        val = dct[item]
        pws_id = val[0]
        pws_name = val[1]
        today = "05-06-2019"
        lst.append({'today_date': today, 'pws_id': pws_id, 'pws_name': pws_name, 'samp_id': []})
        samples = val[3]
        amt_sample = len(samples)
        for i in range(amt_sample):
            sample = samples[i]
            sample_id = sample[0]
            activity = sample[1]
            loc = sample[2]
            # UPDATE BY NAME IS SAMPLE[3]
            create_date = sample[5]
            lst[c]['samp_id'].append({'samp_id': sample_id, 'activity': activity, 'loc': loc, 'create_date': create_date})
        c += 1
    return lst


# Define the templates - assumes they are in the same directory as the code
template = "table_merge_test.docx"
with mailmerge.MailMerge(template) as document:
    document.merge_pages(table_merge(edge_case))
    document.write('EXAMPLE_tables.docx')


# print(table_merge(edge_case))

