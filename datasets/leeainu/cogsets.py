# coding: utf8
from __future__ import unicode_literals, print_function, division


COGSET_MAP = {
    # Language Yakumo concept woman
    # 1: menokó; menokó; menokó; menokó; menokó; menokó; menokó; menokó; menéko
    # 2: mahnekuh; maynepo; mahtekuh; mahneku; mahtekuh; mahnekuh
    {
        "menokó": 1,
        "mátnekur": 2,
    },
    # Language Yakumo concept bird
    # 1: cikáp; cikáp; cikáp; cikáp; cikáp; cikáp; cikáp; cikáp; cikáp; cikáp; cikáp; cikáp; cikah; cikap; cikah; cikah; cikah; cikap
    # 2:
    {
        "cikáp": 1,
        "ciri": 2,
    },
    # Language Yakumo concept leg
    # 1: cikír; cikír; cikír; cikír; cikír; cikír; cikír
    # 2: kemá; kemá; kemá; kemákuciki; kema; kema; kema; kema; kema; kema
    {
        "cikir": 1,
        "kemá": 2,
    },
    # Language Yakumo concept straight
    # 1: 'ittusne; 'o'ihtusno
    # 2: 'o'upéka; 'o'úpeka; 'ówpeka; 'o'ópeka; 'ówpeka; 'ówpeka; 'o'úpeka; 'owpeka; 'o'upeka; 'o'úpeka
    {
        "'íkne": 1,
        "'o'upéka": 2,
    },
    # Language Yakumo concept to swell
    # 1: sekúkke; sekuhke; sekukke; sekuhke; sekuhke; sekuhke; sekuhke
    # 2:
    {
        "sekúkke": 1,
        "tókse": 2,
    },
    # Language Yakumo concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "ní": 2,
        "númnum": 1,
    },
    # Language Horobetsu concept what
    # 1: nép; nép; nep; nep; nep; nep; nep; nep
    # 2: hemánta; hínta; hemánta; hemata; hemata; hemata; hemata; hemata; hemata
    {
        "nép": 1,
        "hemánta": 2,
    },
    # Language Horobetsu concept woman
    # 1: menokó; menokó; menokó; menokó; menokó; menokó; menokó; menokó; menéko
    # 2: mahnekuh; maynepo; mahtekuh; mahneku; mahtekuh; mahnekuh
    {
        "menokó": 1,
        "mát": 2,
    },
    # Language Horobetsu concept other
    # 1: 'oyá; 'oyá; 'oya; 'oya; 'oya; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá
    # 2: mósma; mósma
    {
        "mósma": 2,
        "'oyá": 1,
    },
    # Language Horobetsu concept leg
    # 1: cikír; cikír; cikír; cikír; cikír; cikír; cikír
    # 2: kemá; kemá; kemá; kemákuciki; kema; kema; kema; kema; kema; kema
    {
        "cikír": 1,
        "kemá": 2,
    },
    # Language Horobetsu concept fruit
    # 1: níyepuy; ní'epuy; 'epuyke; níyepuy; níyepuy
    # 2: níka'op; níka'op; níka'op; níka'op
    {
        "níka'op": 2,
        "'epúyke": 1,
    },
    # Language Horobetsu concept if
    # 1: nisap/ko; /ko
    # 2: /yakun; /yakun; /yakun
    {
        "'iká/ko": 1,
        "yakun": 2,
    },
    # Language Horobetsu concept to pierce (to stab)
    # 1: 'ótke; 'ótke; 'ótke; 'ótke; 'okke; 'ótke
    # 2: cíw; cíw; cuy; cíw; cíw; cíw; cíw; cíw; 'eciwkara; ciw
    {
        "'ótke": 1,
        "cíw": 2,
    },
    # Language Horobetsu concept to sew
    # 1: ninú; nínninu
    # 2: 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukawka; 'ukawka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka
    {
        "nínninu": 1,
        "'ukáwkaw": 2,
    },
    # Language Horobetsu concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "ní": 2,
        "núnnun": 1,
    },
    # Language Horobetsu concept dust
    # 1: maná; maná; paná; paná; paná; paná; toypana; pana; paná
    # 2: sirima; sirima
    {
        "maná": 1,
        "sírma": 2,
    },
    # Language Hiratori concept yellow
    # 1: síwnin; síwnin; síwnin; síwnin; síwnin; siwniɴ; siwnin; siwnin; siwnin; siwnin; siwnin
    # 3:
    {
        "síwnin": 1,
        "húre": 3,
    },
    # Language Hiratori concept other
    # 1: 'oyá; 'oyá; 'oya; 'oya; 'oya; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá
    # 2: mósma; mósma
    {
        "mósma": 2,
        "'oyá": 1,
    },
    # Language Hiratori concept fruit
    # 1: níyepuy; ní'epuy; 'epuyke; níyepuy; níyepuy
    # 2: níka'op; níka'op; níka'op; níka'op
    {
        "níka'op": 2,
        "múnepuy": 1,
    },
    # Language Hiratori concept father
    # 2: míci; míci; míci; míci; míci; míci
    # 3:
    {
        "míci": 2,
        "'iyápo": 3,
    },
    # Language Hiratori concept to pull
    # 1: 'etayé; 'etayé; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye
    # 2: 'ehékem; 'ehekeɴ; 'ehekem; 'ehekem; 'ehekem; 'ehekem; 'ehekem
    {
        "'etáye": 1,
        "'ehekem": 2,
    },
    # Language Hiratori concept to pierce (to stab)
    # 1: 'ótke; 'ótke; 'ótke; 'ótke; 'okke; 'ótke
    # 2: cíw; cíw; cuy; cíw; cíw; cíw; cíw; cíw; 'eciwkara; ciw
    {
        "'ótke": 1,
        "cíw": 2,
    },
    # Language Hiratori concept to smell
    # 1: húra nú; húra nú; húra nú; hura nu; húra nú; húra nú; húra nú; húra nú; húra nú; huránu
    # 3: húrarakkar; húrarakkar
    {
        "húrarapkar": 3,
        "húra nú": 1,
    },
    # Language Hiratori concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "ní": 2,
        "núnnun": 1,
    },
    # Language Samani concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "ni": 2,
        "nunnuɴ": 1,
    },
    # Language Obihiro concept cloud
    # 2: nis; nis
    # 3: 'uurara; 'uurara
    {
        "nís": 2,
        "'úrar": 3,
    },
    # Language Obihiro concept yellow
    # 1: síwnin; síwnin; síwnin; síwnin; síwnin; siwniɴ; siwnin; siwnin; siwnin; siwnin; siwnin
    # 3:
    {
        "síwnin": 1,
        "húre": 3,
    },
    # Language Obihiro concept other
    # 1: 'oyá; 'oyá; 'oya; 'oya; 'oya; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá
    # 2: mósma; mósma
    {
        "'oya": 1,
        "mósma": 2,
    },
    # Language Obihiro concept to sew
    # 1: ninú; nínninu
    # 2: 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukawka; 'ukawka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka
    {
        "ninú": 1,
        "'ukáwka": 2,
    },
    # Language Obihiro concept to swell
    # 1: sekúkke; sekuhke; sekukke; sekuhke; sekuhke; sekuhke; sekuhke
    # 3: sipísese; sipíse; sipísese; pisé; piséne
    {
        "pisé": 3,
        "sekúkke": 1,
    },
    # Language Obihiro concept to think
    # 2: sanniyo
    # 3: 'eyáyko'uwepeker; yáykopepeker
    {
        "yáykopepeker": 3,
        "yaykosanniyo": 2,
    },
    # Language Obihiro concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "nún": 1,
        "nínnun": 2,
    },
    # Language Obihiro concept dust
    # 1: maná; maná; paná; paná; paná; paná; toypana; pana; paná
    # 3:
    {
        "kopónci": 3,
        "paná": 1,
    },
    # Language Kushiro concept cloud
    # 1: nískur; kúr; nískur; nískur; nískur; nískur; nís; niskuru; niskuru; niskuru; niskuru
    # 3: 'uurara; 'uurara
    {
        "'urar": 3,
        "niskur": 1,
    },
    # Language Kushiro concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "num": 1,
        "ni": 2,
    },
    # Language Bihoro concept foot
    # 1: 'uré; pará'ure; 'uré; 'uré; paráwre; 'uré; paráwre; para'uri; parure
    # 2: cikír; cikír; cikir; cikir
    {
        "parawre": 1,
        "cikir": 2,
    },
    # Language Bihoro concept yellow
    # 1: síwnin; síwnin; síwnin; síwnin; síwnin; siwniɴ; siwnin; siwnin; siwnin; siwnin; siwnin
    # 3:
    {
        "suynin": 1,
        "hure": 3,
    },
    # Language Bihoro concept snake
    # 5: tannekamuy; tánnekamuy; tánnekamuy
    # 6:
    {
        "tánnekamuy": 5,
        "kokkopipi": 6,
    },
    # Language Bihoro concept flower
    # 3: 'apappo; hapáppo
    # 4: 'epúy; 'epúy; 'epuy; 'ekipuy; 'epuy; 'ekipuy; 'epuy; munepuy
    {
        "'epuyke": 4,
        "'apappo": 3,
    },
    # Language Bihoro concept to swell
    # 1: sekúkke; sekuhke; sekukke; sekuhke; sekuhke; sekuhke; sekuhke
    # 3: sipísese; sipíse; sipísese; pisé; piséne
    {
        "sekutke": 1,
        "pise": 3,
    },
    # Language Bihoro concept to think
    # 1: yáykosiramsuye; yáykosiramsuye; yáykosiramse; yáykosiramsuye; yáykosiramsuye; yáykosiramsuye
    # 2: sanniyo
    {
        "yaykosanniyo": 2,
        "yaykosiramsuye": 1,
    },
    # Language Bihoro concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "ni": 2,
        "nunnum": 1,
    },
    # Language Asahikawa concept woman
    # 1: menokó; menokó; menokó; menokó; menokó; menokó; menokó; menokó; menéko
    # 2: mahnekuh; maynepo; mahtekuh; mahneku; mahtekuh; mahnekuh
    {
        "menokó": 1,
        "matáynu": 2,
    },
    # Language Asahikawa concept foot
    # 1: 'uré; pará'ure; 'uré; 'uré; paráwre; 'uré; paráwre; para'uri; parure
    # 2: cikír; cikír; cikir; cikir
    {
        "pará'ure": 1,
        "cikir": 2,
    },
    # Language Asahikawa concept to fly
    # 1: hopuní; hopuní; hopúni; hopúni; hopúni; hopúni; 'opúni; hopúni
    # 3: 'oyúpu; 'oyúpu; 'oyúpu
    {
        "'opúni": 1,
        "'oyúpu": 3,
    },
    # Language Asahikawa concept cloud
    # 1: nískur; kúr; nískur; nískur; nískur; nískur; nís; niskuru; niskuru; niskuru; niskuru
    # 3: 'uurara; 'uurara
    {
        "nís": 1,
        "nískur": 1,
        "'úrar": 3,
    },
    # Language Asahikawa concept other
    # 1: 'oyá; 'oyá; 'oya; 'oya; 'oya; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá
    # 2: mósma; mósma
    {
        "'oyá": 1,
        "mósma": 2,
    },
    # Language Asahikawa concept if
    # 2: /yakun; /yakun; /yakun
    # 3: /cik; /cikanak; /ciki; /ciki; 'iká/ciki; /ciki; /ciki; /ciki
    {
        "/ciki": 3,
        "yak": 2,
    },
    # Language Asahikawa concept to think
    # 3: 'eyáyko'uwepeker; yáykopepeker
    # 4: yaynu
    {
        "yáykopeker": 3,
        "yáynu": 4,
    },
    # Language Nayoro concept woman
    # 1: menokó; menokó; menokó; menokó; menokó; menokó; menokó; menokó; menéko
    # 2: mahnekuh; maynepo; mahtekuh; mahneku; mahtekuh; mahnekuh
    {
        "menokó": 1,
        "mát": 2,
    },
    # Language Nayoro concept tongue
    # 1: parúnpe; párunpe; parúnpe; parúnpe; parúnpe; parúnpe; parúnpe; parúnpe; parúnpe; parúnpe; parúnpe
    # 2: 'áw; 'áw; 'áw; 'áw; 'áw; 'áw; 'áw
    {
        "'áw": 2,
        "parúnpe": 1,
    },
    # Language Nayoro concept here
    # 1: téta; téta; téta; téta; téta; téta; téta; teeta; teeta; teeta; teeta; teeta; teyta
    # 2: ta'anta; ta'ánta; tanta
    {
        "téta": 1,
        "tánta": 2,
    },
    # Language Nayoro concept other
    # 1: 'oyá; 'oyá; 'oya; 'oya; 'oya; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá; 'oyá
    # 2: mósma; mósma
    {
        "'oyá": 1,
        "mósma": 2,
    },
    # Language Nayoro concept day
    # 1: tókap; tókap; tókap; tókap; tókap; tókap; to; tókam; tóno; toonoske; toono; toono; toono; toono; toono
    # 2: sírpeker; sírpeker; sírpeker
    {
        "tókam": 1,
        "sírpeker": 2,
    },
    # Language Nayoro concept lip
    # 2: pápus; capus; cápus; cápus; cápus; capús; cápus; caapus; caapus; caapus; caapus; caapus; caapus
    # 3: pátoy; pátoy; pátoy
    {
        "pápus": 2,
        "cápus": 2,
        "pátoy": 3,
    },
    # Language Nayoro concept ice
    # 1: kónru; kónru; kónru; kónru; kónru; kónru; kónru; kónru; kónru; kónru; kónru
    # 2: rúp; ruh; rup; ruh; ruh; ruh; tup
    {
        "rúp": 2,
        "kónru": 1,
    },
    # Language Nayoro concept to pull
    # 1: 'etayé; 'etayé; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye; 'etáye
    # 2: 'ehékem; 'ehekeɴ; 'ehekem; 'ehekem; 'ehekem; 'ehekem; 'ehekem
    {
        "'etáye": 1,
        "'ehékem": 2,
    },
    # Language Nayoro concept to throw
    # 2: 'osúra
    # 3: e'ah
    {
        "'osúra": 2,
        "'e'ák": 3,
    },
    # Language Nayoro concept to pierce (to stab)
    # 1: 'ótke; 'ótke; 'ótke; 'ótke; 'okke; 'ótke
    # 2: cíw; cíw; cuy; cíw; cíw; cíw; cíw; cíw; 'eciwkara; ciw
    {
        "'ótke": 1,
        "cíw": 2,
    },
    # Language Nayoro concept to sew
    # 1: ninú; nínninu
    # 2: 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukawka; 'ukawka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka; 'ukáwka
    {
        "'ukáwka": 2,
        "ninú": 1,
    },
    # Language Nayoro concept dust
    # 1: maná; maná; paná; paná; paná; paná; toypana; pana; paná
    # 3:
    {
        "paná": 1,
        "kopónci": 3,
    },
    # Language Sôya concept what
    # 1: nép; nép; nep; nep; nep; nep; nep; nep
    # 2: hemánta; hínta; hemánta; hemata; hemata; hemata; hemata; hemata; hemata
    {
        "hemáta": 2,
        "nép": 1,
    },
    # Language Sôya concept root
    # 1: sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit
    # 2: ciɴkew; niicinkew; cinkew
    {
        "sinrit": 1,
        "cínkew": 2,
    },
    # Language Sôya concept cloud
    # 1: nískur; kúr; nískur; nískur; nískur; nískur; nís; niskuru; niskuru; niskuru; niskuru
    # 3: 'uurara; 'uurara
    {
        "'úrar": 3,
        "nískur": 1,
    },
    # Language Sôya concept smoke
    # 1: sipuyá; sipuyá; supúya; supúya; supúya; supúya; supúya; supúya; supúya; supúya; supúya
    # 2: pá; paa; paa; paa; paa; paa; paa
    {
        "pá": 2,
        "sipúya": 1,
    },
    # Language Sôya concept fire
    # 1: 'apé; 'apé; 'apé; 'apé; 'apé; 'apé; 'apé; 'apé; 'apé; 'apé; 'apé; 'apé
    # 2: 'uɴci; 'unci; 'unci; 'unci; 'unci; 'unci
    {
        "'apé": 1,
        "'únci": 2,
    },
    # Language Sôya concept to push
    # 1: 'oputúye; 'oputúye; 'opútuye; 'opútuye; 'opútuye; 'opútuye; 'opucuye; 'opútuye; 'opútuye; 'opútuye; 'opútuye; 'opítuye; 'okacituypa; 'okacituypa; 'okaapituye
    # 2: 'e'aciw; 'e'aciw
    {
        "'opítuye": 1,
        "'e'áciw": 2,
    },
    # Language Sôya concept to throw
    # 2: 'osúra
    # 3: e'ah
    {
        "'osúra": 2,
        "'eyák": 3,
    },
    # Language Sôya concept to swell
    # 1: sekúkke; sekuhke; sekukke; sekuhke; sekuhke; sekuhke; sekuhke
    # 3: sipísese; sipíse; sipísese; pisé; piséne
    {
        "sekútke": 1,
        "pisé": 3,
    },
    # Language Sôya concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "ni": 2,
        "nunnun": 1,
    },
    # Language Ochiho concept louse
    # 1: 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'uriki
    # 2: rasi; rasi; tasi
    {
        "rasi": 2,
        "'uriki": 1,
    },
    # Language Ochiho concept straight
    # 3: ku'anno; 'e'iku'anno
    # 4: 'ikuruhne
    {
        "ku'aɴno": 3,
        "'ukuruhne": 4,
    },
    # Language Tarantomari concept all
    # 2: 'emuyke; 'imiki; 'emuyke; 'emuyke
    # 3:
    {
        "'anpahno": 3,
        "'imiki": 2,
    },
    # Language Tarantomari concept many
    # 1: porónno; poro'ónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; poroono; poroono
    # 2:
    # 3:
    {
        "'okayno": 3,
        "renkayne": 2,
        "poronno": 1,
    },
    # Language Tarantomari concept root
    # 1: sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit
    # 2: ciɴkew; niicinkew; cinkew
    {
        "cinkew": 2,
        "niisinrit": 1,
    },
    # Language Tarantomari concept skin
    # 1: káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; kah; kah
    # 2: rus; rus
    {
        "rus": 2,
        "kap": 1,
    },
    # Language Tarantomari concept foot
    # 1: 'uré; pará'ure; 'uré; 'uré; paráwre; 'uré; paráwre; para'uri; parure
    # 3: kema
    {
        "paruure": 1,
        "kema": 3,
    },
    # Language Tarantomari concept breast
    # 1: pénram; pénram; pénram; pénram; pénram; pénram; pénram; pénram; pénram; pénram; raɴ(-m); ram; ram; ranka
    # 2: rerar; rerár; rerár; reraru
    {
        "ram": 1,
        "reraru": 2,
    },
    # Language Tarantomari concept to fear
    # 2: 'oháynek; 'ohayne; 'ohayhayne; 'e'ohayohayneh; 'e'ohayne
    # 3:
    {
        "'ohayne": 2,
        "'eyaytupare": 3,
    },
    # Language Maoka concept I
    # 2: cókay
    # 3: 'anokay; 'anoka(y)
    {
        "'anokay": 3,
        "co'okay": 2,
    },
    # Language Maoka concept many
    # 1: porónno; poro'ónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; poroono; poroono
    # 2:
    {
        "poronno": 1,
        "renkayne": 2,
    },
    # Language Maoka concept louse
    # 1: 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'úrki; 'uriki
    # 2: rasi; rasi; tasi
    {
        "'uriki": 1,
        "rasi": 2,
    },
    # Language Maoka concept root
    # 2: ciɴkew; niicinkew; cinkew
    # 3:
    {
        "cinkew": 2,
        "nii'oosikehe": 3,
    },
    # Language Maoka concept skin
    # 1: káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; kah; kah
    # 2: rus; rus
    {
        "rus": 2,
        "kah": 1,
    },
    # Language Maoka concept dry
    # 1: sít; sít; sít; sít; sít; sít; sít; sít; sít; sít; sít; sít; sáttek; sahteh; sahteh; sahteh; sattek
    # 2: riwa
    {
        "riwa": 2,
        "sahteh": 1,
    },
    # Language Maoka concept ye
    # 1: 'eciókay('utár); 'eci'okáy('utár); 'eci'oká; 'eci'oká; 'eci'okay; 'eci'utári; 'eci'okay; 'eci'okay; 'esí'utar; 'ecooka(y) 'uta(ri); 'eci'okay; 'eci'okayahcin; 'eco'okay ('utara)
    # 2: 'e'ani 'utár; 'e'áni 'utári; 'e'áni 'utár; 'e'áni 'utári; e'ani 'utara
    {
        "'ecookay 'utara": 1,
        "'e'ani 'utara": 2,
    },
    # Language Maoka concept straight
    # 1: 'ittusne; 'o'ihtusno
    # 3: ku'anno; 'e'iku'anno
    {
        "ku'anno": 3,
        "'istusne": 1,
    },
    # Language Maoka concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "nunnum": 1,
        "nii": 2,
    },
    # Language Maoka concept to fear
    # 2: 'oháynek; 'ohayne; 'ohayhayne; 'e'ohayohayneh; 'e'ohayne
    # 3:
    {
        "'ohayne": 2,
        "'eyaytupare": 3,
    },
    # Language Shiraura concept I
    # 1: ku'ani; ku'ani; káni; káni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni
    # 2: cókay
    {
        "ku'ani": 1,
        "co'okay": 2,
    },
    # Language Raichishka concept I
    # 1: ku'ani; ku'ani; káni; káni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni
    # 3: 'anokay; 'anoka(y)
    {
        "ku'ani": 1,
        "anoka": 3,
    },
    # Language Raichishka concept all
    # 2: 'emuyke; 'imiki; 'emuyke; 'emuyke
    # 4:
    {
        "'okore": 4,
        "'emuyke": 2,
    },
    # Language Raichishka concept many
    # 1: porónno; poro'ónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; poroono; poroono
    # 2:
    # 3:
    {
        "'okayno": 3,
        "renkayne": 2,
        "poronno": 1,
    },
    # Language Raichishka concept root
    # 1: sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit; sínrit
    # 2: ciɴkew; niicinkew; cinkew
    {
        "cinkew(large)": 2,
        "sinris(small)": 1,
    },
    # Language Raichishka concept foot
    # 1: 'uré; pará'ure; 'uré; 'uré; paráwre; 'uré; paráwre; para'uri; parure
    # 3: kema
    {
        "kema": 3,
        "('urekucis)para'ure": 1,
    },
    # Language Raichishka concept he
    # 2: tara 'aynu; tara 'aynu; tara 'aynu; tara 'aynu; tara 'aynu
    # 3:
    {
        "ta'an a'ynu": 3,
        "tara 'aynu": 2,
    },
    # Language Raichishka concept they
    # 2: tara 'aynu 'utara; tara; tara 'aynu 'utara; tara 'aynu 'utara; tara 'aynu('utara)
    # 3:
    {
        "ta'anoka 'aynu'utah": 3,
        "taranoka 'aynu'utah": 2,
    },
    # Language Raichishka concept there
    # 2: taraata; 'ukita; tarata; taraata; tarata
    # 3:
    {
        "ta'anteeta": 3,
        "taranteeta": 2,
    },
    # Language Raichishka concept to suck
    # 1: núnnun; nun; nunnun; sikonun; nunnun
    # 2: sikoní; ní
    {
        "sikonun": 1,
        "nunnun": 1,
        "nii": 2,
    },
    # Language Nairo concept I
    # 1: ku'ani; ku'ani; káni; káni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni; Ku'áni
    # 2: cókay
    # 3: 'anokay; 'anoka(y)
    {
        "'anokay": 3,
        "cookay": 2,
        "ku'ani": 1,
    },
    # Language Nairo concept many
    # 1: porónno; poro'ónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; porónno; poroono; poroono
    # 3:
    {
        "'okayno": 3,
        "poronno": 1,
    },
    # Language Nairo concept skin
    # 1: káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; káp; kah; kah
    # 2: rus; rus
    {
        "tus": 2,
        "kap": 1,
    },
    # Language Nairo concept foot
    # 1: 'uré; pará'ure; 'uré; 'uré; paráwre; 'uré; paráwre; para'uri; parure
    # 3: kema
    {
        "kema": 3,
        "para'uri": 1,
    },
}
