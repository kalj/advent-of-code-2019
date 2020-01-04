

def get_variants(n):
    s = str(n)
    nstrs = [s[0:1]+s[0:],
             s[0:2]+s[1:],
             s[0:3]+s[2:],
             s[0:4]+s[3:],
             s[0:5]+s[4:]]
    return [int(s) for s in nstrs]

nums = [17894,
        78999,
        11123,
        ]




for n in nums:
    ns = get_variants(n)
    print(n,*ns)
