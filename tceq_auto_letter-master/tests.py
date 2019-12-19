import openpyxl
import pickle

file = '3Y_2017_SPP.xlsx'
wb = openpyxl.load_workbook(file)
sheet = wb['GREEN']

a = open('approved.pkl', 'rb')
approved = pickle.load(a)


def test(dct):
    f = open('test.txt', 'w')
    for x in dct:
        val = dct[x]
        samples = val[2]
        sample_site_count = len(samples)
        for i in range(sample_site_count):
            sample = samples[i]
            tier = sample[1]
            creation = sample[3]
            f.write(str(tier))
    f.close()


def check_manual(sheet):
    lst = []
    for i in range(1, 1405):
        pws_id = sheet.cell(row=i, column=1).value
        try:
            if approved[pws_id]:
                pass
        except:
            lst.append(pws_id)
    return lst


lst = check_manual(sheet)
print(lst)
