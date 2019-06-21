import cx_Oracle
import mailmerge
import datetime

# EXPORT ACTIVE LCR SAMPLE SITES FOR ANY PWS USING LIVE ORACLE DATA


def sample_sites_word_merge():
    dsn_tns = cx_Oracle.makedsn('aed2-scan.tceq.texas.gov', '1521', service_name='PRDEXA.TCEQ.TEXAS.GOV')
    conn = cx_Oracle.connect('ESTINSON', 'Sartre05', dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    ask = input("ENTER PWS ID: ")
    if len(ask) == 7:
        ask = "TX" + str(ask)
    else:
        while ask[:2] != 'TX':
            ask = input("ENTER FULL PWS ID: ")
    c.execute("SELECT TINWSYS_IS_NUMBER, NAME "
              "FROM SDWIS2TX.TINWSYS "
              "WHERE NUMBER0 = '{}'".format(ask))
    val = c.fetchall()
    tinwsys = val[0][0]
    name = val[0][1]
    c.execute("SELECT TINWSF_IS_NUMBER "
              "FROM SDWIS2TX.TINWSF "
              "WHERE TINWSYS_IS_NUMBER = {} AND TYPE_CODE = 'DS'".format(tinwsys))
    tinwsf0is = c.fetchone()[0]
    c.execute("SELECT IDENTIFICATION_CD, DESCRIPTION_TEXT, LD_CP_TIER_LEV_TXT, "
              "D_LAST_UPDT_TS, ACTIVITY_STATUS_CD "
              "FROM SDWIS2TX.TSASMPPT "
              "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))
    val = c.fetchall()
    sites = []
    for v in val:
        if v[0][:3] == 'LCR':
            YEAR = str(v[3].year)
            month = str(v[3].month)
            if len(month) == 1:
                month = "0" + month
            day = str(v[3].day)
            DATE = month + "/" + day + "/" + YEAR
            d = {'SAMPLE_ID': v[0][:6], 'sample_loc': v[1], 'activity': v[4], 'tier': v[2], 'last_update': DATE}
            sites.append(d)
    template = "sample_sites.docx"
    today = datetime.datetime.today()
    year = today.year
    month = str(today.month)
    if len(month) == 1:
        month = "0" + str(month)
    day = str(today.day)
    if len(day) == 1:
        day = "0" + str(month)
    code_today = str(year) + month + day
    document = mailmerge.MailMerge(template)
    document.merge(pws_id=ask,
                   pws_name=name,
                   short_id=ask[2:],
                   yearmonthday=code_today,
                   SAMPLE_ID=sites)
    path = r'C:\Users\Estinson\Desktop' + "\\" + "sample_sites_" + ask + ".docx"
    document.write(path)
    c.close()
    conn.close()


sample_sites_word_merge()
