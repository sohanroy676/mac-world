import re,sys
for f in sys.argv[1:]:
    ex=ed=amb=0; n=0; oth=0
    for l in open(f):
        m=re.match(r'\s+AP(\d) set=(\d+)/(\d+) ap=\S+ stas: exact=(\d+) edcaRounded\((\d+)/(\d+)\)=(\d+) other=(\d+)',l)
        if m:
            s,e,r,ed_=int(m[2]),int(m[4]),int(m[5]),int(m[7]); oth+=int(m[8]); n+=1
            if s==r: amb+=1; continue
            ex+=e; ed+=ed_
    print(f,'AP-samples',n,'set==2^k-1 (ambiguous)',amb,'STA-samples exact',ex,'rounded',ed,'share exact %.3f'%(ex/max(1,ex+ed)),'other',oth)
