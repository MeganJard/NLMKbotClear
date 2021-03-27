def work(stri):
    while '01' in stri or '02' in stri or '03' in stri:
        stri = stri.replace('01', '2302', 1)
        stri = stri.replace('02', '10', 1)
        stri = stri.replace('03', '201', 1)
    return stri

stri = '0'
for i in '1' * 40:
    for j in '2' * 10:
        for k in 3 * '8':

