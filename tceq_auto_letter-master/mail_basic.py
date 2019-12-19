import mailmerge
import pickle

a = open('approved.pkl', 'rb')
approved = pickle.load(a)
"""
e = open('edge.pkl', 'rb')
edge_case = pickle.load(e)

d = open('deny.pkl', 'rb')
deny = pickle.load(d)

 EXAMPLE OF DICTIONARY BEING PASSED THROUGH TO EACH PAGE
pws_1 = {
    'pws_id': 'TX000000',
    'pws_name': 'WSC',
}
"""


def unpack_pws(dct):
    lst = []
    for item in dct:
        val = dct[item]
        lst.append({'Short_PWS': val[0], 'PWSNAME': val[1]})
    return lst


# Define the templates - assumes they are in the same directory as the code
template = "test.docx"
document = mailmerge.MailMerge(template)
document.merge_pages(unpack_pws(approved))
document.write('EXAMPLE.docx')


