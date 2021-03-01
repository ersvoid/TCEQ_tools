import cx_Oracle
from operator import itemgetter
import datetime
from math import floor
import time


def strip_lst(lst):
    new = []
    for item in lst:
        try:
            item = item.strip()
        except AttributeError:
            pass
        finally:
            new.append(item)
    return new


def time_in_range(start, _end, x):
    """Return true if x is in the range [start, end]"""
    if start <= _end:
        return start <= x <= _end
    else:
        return start <= x or x <= _end


def water_systems(c):
    pws_lst = []
    sql_statement = "SELECT " \
                    "NUMBER0, " \
                    "TINWSYS_IS_NUMBER, " \
                    "NAME, " \
                    "ACTIVITY_STATUS_CD, " \
                    "D_POPULATION_COUNT, " \
                    "PWS_ST_TYPE_CD " \
                    "FROM SDWIS2TX.TINWSYS " \
                    "WHERE ACTIVITY_STATUS_CD = 'A'"
    c.execute(sql_statement)
    for row in c.fetchall():
        row = strip_lst(row)
        pws_lst.append(row)
    return pws_lst


def inventory_info(c, pws_id):
    inv_info = []
    sources = ["Surface Water Purchased", "Surface Water", "Ground Water", "Ground Water Purchased", "GUI",
               "GUI Purchased"]
    codes = ["SWP", "SW", "GW", "GWP", "GU", "GUP"]
    sql_statement = "SELECT " \
                    "TINWSYS.NUMBER0, " \
                    "TINWSYS.TINWSYS_IS_NUMBER, " \
                    "TINWSYS.NAME, " \
                    "TINWSYS.ACTIVITY_STATUS_CD, " \
                    "TINWSYS.D_ST_PRIM_SRC_CD, " \
                    "TINWSYS.D_POPULATION_COUNT, " \
                    "TINWSYS.PWS_ST_TYPE_CD, " \
                    "TINWSF.TINWSF_IS_NUMBER, " \
                    "TINWSF.TYPE_CODE, " \
                    "TINWSF.ST_ASGN_IDENT_CD " \
                    "FROM SDWIS2TX.TINWSYS " \
                    "LEFT JOIN SDWIS2TX.TINWSF " \
                    "ON TINWSYS.TINWSYS_IS_NUMBER = TINWSF.TINWSYS_IS_NUMBER " \
                    "WHERE TINWSF.ACTIVITY_STATUS_CD = 'A' AND TINWSYS.NUMBER0 = '{}'".format(pws_id)
    c.execute(sql_statement)
    tinwsf0is = ''
    entry_points = 0
    pbcu_points = 0
    for row in c.fetchall():
        row = strip_lst(row)
        number0 = row[0]
        tinwsys = row[1]
        name = row[2]
        activity = row[3]
        source = row[4]
        try:
            source = sources[codes.index(source)]
        except ValueError:
            source = "Unknown Source"
        pop = row[5]
        pws_type = row[6]
        tinwsf = row[7]
        type_code = row[8]  # DS = Distribution System; SS = Entry Points
        st_code = row[9]  # DS01 = Distribution System; EP = Entry Points; PBCU = Entry Points for LCR
        if type_code == 'DS':
            tinwsf0is = tinwsf
        if st_code[:2] == 'EP':
            entry_points += 1
        elif st_code[:4] == 'PBCU':
            pbcu_points += 1
        inv_info = [number0,
                    name,
                    activity,
                    source,
                    pop,
                    pws_type,
                    tinwsys,
                    tinwsf0is,
                    entry_points,
                    pbcu_points]
    return inv_info


def indicator_info(c, tinwsys):
    indicators = []
    c.execute("SELECT INDICATOR_NAME, INDICATOR_VALUE_CD, INDICATOR_DATE, INDICATOR_END_DATE "
              "FROM SDWIS2TX.TINWSIN "
              "WHERE TINWSYS_IS_NUMBER = {}".format(tinwsys))
    for row in c.fetchall():
        if row[0] == "UNDM":
            try:
                begin_date = row[2].date()
                # begin_date = datetime_conversion(row[2])
            except:
                begin_date = row[2]
            try:
                end_date = row[3].date()
                # end_date = datetime_conversion(row[3])
            except:
                end_date = row[3]
            indicators.append([row[0], row[1], begin_date, end_date])
    return indicators


def milestone_info(c, tinwsys):
    c.execute("SELECT TYPE_CODE, ACTUAL_DATE, MEASURE "
              "FROM SDWIS2TX.TFRMEVNT "
              "WHERE TINWSYS_IS_NUMBER = {}".format(tinwsys))
    milestones = []
    for row in c.fetchall():
        actual_date = row[1].date()
        if row[0] == "CU90":
            milestones.append([row[0], actual_date, row[2]])
        elif row[0] == "PB90":
            milestones.append([row[0], actual_date, row[2]])
        else:
            if actual_date.year >= 2011:
                milestones.append([row[0], actual_date, row[2]])
    return milestones


def group_actions(lst):
    dct = {}
    for row in lst:
        tmnviol = row[0]
        tmnvtype = row[1]
        status_type = row[2]
        begin_date = row[3]
        end_date = row[4]
        dct[tmnviol] = [tmnvtype, status_type, begin_date, end_date, []]
    for row in lst:
        tmnviol = row[0]
        last_date = row[5]
        tenactyp = row[6]
        loc_type = row[7]
        formal_code = row[8]
        sub_code = row[9]
        name = row[10]
        dct[tmnviol][4].append([last_date, tenactyp, loc_type, formal_code, sub_code, name])
    return dct


def violation_info(c, tinwsys):
    violations = []
    sql_statement = "SELECT TMNVIOL.TMNVIOL_IS_NUMBER, " \
                    "TMNVIOL.TMNVTYPE_IS_NUMBER, " \
                    "TMNVIOL.STATUS_TYPE_CODE, " \
                    "TMNVIOL.STATE_PRD_BEGIN_DT, " \
                    "TMNVIOL.STATE_PRD_END_DT, " \
                    "TMNVIEAA.D_LAST_UPDT_TS, " \
                    "TMNVIEAA.TENACTYP_IS_NUMBER, " \
                    "TENACTYP.LOCATION_TYPE_CODE, " \
                    "TENACTYP.FORMAL_TYPE_CODE, " \
                    "TENACTYP.SUB_CATEGORY_CODE, " \
                    "TENACTYP.NAME " \
                    "FROM SDWIS2TX.TMNVIOL " \
                    "LEFT JOIN SDWIS2TX.TMNVIEAA " \
                    "ON TMNVIOL.TMNVIOL_IS_NUMBER = TMNVIEAA.TMNVIOL_IS_NUMBER " \
                    "LEFT JOIN SDWIS2TX.TENACTYP " \
                    "ON TMNVIEAA.TENACTYP_IS_NUMBER = TENACTYP.TENACTYP_IS_NUMBER " \
                    "WHERE TMNVIOL.TINWSYS_IS_NUMBER = {}".format(tinwsys)
    c.execute(sql_statement)
    for row in c.fetchall():
        row = strip_lst(row)
        tmnviol = row[0]
        tmnvtype = row[1]
        status_type = row[2]
        begin_date = row[3]
        if begin_date is not None:
            begin_date = begin_date.date()
        end_date = row[4]
        if end_date is not None:
            end_date = end_date.date()
        last_date = row[5]
        if last_date is not None:
            last_date = last_date.date()
        tenactyp = row[6]
        loc_type = row[7]
        formal_code = row[8]
        sub_code = row[9]
        name = row[10]
        violations.append([tmnviol, tmnvtype, status_type, begin_date, end_date, last_date, tenactyp, loc_type,
                           formal_code, sub_code, name])
    return group_actions(violations)


def violation_pull(u, p, violation_number, year, option):
    viols = [22, 23, 24, 27, 28, 29, 30, 34, 35, 36, 87]
    types = [51, 52, 53, 56, 57, 58, 59, 63, 64, 65, 66]
    types = [str(x) for x in types]
    tenactyp_vals = [66, 72, 82, 86]
    options = ["V", "P"]
    violations = {}
    actions = {}
    closed = {}
    open = {}
    viol_number = viols[types.index(violation_number)]
    if year is not None:
        year_string = "01-JAN-{}".format(year[2:])
        sql_statement = "SELECT " \
                        "TINWSYS.NUMBER0, " \
                        "TINWSYS.TINWSYS_IS_NUMBER, " \
                        "TINWSYS.NAME, " \
                        "TINWSYS.ACTIVITY_STATUS_CD, " \
                        "TINWSYS.D_POPULATION_COUNT, " \
                        "TINWSYS.PWS_ST_TYPE_CD, " \
                        "TMNVIOL.TMNVIOL_IS_NUMBER, " \
                        "TMNVIOL.TMNVTYPE_IS_NUMBER, " \
                        "TMNVIOL.STATUS_TYPE_CODE, " \
                        "TMNVIOL.STATE_PRD_BEGIN_DT, " \
                        "TMNVIOL.STATE_PRD_END_DT, " \
                        "TMNVIEAA.D_LAST_UPDT_TS, " \
                        "TMNVIEAA.TENACTYP_IS_NUMBER, " \
                        "TENACTYP.LOCATION_TYPE_CODE, " \
                        "TENACTYP.FORMAL_TYPE_CODE, " \
                        "TENACTYP.SUB_CATEGORY_CODE, " \
                        "TENACTYP.NAME " \
                        "FROM " \
                        "SDWIS2TX.TINWSYS " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TMNVIOL " \
                        "ON " \
                        "TINWSYS.TINWSYS_IS_NUMBER = TMNVIOL.TINWSYS_IS_NUMBER " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TMNVIEAA " \
                        "ON " \
                        "TMNVIOL.TMNVIOL_IS_NUMBER = TMNVIEAA.TMNVIOL_IS_NUMBER " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TENACTYP " \
                        "ON " \
                        "TMNVIEAA.TENACTYP_IS_NUMBER = TENACTYP.TENACTYP_IS_NUMBER " \
                        "WHERE " \
                        "TMNVIOL.STATE_PRD_BEGIN_DT = '{}' " \
                        "AND " \
                        "TMNVIOL.TMNVTYPE_IS_NUMBER = {}".format(year_string, viol_number)
    else:
        sql_statement = "SELECT " \
                        "TINWSYS.NUMBER0, " \
                        "TINWSYS.TINWSYS_IS_NUMBER, " \
                        "TINWSYS.NAME, " \
                        "TINWSYS.ACTIVITY_STATUS_CD, " \
                        "TINWSYS.D_POPULATION_COUNT, " \
                        "TINWSYS.PWS_ST_TYPE_CD, " \
                        "TMNVIOL.TMNVIOL_IS_NUMBER, " \
                        "TMNVIOL.TMNVTYPE_IS_NUMBER, " \
                        "TMNVIOL.STATUS_TYPE_CODE, " \
                        "TMNVIOL.STATE_PRD_BEGIN_DT, " \
                        "TMNVIOL.STATE_PRD_END_DT, " \
                        "TMNVIEAA.D_LAST_UPDT_TS, " \
                        "TMNVIEAA.TENACTYP_IS_NUMBER, " \
                        "TENACTYP.LOCATION_TYPE_CODE, " \
                        "TENACTYP.FORMAL_TYPE_CODE, " \
                        "TENACTYP.SUB_CATEGORY_CODE, " \
                        "TENACTYP.NAME " \
                        "FROM " \
                        "SDWIS2TX.TINWSYS " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TMNVIOL " \
                        "ON " \
                        "TINWSYS.TINWSYS_IS_NUMBER = TMNVIOL.TINWSYS_IS_NUMBER " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TMNVIEAA " \
                        "ON " \
                        "TMNVIOL.TMNVIOL_IS_NUMBER = TMNVIEAA.TMNVIOL_IS_NUMBER " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TENACTYP " \
                        "ON " \
                        "TMNVIEAA.TENACTYP_IS_NUMBER = TENACTYP.TENACTYP_IS_NUMBER " \
                        "WHERE " \
                        "TMNVIOL.TMNVTYPE_IS_NUMBER = {}".format(viol_number)
    dsn_tns = cx_Oracle.makedsn('.gov link', 'port number', service_name='another .gov link')
    conn = cx_Oracle.connect(u, p, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()

    c.execute(sql_statement)
    for row in c.fetchall():
        row = strip_lst(row)
        pws_id = row[0]
        tinwsys = row[1]
        name = row[2]
        activity = row[3]
        pop = row[4]
        pws_type = row[5]
        inventory = [pws_id, tinwsys, name, activity, pop, pws_type]
        tmnviol = row[6]
        tmnvtype = row[7]
        status_type = row[8]
        begin_date = row[9].date()
        end_date = row[10]
        if end_date is not None:
            end_date = end_date.date()
        last_date = row[11]
        violation = [tmnviol, tmnvtype, status_type, str(begin_date), str(end_date), last_date]
        if tmnviol not in actions:
            actions[tmnviol] = []
        tenactyp = row[12]
        loc_type = row[13]
        formal_code = row[14]
        sub_code = row[15]
        name = row[16]
        actions[tmnviol].append([tenactyp, loc_type, formal_code, sub_code, name])
        violations[tmnviol] = [inventory, violation, actions[tmnviol]]
    if option == "ALL VIOLATIONS":
        print("Violations: ", len(violations))
        return violations
    else:
        for tmnviol in violations:
            violation = violations[tmnviol]
            actions = violation[2]
            results = []
            for action in actions:
                results.append(action[0])
            s1 = set(results)
            s2 = set(tenactyp_vals)
            if not s1.intersection(s2):
                open[tmnviol] = violation
            else:
                closed[tmnviol] = violation
        if option == "OPEN VIOLATIONS":
            print("Violations: ", len(open))
            return open
        elif option == "CLOSED VIOLATIONS":
            print("Violations: ", len(closed))
            return closed


def group_violations(dct):
    closed = {}
    open = {}
    viols = [22, 23, 24, 27, 28, 29, 30, 34, 35, 36, 87]
    types = [51, 52, 53, 56, 57, 58, 59, 63, 64, 65, 66]
    tenactyp_vals = [66, 72, 82, 86]
    options = ["V", "P"]
    for tmnviol in dct:
        results = []
        dates = []
        violation = dct[tmnviol]
        tmnvtype = violation[0]
        status_type = violation[1]
        begin_date = violation[2]
        end_date = violation[3]
        if tmnvtype in viols:
            if status_type in options:
                if begin_date.year >= 2011:
                    viol = types[viols.index(tmnvtype)]
                    actions = violation[4]
                    v = []
                    for action in actions:
                        last_date = action[0]
                        tenactyp = action[1]
                        loc_type = action[2]
                        formal_code = action[3]
                        sub_code = action[4]
                        name = action[5]
                        results.append(tenactyp)
                        dates.append([last_date, tenactyp])
                        v.append([tenactyp, loc_type, formal_code, sub_code, name, last_date])
                    s1 = set(results)
                    s2 = set(tenactyp_vals)
                    if not s1.intersection(s2):
                        v_inv = [viol, status_type, begin_date, end_date]
                        open[tmnviol] = [v_inv, v]
                    else:
                        v_inv = [viol, status_type, begin_date, end_date]
                        closed[tmnviol] = [v_inv, v]
    return [closed, open]


def compliance_info(c, tinwsys):
    compliance = []
    sql_statement = """
                    SELECT 
                    TENSCHD.TENSCHD_IS_NUMBER, 
                    TENSCHD.EFFECTIVE_DATE, 
                    TENSCHD.CLOSED_DATE, 
                    TENSCHD.TYPE_CODE_CV, 
                    TENSCHAT.DUE_DATE 
                    FROM 
                    SDWIS2TX.TENSCHD 
                    LEFT JOIN 
                    SDWIS2TX.TENSCHAT 
                    ON 
                    TENSCHD.TENSCHD_IS_NUMBER = TENSCHAT.TENSCHD_IS_NUMBER 
                    WHERE 
                    SDWIS2TX.TENSCHD.TINWSYS_IS_NUMBER = '{}'""".format(tinwsys)
    c.execute(sql_statement)
    options = ["LCNT", "CCST", "LCTS", 'CCTI']
    for row in c.fetchall():
        if row[3] in options:
            effective = row[1]
            if effective is not None:
                effective = effective.date()
            closed = row[2]
            if closed is not None:
                closed = closed.date()
            due = row[4]
            if due is not None:
                due = due.date()
            compliance.append([row[0], effective, closed, row[3], due])
    return compliance


def compliance_pull(u, p, type_code, year, option):
    dsn_tns = cx_Oracle.makedsn('.gov link', 'port number', service_name='another .gov link')
    conn = cx_Oracle.connect(u, p, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    compliance = []
    sql_statement = """
                    SELECT 
                    TINWSYS.NUMBER0, 
                    TINWSYS.TINWSYS_IS_NUMBER, 
                    TINWSYS.NAME, 
                    TINWSYS.ACTIVITY_STATUS_CD, 
                    TINWSYS.D_POPULATION_COUNT, 
                    TINWSYS.PWS_ST_TYPE_CD, 
                    TENSCHD.TENSCHD_IS_NUMBER, 
                    TENSCHD.EFFECTIVE_DATE, 
                    TENSCHD.CLOSED_DATE, 
                    TENSCHD.TYPE_CODE_CV, 
                    TENSCHAT.DUE_DATE 
                    FROM 
                    SDWIS2TX.TINWSYS
                    LEFT JOIN 
                    SDWIS2TX.TENSCHD 
                    ON
                    SDWIS2TX.TENSCHD.TINWSYS_IS_NUMBER = TINWSYS.TINWSYS_IS_NUMBER
                    LEFT JOIN 
                    SDWIS2TX.TENSCHAT 
                    ON 
                    TENSCHD.TENSCHD_IS_NUMBER = TENSCHAT.TENSCHD_IS_NUMBER 
                    WHERE 
                    TENSCHD.TYPE_CODE_CV = '{}'""".format(type_code)
    c.execute(sql_statement)
    for row in c.fetchall():
        schedule_year = row[7].date().year
        if year is not None:
            if schedule_year == int(year):
                if option == "ALL SCHEDULES":
                    compliance.append(row)
                elif option == "OPEN SCHEDULES":
                    if row[8] is None:
                        compliance.append(row)
                elif option == "CLOSED SCHEDULES":
                    if row[8] is not None:
                        compliance.append(row)
        else:
            if option == "OPEN SCHEDULES":
                if row[8] is None:
                    compliance.append(row)
    print("COMP SHEDS: ", len(compliance))
    return compliance


def schedule_info(c, tinwsys):
    scheds = []
    c.execute("SELECT DISTINCT TMNSSGRP.REASON_TEXT, TMNSSGRP.BEGIN_DATE, TMNSSGRP.END_DATE, TMNMNR.SAMPLE_TYPE_CODE, "
              "TMNMNR.SAMPLE_COUNT, TMNMNR.SMPL_CNT_UNIT_CD, TMNMNR.TMNVTYPE_IS_NUMBER "
              "FROM SDWIS2TX.TINWSYS "
              "LEFT JOIN SDWIS2TX.TMNSASCH "
              "ON TINWSYS.TINWSYS_IS_NUMBER = TMNSASCH.TINWSYS_IS_NUMBER "
              "LEFT JOIN SDWIS2TX.TMNSSGRP "
              "ON TMNSASCH.TMNSSGRP_IS_NUMBER = TMNSSGRP.TMNSSGRP_IS_NUMBER "
              "LEFT JOIN SDWIS2TX.TMNMNR "
              "ON TMNSSGRP.TMNMNR_IS_NUMBER = TMNMNR.TMNMNR_IS_NUMBER "
              "WHERE TINWSYS.D_POPULATION_COUNT > 0 "
              "AND TINWSYS.ACTIVITY_STATUS_CD = 'A' "
              # "AND TMNSASCH.END_DATE IS NULL "
              "AND TMNMNR.TSAANGRP_IS_NUMBER = 1"
              "AND TINWSYS.TINWSYS_IS_NUMBER = '{}'".format(tinwsys))
    for row in c.fetchall():
        comment = row[0]
        comment = comment.replace('\r', "").replace('\n', '')
        begin_date = row[1]
        if begin_date is not None:
            begin_date = begin_date.date()
        year = begin_date.year
        end_date = row[2]
        if end_date is not None:
            end_date = end_date.date()
        sample_code = row[3]
        sample_count = row[4]
        sample_unit_code = row[5]
        tmnvtype = row[6]
        schedule = str(year)[2:] + " " + sample_unit_code
        year_start = datetime.date(year, 1, 1)
        year_half = datetime.date(year, 6, 30)
        if schedule[3:5] == "6M":
            if time_in_range(year_start, year_half, begin_date):
                schedule = str(year)[2:] + " 6M1"
            else:
                schedule = str(year)[2:] + " 6M2"
        lst = [schedule, comment, begin_date, end_date, sample_code, sample_count, sample_unit_code, tmnvtype]
        scheds.append(lst)
    scheds = sorted(scheds, key=itemgetter(2))
    index = 0
    current = ""
    for sched in scheds:
        if sched[3] is None:
            current = scheds.pop(index)
        index += 1
    if not current:
        current = ["None", "None", "None", "None", "None", "None", "None", "None"]
    return [current, scheds]


def specific_schedule(c, schedule, year, tinwsys):
    scheds = []
    c.execute("SELECT DISTINCT "
              "TMNSSGRP.BEGIN_DATE, "
              "TMNSSGRP.END_DATE, "
              "TMNMNR.SAMPLE_TYPE_CODE, "
              "TMNMNR.SAMPLE_COUNT, "
              "TMNMNR.SMPL_CNT_UNIT_CD, "
              "TMNMNR.TMNVTYPE_IS_NUMBER "
              "FROM SDWIS2TX.TINWSYS "
              "LEFT JOIN SDWIS2TX.TMNSASCH "
              "ON TINWSYS.TINWSYS_IS_NUMBER = TMNSASCH.TINWSYS_IS_NUMBER "
              "LEFT JOIN SDWIS2TX.TMNSSGRP "
              "ON TMNSASCH.TMNSSGRP_IS_NUMBER = TMNSSGRP.TMNSSGRP_IS_NUMBER "
              "LEFT JOIN SDWIS2TX.TMNMNR "
              "ON TMNSSGRP.TMNMNR_IS_NUMBER = TMNMNR.TMNMNR_IS_NUMBER "
              "WHERE TMNMNR.TSAANGRP_IS_NUMBER = 1"
              "AND  TMNMNR.SMPL_CNT_UNIT_CD = '{}'"
              "AND TINWSYS.TINWSYS_IS_NUMBER = '{}'".format(schedule, tinwsys))
    for row in c.fetchall():
        begin_date = row[0].date()
        schedule_year = begin_date.year
        if int(year) == schedule_year:
            print("yes")
            scheds.append(row)
    return scheds


def summary_info(c, tinwsys):
    summaries = []
    sql_statement = "SELECT " \
                    "TSASMPSM.TSASMPSM_IS_NUMBER, " \
                    "TSASMPSM.COLLECTION_STRT_DT, " \
                    "TSASMPSM.COLLECTION_END_DT, " \
                    "TSASMPSM.TSAANLYT_IS_NUMBER, " \
                    "TSAANLYT.NAME, " \
                    "TSAANLYT.CODE, " \
                    "TSASSR.TSASSR_IS_NUMBER, " \
                    "TSASSR.TYPE_CODE, " \
                    "TSASSR.COUNT_QTY, " \
                    "TSASSR.MEASURE, " \
                    "TSASSR.UOM_CODE " \
                    "FROM " \
                    "SDWIS2TX.TSASMPSM " \
                    "LEFT JOIN " \
                    "SDWIS2TX.TSAANLYT " \
                    "ON " \
                    "TSASMPSM.TSAANLYT_IS_NUMBER = TSAANLYT.TSAANLYT_IS_NUMBER " \
                    "LEFT JOIN " \
                    "SDWIS2TX.TSASSR " \
                    "ON " \
                    "TSASMPSM.TSASMPSM_IS_NUMBER = TSASSR.TSASMPSM_IS_NUMBER " \
                    "WHERE " \
                    "TSASMPSM.TINWSYS_IS_NUMBER = {}".format(tinwsys)
    c.execute(sql_statement)
    for row in c.fetchall():
        row = strip_lst(row)
        analytes = [705, 803]
        tsasmpsm = row[0]
        start_date = row[1]
        if start_date is None:
            start_date = datetime.datetime(1900, 1, 1)
        end_date = row[2]
        if end_date is None:
            end_date = datetime.datetime(1900, 1, 1)
        tsaanlyt = row[3]
        name = row[4]  # LEAD OR COPPER SUMMARY
        name = "{:14}".format(name)
        code = row[5]  # PB90 OR CU90
        tsassr = row[6]
        type_code = row[7]  #90 OR 95 PERCENTILES
        count = row[8]  # SAMPLE COUNT
        measure = row[9]
        if measure is None:
            measure = 0.0
        status = ""
        if code == "PB90":
            if measure > 0.0154:
                status = "ALE"
            elif measure > 0.0054:
                status = "OVER RML"
            else:
                status = "UNDER RML"
        elif code == "CU90":
            if measure > 1.34:
                status = "ALE"
            elif measure > 0.654:
                status = "OVER RML"
            else:
                status = "UNDER RML"
        if measure is not None:
            measure = '{:7}'.format(measure)
        uom_code = row[10]  # mg/L
        if tsaanlyt in analytes:
            if type_code == '90':
                lst = [tsasmpsm, start_date, end_date, tsaanlyt, name, code, tsassr, type_code, count, measure,
                       uom_code, status]
                summaries.append(lst)
    # summaries = sorted(summaries, key=itemgetter(1))
    periods = {}
    sum_keys = []
    holder = []
    for summ in summaries:
        date_key = str(summ[1].year) + "-" + str(summ[1].month)
        sum_keys.append(date_key)
    periods = periods.fromkeys(sum_keys)
    for key in periods:
        periods[key] = []
    for summ in summaries:
        date_key = str(summ[1].year) + "-" + str(summ[1].month)
        periods[date_key].append(summ)
    for key in periods:
        unsorted_period_sums = periods[key]
        periods[key] = sorted(unsorted_period_sums, key=itemgetter(0))
    for key in periods:
        val = periods[key]
        lst = [key, val]
        holder.append(lst)
    summaries = sorted(holder, key=itemgetter(0))
    for period in summaries:
        try:
            if period[1][1]:
                pass
        except IndexError:
            if period[1][0][3] == 705:
                # create blank copper summary
                date = period[1][0][1]
                copper = [0, date, date, 803, 'COPPER SUMMARY', 'CU90', 0, '90', 0, '    0.0', 'MG/L', 'NONE']
                period[1].append(copper)
            elif period[1][0][3] == 803:
                # create blank lead summary
                date = period[1][0][1]
                lead = [0, date, date, 705, 'LEAD SUMMARY  ', 'PB90', 0, '90', 0, '    0.0', 'MG/L', 'NONE']
                period[1].insert(0, lead)
    return summaries


def scheduling_summary_pull(user, pw, lst):
    dsn_tns = cx_Oracle.makedsn('.gov link', 'port number', service_name='another .gov link')
    conn = cx_Oracle.connect(user, pw, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    summaries = []
    for schedule in lst:
        tinwsys = schedule[1]
        year = schedule[6].date().year
        sample_count = schedule[9]
        sql_statement = "SELECT " \
                        "TSASMPSM.TSASMPSM_IS_NUMBER, " \
                        "TSASMPSM.COLLECTION_STRT_DT, " \
                        "TSASMPSM.COLLECTION_END_DT, " \
                        "TSASMPSM.TSAANLYT_IS_NUMBER, " \
                        "TSAANLYT.NAME, " \
                        "TSAANLYT.CODE, " \
                        "TSASSR.TSASSR_IS_NUMBER, " \
                        "TSASSR.TYPE_CODE, " \
                        "TSASSR.COUNT_QTY, " \
                        "TSASSR.MEASURE, " \
                        "TSASSR.UOM_CODE " \
                        "FROM " \
                        "SDWIS2TX.TSASMPSM " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TSAANLYT " \
                        "ON " \
                        "TSASMPSM.TSAANLYT_IS_NUMBER = TSAANLYT.TSAANLYT_IS_NUMBER " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TSASSR " \
                        "ON " \
                        "TSASMPSM.TSASMPSM_IS_NUMBER = TSASSR.TSASMPSM_IS_NUMBER " \
                        "WHERE " \
                        "TSASMPSM.TINWSYS_IS_NUMBER = {}".format(tinwsys)
        c.execute(sql_statement)
        for row in c.fetchall():
            row = strip_lst(row)
            analytes = [705, 803]
            tsasmpsm = row[0]
            start_date = row[1]
            end_date = row[2]
            tsaanlyt = row[3]
            name = row[4]  # LEAD OR COPPER SUMMARY
            name = "{:14}".format(name)
            code = row[5]  # PB90 OR CU90
            tsassr = row[6]
            type_code = row[7]  #90 OR 95 PERCENTILES
            count = row[8]  # SAMPLE COUNT
            measure = row[9]
            if measure is not None:
                measure = '{:7}'.format(measure)
            uom_code = row[10]  # mg/L
            if tsaanlyt in analytes:
                if type_code == '90':
                    if start_date.date().year == year:
                        if count >= sample_count:
                            lst = [tsasmpsm, start_date, end_date, tsaanlyt, name, code, tsassr, type_code, count,
                                   measure, uom_code]
                    summaries.append(lst)
    # summaries = sorted(summaries, key=itemgetter(1))
    periods = {}
    sum_keys = []
    holder = []
    for summ in summaries:
        date_key = str(summ[1].year) + "-" + str(summ[1].month)
        sum_keys.append(date_key)
    periods = periods.fromkeys(sum_keys)
    for key in periods:
        periods[key] = []
    for summ in summaries:
        date_key = str(summ[1].year) + "-" + str(summ[1].month)
        periods[date_key].append(summ)
    for key in periods:
        unsorted_period_sums = periods[key]
        periods[key] = sorted(unsorted_period_sums, key=itemgetter(0))
    for key in periods:
        val = periods[key]
        lst = [key, val]
        holder.append(lst)
    summaries = sorted(holder, key=itemgetter(0))
    return summaries


def summary_pull(u, p, code, year):
    dsn_tns = cx_Oracle.makedsn('.gov link', 'port', service_name='.gov link')
    conn = cx_Oracle.connect(u, p, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    summaries = []
    tsaanlyt = ""
    if code[:2] == "PB":
        tsaanlyt = 705
    elif code[:2] == "CU":
        tsaanlyt = 803
    sql_statement = "SELECT " \
                    "TINWSYS.NUMBER0, " \
                    "TINWSYS.TINWSYS_IS_NUMBER, " \
                    "TINWSYS.NAME, " \
                    "TINWSYS.ACTIVITY_STATUS_CD, " \
                    "TINWSYS.D_POPULATION_COUNT, " \
                    "TINWSYS.PWS_ST_TYPE_CD, " \
                    "TSASMPSM.TSASMPSM_IS_NUMBER, " \
                    "TSASMPSM.COLLECTION_STRT_DT, " \
                    "TSASMPSM.COLLECTION_END_DT, " \
                    "TSASMPSM.TSAANLYT_IS_NUMBER, " \
                    "TSAANLYT.NAME, " \
                    "TSAANLYT.CODE, " \
                    "TSASSR.TSASSR_IS_NUMBER, " \
                    "TSASSR.TYPE_CODE, " \
                    "TSASSR.COUNT_QTY, " \
                    "TSASSR.MEASURE, " \
                    "TSASSR.UOM_CODE " \
                    "FROM " \
                    "SDWIS2TX.TINWSYS " \
                    "LEFT JOIN " \
                    "SDWIS2TX.TSASMPSM " \
                    "ON " \
                    "TINWSYS.TINWSYS_IS_NUMBER = TSASMPSM.TINWSYS_IS_NUMBER " \
                    "LEFT JOIN " \
                    "SDWIS2TX.TSAANLYT " \
                    "ON " \
                    "TSASMPSM.TSAANLYT_IS_NUMBER = TSAANLYT.TSAANLYT_IS_NUMBER " \
                    "LEFT JOIN " \
                    "SDWIS2TX.TSASSR " \
                    "ON " \
                    "TSASMPSM.TSASMPSM_IS_NUMBER = TSASSR.TSASMPSM_IS_NUMBER " \
                    "WHERE " \
                    "TSASMPSM.TSAANLYT_IS_NUMBER = {}".format(tsaanlyt)
    c.execute(sql_statement)
    for row in c.fetchall():

        start_date = row[7].date().year
        row = strip_lst(row)
        type_code = row[13]
        measure = row[15]
        lst = [row[0], row[2], row[3], row[4], str(row[7].date()), measure]
        if year is not None:
            if start_date == int(year):
                if type_code == '90':
                    if code == 'PB ALE':
                        if measure > 0.0154:
                            summaries.append(lst)
                    elif code == 'PB>RML':
                        if measure > 0.0054:
                            summaries.append(lst)
                    elif code == 'CU ALE':
                        if measure > 1.354:
                            summaries.append(lst)
                    elif code == 'CU>RML':
                        if measure > 0.654:
                            summaries.append(lst)
        else:
            if type_code == '90':
                if code == 'PB ALE':
                    if measure > 0.0154:
                        summaries.append(lst)
                elif code == 'PB>RML':
                    if measure > 0.0054:
                        summaries.append(lst)
                elif code == 'CU ALE':
                    if measure > 1.354:
                        summaries.append(lst)
                elif code == 'CU>RML':
                    if measure > 0.654:
                        summaries.append(lst)
    print("Summaries Found: ", len(summaries))
    return summaries


def wqp_schedules(c, tinwsys):
    wqps = []
    sql_statement = """SELECT DISTINCT 
                       SDWIS2TX.TMNSSGRP.REASON_TEXT,
                       SDWIS2TX.TMNSSGRP.BEGIN_DATE,
                       SDWIS2TX.TMNSSGRP.END_DATE,
                       SDWIS2TX.TMNMNR.SAMPLE_TYPE_CODE,
                       SDWIS2TX.TMNMNR.SAMPLE_COUNT,
                       SDWIS2TX.TMNMNR.SMPL_CNT_UNIT_CD,
                       SDWIS2TX.TMNMNR.TMNVTYPE_IS_NUMBER,
                       SDWIS2TX.TMNMNR.TSAANGRP_IS_NUMBER
                       FROM SDWIS2TX.TMNSASCH
                       LEFT JOIN SDWIS2TX.TMNSSGRP
                       ON SDWIS2TX.TMNSASCH.TMNSSGRP_IS_NUMBER = SDWIS2TX.TMNSSGRP.TMNSSGRP_IS_NUMBER
                       LEFT JOIN SDWIS2TX.TMNMNR
                       ON SDWIS2TX.TMNSSGRP.TMNMNR_IS_NUMBER     = SDWIS2TX.TMNMNR.TMNMNR_IS_NUMBER
                       WHERE SDWIS2TX.TMNSASCH.TINWSYS_IS_NUMBER = {} 
                       AND SDWIS2TX.TMNSSGRP.BEGIN_DATE          > '01-JUL-13'
                       AND ((SDWIS2TX.TMNMNR.TSAANGRP_IS_NUMBER  = 11)
                       OR (SDWIS2TX.TMNMNR.TSAANGRP_IS_NUMBER    = 16)
                       OR (SDWIS2TX.TMNMNR.TSAANGRP_IS_NUMBER    = 17)
                       OR (SDWIS2TX.TMNMNR.TSAANGRP_IS_NUMBER    = 22))""".format(tinwsys)
    c.execute(sql_statement)
    for row in c.fetchall():
        begin = row[1]
        if begin is not None:
            begin = begin.date()
        end = row[2]
        if end is not None:
            end = end.date()
        wqps.append([begin, end, row[3], row[4], row[5]])
    return wqps


def sample_site_info(c, tinwsf0is):
    c.execute("SELECT IDENTIFICATION_CD, DESCRIPTION_TEXT, LD_CP_TIER_LEV_TXT, LD_CP_TIER_TYP_TXT, "
              "D_LAST_UPDT_TS, D_USERID_CODE, ACTIVITY_STATUS_CD "
              "FROM SDWIS2TX.TSASMPPT "
              "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))
    val = c.fetchall()
    sites = []
    loc_len = []
    for v in val:
        if v[0][:3] == 'LCR':
            _id = v[0]
            loc = v[1]
            if loc is not None:
                loc_len.append(len(loc))
            else:
                loc = "NO ADDRESS"
                loc_len.append(0)
            tier = v[2]
            material = v[3]
            update = v[4].date()
            user_id = v[5]
            activity = v[6]
            lst = [_id, loc, tier, material, user_id, update, activity]
            sites.append(lst)
    sites = sorted(sites, key=itemgetter(0))
    try:
        space = max(loc_len) + 2
    except ValueError:
        space = 30
    space = '{:' + str(space) + '}'
    for site in sites:
        site[1] = space.format(site[1])
    return sites


def sample_plan_info(c, tinwsys):
    lst = []
    c.execute("SELECT APPROVAL_DATE, BEGIN_DATE "
              "FROM SDWIS2TX.TMNSAPLN "
              "WHERE TINWSYS_IS_NUMBER = '{}'".format(tinwsys))
    for row in c.fetchall():
        approval = row[0]
        if approval is not None:
            approval = approval.date()
        begin = row[1]
        if begin is not None:
            begin = begin.date()
        lst.append([approval, begin])
    return lst


def schedule_summary_group(scheds, summaries):
    scheds_summs = []
    for sched in scheds:
        schedule = sched[0][3:]
        sched_year = int('20' + sched[0][:3])
        for summ in summaries:
            collection_date = summ[0]
            year = int(collection_date[:4])
            month = int(collection_date[5:])
            collection_date = datetime.date(year, month, 1)
            if schedule == "6M1":
                sched_start = datetime.date(sched_year, 1, 1)
                sched_end = datetime.date(sched_year, 6, 30)
                if time_in_range(sched_start, sched_end, collection_date):
                    scheds_summs.append([[sched], [summ]])
            elif schedule == "6M2":
                sched_start = datetime.date(sched_year, 7, 1)
                sched_end = datetime.date(sched_year, 12, 30)
                if time_in_range(sched_start, sched_end, collection_date):
                    scheds_summs.append([[sched], [summ]])
            elif schedule == "YR ":
                sched_start = datetime.date(sched_year, 1, 1)
                sched_end = datetime.date(sched_year, 12, 30)
                if time_in_range(sched_start, sched_end, collection_date):
                    scheds_summs.append([[sched], [summ]])
            elif schedule == "3Y ":
                sched_year2 = sched_year + 2
                sched_start = datetime.date(sched_year, 1, 1)
                sched_end = datetime.date(sched_year2, 12, 30)
                if time_in_range(sched_start, sched_end, collection_date):
                    scheds_summs.append([[sched], [summ]])
            elif schedule == "9Y ":
                sched_year2 = sched_year + 8
                sched_start = datetime.date(sched_year, 1, 1)
                sched_end = datetime.date(sched_year2, 12, 30)
                if time_in_range(sched_start, sched_end, collection_date):
                    scheds_summs.append([[sched], [summ]])
        lst = []
        for group in scheds_summs:
            n = group[0]
            lst.append(n)
        if sched not in lst:
            scheds_summs.append([[sched], ["No Summary Found"]])
    lst = []
    for summ in summaries:
        n = summ[1]
        lst.append(n)
    for summ in summaries:
        if summ not in lst:
            scheds_summs.append([["No Schedule Found"], summ])
    return scheds_summs


def data_pull(user, pw, raw):
    if len(raw) == 7:
        raw = "TX" + str(raw)
    if len(raw) == 9:
        if raw[:2] == 'tx':
            raw = "TX" + raw[2:]
    dsn_tns = cx_Oracle.makedsn('.gov', 'port', service_name='.gov')
    conn = cx_Oracle.connect(user, pw, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    inv_info = inventory_info(c, raw)
    tinwsys = inv_info[6]
    tinwsf0is = inv_info[7]
    indicators = indicator_info(c, tinwsys)
    milestones = milestone_info(c, tinwsys)
    violations = violation_info(c, tinwsys)
    violations = group_violations(violations)
    closed = violations[0]
    open = violations[1]
    compliance = compliance_info(c, tinwsys)
    scheds = schedule_info(c, tinwsys)
    if inv_info[4] != 0:
        if inv_info[5] != "NC":
            if scheds[0][0] == "None":
                print(raw)
    summaries = summary_info(c, tinwsys)
    wqps = wqp_schedules(c, tinwsys)
    sites = sample_site_info(c, tinwsf0is)
    plan = sample_plan_info(c, tinwsys)
    # scheds_summs = schedule_summary_group(scheds, summaries)
    c.close()
    conn.close()
    lst = [inv_info, indicators, milestones, closed, open, compliance, scheds, summaries, wqps, sites, plan]
    return lst


def schedule_monitoring(user, pw, schedule, year, option):
    schedules = []
    count = 0
    year = str(year[2:])
    if schedule == "6M2":
        schedule = "6M"
        date = "01-JUL-{}".format(year)
    elif schedule == "6M1":
        schedule = "6M"
        date = "01-JAN-{}".format(year)
    else:
        date = "01-JAN-{}".format(year)
    sql_statement = "SELECT DISTINCT " \
                    "TINWSYS.NUMBER0, " \
                    "TINWSYS.TINWSYS_IS_NUMBER, " \
                    "TINWSYS.NAME, " \
                    "TINWSYS.ACTIVITY_STATUS_CD, " \
                    "TINWSYS.D_POPULATION_COUNT, " \
                    "TINWSYS.PWS_ST_TYPE_CD, " \
                    "TMNSSGRP.BEGIN_DATE, " \
                    "TMNSSGRP.END_DATE, " \
                    "TMNMNR.SAMPLE_TYPE_CODE, " \
                    "TMNMNR.SAMPLE_COUNT, " \
                    "TMNMNR.SMPL_CNT_UNIT_CD, " \
                    "TMNMNR.TMNVTYPE_IS_NUMBER " \
                    "FROM SDWIS2TX.TINWSYS " \
                    "LEFT JOIN SDWIS2TX.TMNSASCH " \
                    "ON TINWSYS.TINWSYS_IS_NUMBER = TMNSASCH.TINWSYS_IS_NUMBER " \
                    "LEFT JOIN SDWIS2TX.TMNSSGRP " \
                    "ON TMNSASCH.TMNSSGRP_IS_NUMBER = TMNSSGRP.TMNSSGRP_IS_NUMBER " \
                    "LEFT JOIN SDWIS2TX.TMNMNR " \
                    "ON TMNSSGRP.TMNMNR_IS_NUMBER = TMNMNR.TMNMNR_IS_NUMBER " \
                    "WHERE TMNMNR.TSAANGRP_IS_NUMBER = 1 " \
                    "AND TINWSYS.ACTIVITY_STATUS_CD = 'A' " \
                    "AND  TMNMNR.SMPL_CNT_UNIT_CD = '{}' " \
                    "AND TMNSSGRP.BEGIN_DATE = '{}'".format(schedule, date)
    dsn_tns = cx_Oracle.makedsn('.gov', 'port', service_name='.gov')
    conn = cx_Oracle.connect(user, pw, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    c.execute(sql_statement)
    for row in c.fetchall():
        count += 1
        end_date = row[7]
        if option == "ALL SCHEDULES":
            schedules.append(row)
        elif option == "OPEN SCHEDULES":
            if end_date is None:
                schedules.append(row)
        elif option == "CLOSED SCHEDULES":
            if end_date is not None:
                schedules.append(row)
    print("Number of schedules: ", count)
    return schedules


def summary_pull_by_schedule(u, p, lst):
    dsn_tns = cx_Oracle.makedsn('.gov', 'port', service_name='.gov')
    conn = cx_Oracle.connect(u, p, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    summaries = {}
    for schedule in lst:
        lst_of_705 = []
        lst_of_803 = []
        tinwsys = schedule[1]
        begin_date = schedule[6].date()
        year = begin_date.year
        month = begin_date.month
        sample_count = schedule[9]
        schedule_type = schedule[10]
        end = datetime.date(year, 12, 30)
        if schedule_type == "6M":
            if month == 1:
                end = datetime.date(year, 9, 30)
            else:
                end = datetime.date((year + 1), 3, 31)
        elif schedule_type == "3Y ":
            end = datetime.date((year + 2), 12, 30)
        elif schedule_type == "9Y":
            end = datetime.date((year + 8), 12, 30)
        lst = [schedule[0], schedule[2], schedule[3], schedule[4], sample_count]
        sql_statement = "SELECT " \
                        "TSASMPSM.TSASMPSM_IS_NUMBER, " \
                        "TSASMPSM.COLLECTION_STRT_DT, " \
                        "TSASMPSM.COLLECTION_END_DT, " \
                        "TSASMPSM.TSAANLYT_IS_NUMBER, " \
                        "TSAANLYT.NAME, " \
                        "TSAANLYT.CODE, " \
                        "TSASSR.TSASSR_IS_NUMBER, " \
                        "TSASSR.TYPE_CODE, " \
                        "TSASSR.COUNT_QTY, " \
                        "TSASSR.MEASURE, " \
                        "TSASSR.UOM_CODE " \
                        "FROM " \
                        "SDWIS2TX.TSASMPSM " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TSAANLYT " \
                        "ON " \
                        "TSASMPSM.TSAANLYT_IS_NUMBER = TSAANLYT.TSAANLYT_IS_NUMBER " \
                        "LEFT JOIN " \
                        "SDWIS2TX.TSASSR " \
                        "ON " \
                        "TSASMPSM.TSASMPSM_IS_NUMBER = TSASSR.TSASMPSM_IS_NUMBER " \
                        "WHERE " \
                        "TSASMPSM.COLLECTION_STRT_DT is not null " \
                        "AND " \
                        "TSASMPSM.TINWSYS_IS_NUMBER = {}".format(tinwsys)
        c.execute(sql_statement)
        for row in c.fetchall():
            row = strip_lst(row)
            analytes = [705, 803]
            tsasmpsm = row[0]
            start_date = row[1]
            if start_date is not None:
                start_date = start_date.date()
            end_date = row[2]
            if end_date is not None:
                end_date = end_date.date()
            tsaanlyt = row[3]
            name = row[4]  # LEAD OR COPPER SUMMARY
            name = "{:14}".format(name)
            code = row[5]  # PB90 OR CU90
            tsassr = row[6]
            type_code = row[7]  #90 OR 95 PERCENTILES
            count = row[8]  # SAMPLE COUNT
            measure = row[9]
            if measure is not None:
                measure = '{:7}'.format(measure)
            uom_code = row[10]  # mg/L
            if tsaanlyt in analytes:
                if type_code == '90':
                    if time_in_range(begin_date, end, start_date):
                        if count >= sample_count:
                            if tsaanlyt == 705:
                                lst_of_705 = [tsasmpsm, start_date, end_date, tsaanlyt, name, code, tsassr, type_code,
                                              count, measure, uom_code]
                            elif tsaanlyt == 803:
                                lst_of_803 = [tsasmpsm, start_date, end_date, tsaanlyt, name, code, tsassr, type_code,
                                              count, measure, uom_code]
        if lst_of_705:
            if lst_of_803:
                summaries[tinwsys] = [lst, lst_of_705, lst_of_803]
    return summaries


def sampling_export(u, p, raw):
    pws_id = str(raw)
    if len(raw) == 7:
        pws_id = "TX" + str(raw)
    if len(raw) == 9:
        if raw[:2] == 'tx':
            pws_id = "TX" + raw[2:]
        else:
            pws_id = raw
    dsn_tns = cx_Oracle.makedsn('.gov', 'port', service_name='.gov')
    conn = cx_Oracle.connect(u, p, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    lst = inventory_info(c, pws_id)
    sample_sites = sample_site_info(c, lst[7])
    sample_plan = sample_plan_info(c, lst[6])
    return [lst, sample_sites, strip_lst(sample_plan)]


def sample_sites(c, tinwsf0is):
    c.execute("SELECT TSASMPPT_IS_NUMBER, IDENTIFICATION_CD, DESCRIPTION_TEXT "
              "FROM SDWIS2TX.TSASMPPT "
              "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))
    val = c.fetchall()
    sites = []
    for v in val:
        if v[1][:3] == 'LCR':
            tsasmppt = v[0]
            _id = v[1]
            loc = v[2]
            lst = [tsasmppt, _id, loc]
            sites.append(lst)
    return sites


def sample_results(c, lst):
    results = []
    for sample_site in lst:
        tsasmppt = sample_site[0]
        lcr_id = sample_site[1]
        description_text = sample_site[2]
        c.execute("SELECT TSASAMPL_IS_NUMBER, COLLLECTION_END_DT, REJECT_REASON_CD, COLLECTION_ADDRESS "
                  "FROM SDWIS2TX.TSASAMPL "
                  "WHERE TSASMPPT_IS_NUMBER = '{}'".format(tsasmppt))
        val = c.fetchall()
        for v in val:
            tsasampl = v[0]
            date = v[1].date()
            reject_reason = v[2]
            collection_address = v[3]
            results.append([tsasampl, lcr_id, description_text, collection_address, date, reject_reason])
    return results


def find_samples(u, p, raw):
    pws_id = str(raw)
    if len(raw) == 7:
        pws_id = "TX" + str(raw)
    if len(raw) == 9:
        if raw[:2] == 'tx':
            pws_id = "TX" + raw[2:]
        else:
            pws_id = raw
    dsn_tns = cx_Oracle.makedsn('.gov', 'port', service_name='.gov')
    conn = cx_Oracle.connect(u, p, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    lst = inventory_info(c, pws_id)
    sample_sites_lst = sample_sites(c, lst[7])
    sample_results_lst = sample_results(c, sample_sites_lst)

    return sample_results_lst


def testing(u, p):
    dsn_tns = cx_Oracle.makedsn('.gov', 'port', service_name='.gov')
    conn = cx_Oracle.connect(u, p, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    lst = water_systems(c)
    print("List of active water systems generated")
    length = len(lst)
    print("Number of systems: ", length)
    return lst
