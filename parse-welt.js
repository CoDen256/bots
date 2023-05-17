
addr = document.querySelector("#exposeAddress > sd-cell > sd-cell-row > sd-cell-col.cell__col.is-center-v > span:nth-child(1)").textContent
plz = document.querySelector("#exposeAddress > sd-cell > sd-cell-row > sd-cell-col.cell__col.is-center-v > span.has-font-100.is-bold.flex.flex-wrap > div:nth-child(1)").textContent


plz_full = plz.split(" ")[0]

url = window.location.href

warm = document.querySelector("#aPreis > sd-card > sd-cell").textContent
warm_full = ""
//warm_full = parseInt(warm.split("in Warmmiete")[1].split("Warmmiete")[1].trim().split(" ")[0].slice(0, -1))
flach = document.querySelector("#aUebersicht > app-hardfacts > div > div > div.flex.ng-star-inserted > div:nth-child(1)").textContent
flache_full = flach.trim().split(" ")[0]


ebk = (document.documentElement.textContent || document.documentElement.innerText).indexOf('inbauk') > -1 || (document.documentElement.textContent || document.documentElement.innerText).indexOf('EBK') > -1
ebk_full = ebk ? 1: -1

etage = document.querySelector("#aImmobilie").textContent.split("Geschoss")[0].slice(-3,-2)

tel = ""
tel = $('a[href^="tel"]').textContent
vermiter = ""
vermiter = document.querySelector("#divAnbieter").textContent.split("Anbieter der Immobilie")[1].split(",")[0]

console.log(`${addr}\n${url}\n${plz_full}\n${warm_full}\n${flache_full}\n\n\n\n\n${ebk_full}\n${etage}\n\n${vermiter}\n${tel}`)
