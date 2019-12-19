# tceq_auto_letter
Takes TCEQ PWS data from Excel and generates form letters for mailing<br>

scrape.py <== Loads Excel files, pulls relevant data into a dictionary, and pickles dictionary<br>
anaylze.py <== Determines approval of sample site plan for each PWS<br>
check.py <== Determines if total sum of approvals, denials, and edge-cases equals the total sum of PWS<br>
sampling.py <== Two functions: 1) for sampling intervals of an analyzed dictionary, 2) for displaying edge-case dictionary for       approval/denial<br>
mail_basic.py <== MailMerge for multiple letters<br>
mail_table_merge.py <== MailMerge for multiple letters with variable table data<br>
test.py <== Contains functions for vasious testing<br>
