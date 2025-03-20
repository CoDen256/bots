addr = document.querySelector("#is24-content > div.grid-item.padding-desk-right-xl.desk-two-thirds.lap-one-whole.desk-column-left.flex-item.palm--flex__order--1.lap--flex__order--1 > div.is24-ex-details.main-criteria-headline-size.two-column-layout > div:nth-child(1) > div.grid.grid-flex.grid-fill-rows.margin-bottom-l.margin-top-s > div.grid-item.desk-one-half.lap-one-half.palm-one-whole.address-with-map-link > div.grid.grid-flex > div.grid-item.one-half > span > div > div").textContent
addr_full = addr.trim().split("\n")[0].slice(0, -1)
plz = addr.trim().split("\n")[1].trim().split(' ')[1]

time = document.querySelector("#is24-expose-travel-time > div > div.travelTimeAddressesContainer_tlZVi").textContent
work  = time.split("Germany")[0].trim().split(" min")[0]
htwk = time.split("Germany")[1].trim().split(" min")[0]


url = window.location.href
flache = document.querySelector("#is24-content > div.grid-item.padding-desk-right-xl.desk-two-thirds.lap-one-whole.desk-column-left.flex-item.palm--flex__order--1.lap--flex__order--1 > div.is24-ex-details.main-criteria-headline-size.two-column-layout > div.criteriagroup.flex.flex--wrap.main-criteria-container > div:nth-child(3) > div.is24qa-flaeche-main.is24-value.font-semibold")
warm = document.querySelector("#is24-content > div.grid-item.padding-desk-right-xl.desk-two-thirds.lap-one-whole.desk-column-left.flex-item.palm--flex__order--1.lap--flex__order--1 > div.is24-ex-details.main-criteria-headline-size.two-column-layout > div.criteriagroup.flex.flex--wrap.main-criteria-container > div:nth-child(4) > div > div.is24qa-warmmiete-main.is24-value.font-semibold").textContent

flache_full = flache.textContent.trim().split(" ")[0]
warm_full = warm.trim().split(' ')[0]

ebk = (document.documentElement.textContent || document.documentElement.innerText).indexOf('inbauk') > -1 || (document.documentElement.textContent || document.documentElement.innerText).indexOf('EBK') > -1
ebk_full = ebk ? 1: -1


etage_frei_tiere = document.querySelector("#is24-content > div.grid-item.padding-desk-right-xl.desk-two-thirds.lap-one-whole.desk-column-left.flex-item.palm--flex__order--1.lap--flex__order--1 > div.is24-ex-details.main-criteria-headline-size.two-column-layout > div.criteriagroup.flex.flex--wrap.criteria-group--spacing.padding-top-s > div:nth-child(1)").textContent
bezug = etage_frei_tiere.trim().split("Bezugsfrei ab")[1].trim().split(" ")[0]
etage = ""
etage = etage_frei_tiere.split("Etage\n")[1].trim().split(" ")[0]
tiere = "Nach Vereinbarung"
tiere = etage_frei_tiere.split("Haustiere")[1].trim().split("\n")[0]
tiere_full = tiere == "Nein" ? -1 : (tiere == "Nach Vereinbarung" ? 0 : 1)

heiz=document.querySelector("#is24-content > div.grid-item.padding-desk-right-xl.desk-two-thirds.lap-one-whole.desk-column-left.flex-item.palm--flex__order--1.lap--flex__order--1 > div.is24-ex-details.main-criteria-headline-size.two-column-layout > div.criteriagroup.flex.flex--wrap.criteria-group--spacing.padding-top-s > div.criteriagroup.criteria-group--border.criteria-group--two-columns.criteria-group--spacing").textContent
heiz_full = heiz.split("sart")[1].trim().split("\n")[0]
vermieter = document.querySelector("#is24-expose-contact-box > div > div > div.one-whole.contactBoxRealtorData_mOkbU > div.realtorInfoVerticalRepair_FNx\\+v > div > div.truncateChild_5TDve.font-semibold").textContent
tel = ""
tel_full = ""
tel_mobil = ""

tel = document.querySelector("#is24-expose-popup > div > div:nth-child(1) > div:nth-child(3)").textContent
tel_full = tel.split("Telefon: ")[1].split(" ").slice(0, 2).join("")
tel_mobil = tel.split("Mobil:")[1].trim().split(" ").slice(0, 2).join("")

console.log(`${addr_full}\n${url}\n${plz}\n${warm_full}\n${flache_full}\n${bezug}\n${work}\n${htwk}\n${tiere_full}\n${ebk_full}\n${etage}\n${heiz_full}\n${vermieter}\n${tel_full}\n${tel_mobil}`)
