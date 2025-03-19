# First
POST https://onlinetermine.arzt-direkt.com/api/appointment-category
accept: application/json, text/plain, */*
content-type: application/json
referer: sec-ch-ua: "Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"
sec-ch-ua-mobile:?0
sec-ch-ua-platform:"Windows"
user-agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0

{"birthDate":null,"localityIds":["136244789462435842","106154130175164417","106154141269098497"],"instance":"5e8d5ff3a6abce001906ae07","catId":"","insuranceType":"gkv"}


- Returns appointmentTypes with available options
- Look out for 'hasOpenings'


For requesting openings:
https://onlinetermine.arzt-direkt.com/api/opening?localityIds=&instance=63888c84a368f154129b0af0&terminSucheIdent=132158609569087490&forerunTime=0

localityIds and instance same as in previous request, and are hardcoded for markleeberg and leipzig
terminSucheIdent is the one, that specifies the actual appointment type.
