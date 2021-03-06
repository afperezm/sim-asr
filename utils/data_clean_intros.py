import argparse
import functools
import glob
import operator
import os
import pprint
import re
from shutil import copyfile


def compute_transcript_headings(transcript_files):
    pattern = re.compile(r"^(.*?)\s*?(\**-?\[?\w+(\s\(\w*\))?\]?\s?[12]?\**\s?):")
    pattern_transcript = re.compile(r"^(/.+/?)+(\d{3}-\w{2}-\d{5})\.txt$")
    clean_intros = {}
    clean_matches = {}
    dirty_intros = {}
    dirty_matches = {}
    for transcript_file in sorted(transcript_files):
        print("Processing... {0}".format(transcript_file))
        result = pattern_transcript.search(transcript_file)
        if result is not None and (result.group(2) == '198-VI-00025' or
                                   result.group(2) == '469-VI-00001' or
                                   result.group(2) == '126-VI-00031' or
                                   result.group(2) == '341-VI-00006'):
            # print("***{0}***".format(transcript_file))
            print("Cannot be used since audio and transcript don't correspond")
            continue
        elif result is not None and result.group(2) == '149-VI-00001':
            # print("***{0}***".format(transcript_file))
            print("Cannot be used since transcript is a pilot and not so accurate")
            continue
        elif result is not None and (result.group(2) == '802-VI-00001' or
                                     result.group(2) == '778-VI-00004' or
                                     result.group(2) == '422-VI-00001' or
                                     result.group(2) == '778-VI-00003'):
            # print("***{0}***".format(transcript_file))
            print("Skipping since transcript is not annotated with actor tags")
            continue
        with open(transcript_file) as f:
            contents = f.read()
            contents_replaced = re.sub("\n", " ", contents)
            # oTranscribe block (it happens at the beginning or the end)
            contents_replaced = re.sub(r"^\s*Enter your transcript here\.{3}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Quick tips:", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\\- _Ctrl\+I_ adds _italic_ formatting and "
                                       r"\*\*Ctrl\+B\*\* adds \*\*bold\*\* formatting\.",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\\- Press ESC to play/pause, "
                                       r"and Ctrl\+J to insert the current timestamp\.",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Top block
            contents_replaced = re.sub(r"^\s*"
                                       r"("
                                       r"\**\[?"
                                       r"(\d{3}-\w{2}-\d{3,5}\s\d{3}-\w{2}-\d{3,5}_\s\(\d{5}\)\s_)?"
                                       r"(\d{3}-\w{2}-\d{5}_\s?\(\d{4,5}\)\s?_)?"
                                       r"(\d{3}-\w{2}-\d{5}\s{2}\*{2})?"
                                       r"Audio(\s?de\sla\s?entrevista)?:?\s?"
                                       r"(\s\(#\d{3,4}\)\s)?"
                                       r"(\d{3}[\s\-_]\w{2}[\-_]\d{3,6})?"
                                       r"([\-_]\(?\d{5}\)?)?"
                                       r"((-|_|\s)?\(\d{3,5}\)(([\s_]\w+)+)?(\.wav)?(\s\(cifrado\))?)?"
                                       r"(_?\(\w+\s\w+\.wav\))?"
                                       r"(_\(\*{2}\s\*{2}\d{5}\s\))?"
                                       r"(\.(wav)?(mp3)?\s\(cifrado\))?"
                                       r":?\]?\.?[\s*]*"
                                       r"){1,2}"
                                       r"\s{1,2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*"
                                       r"https://sim3?\.comisiondelaverdad\.co/expedientes/public/transmitir/\d{5}"
                                       r"\**\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Top block
            contents_replaced = re.sub(r"^\s*\**(Transcripci??n)?\s?entrevista(n??mero)?:?"
                                       r"(\s?\(#\d{3,4}\))?\s?\d{3}\s?-\s?\w{2}\s?-\s?\d{3,6}\s*\**\s*\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Top block
            contents_replaced = re.sub(r"^\s*"
                                       r"("
                                       r"(\*{4}\s{2})?"
                                       r"\**"
                                       r"("
                                       r"((\d{2})?\.?\(#\s?\d{4}\)\s?)|"
                                       r"(Entrevista\s(audio)?\s?)|"
                                       r"(ENT\s)|"
                                       r"(\s([/\-|])?\s?)|"
                                       r"(\d{2}\s{4})|"
                                       r"(O?\d{2,3}\s?\d?\s?[ -???]\s?\w{2}\s?[ -???]\s?\d{3,6}\/?)|"
                                       r"(\d{3}-\d{5})|"
                                       r"(\d{1,2}:\d{2}\s[apAP][mM])|"
                                       r"(\d{1,2}[-/]\d{2}[-/]\d{4})|"
                                       r"(_?\s?\(?\s?\d{4,5}\s?\)?)|"
                                       r"(\s?\\?-(TF-)?\s?\d{3})"
                                       r")+"
                                       r"(\s+\*{2}\s+\*{2})*"
                                       r"(\s|\*|_)*\.?\s{2}"
                                       r"){1,2}",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Ficha\s?(Corta)?\]?:?([^\]]+)\]",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**\s*\[(Lectura\sde)?\s*consent?it?miento(\sinformado)?([^\]]+)\]\.?\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Transcripci??n:((\s\w+)+|(\s\d+))\.?\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Inicio\sde\sentrevista:\s(\d{1,2}???{1,2}:?)+\s{2}", "  ", contents_replaced)
            # The following expression repeats twice on interview 393-VI-00021 the full content repeats twice
            contents_replaced = re.sub(r"^\s*\**Transcriptor:\s\d{3}(\s|\*)*\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**Tiempo:\s(\d{2}:?)+\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # First block (metadata)
            contents_replaced = re.sub(r"^\s*\**C??digo\s?de\s?la\s?entrevista:?\**\s+\d{2,3}\**\s*-\w{2}-\d{3,5}\s?\**"
                                       r"(_?\(\d{3,4}\)?)?"
                                       r"(___5d273a5e31c62)?",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**C??digo\s?(de)?\s?(del)?\s?entrevistador:?\**\s*(\d{2,3})?\s?\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Nombre(s)?\stranscriptor(a|es)?:?\s?(\s\w+)+\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Custom replacements for expressions that could not be captured otherwise without messing things up
            contents_replaced = re.sub(r"^\s*Nombre\stranscriptora:\s{3}"
                                       r"Juliana\sRobles\s\(00:00-0:30:24\)\s{2}"
                                       r"Esteban\sZapata\s\(0:30:24 -0:47:00\)\s{2}"
                                       r"Ivonne\sEspitia\s\(0:47:00 ??? 1:04:00\)\s{2}"
                                       r"Isabel\sGil\s\(1:04:00 -2:00:00\)\s{2}"
                                       r"Juliana\sMateus\s\(2:00:00-2:40:00\)",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*C??digo\stranscriptora:\s{3}03\s{2}06\s{2}04\s{2}05\s{2}02",
                                       "  ", contents_replaced)
            # End of custom replacements
            contents_replaced = re.sub(r"^\s*\**C??digo\s?(de)?\s?(del)?\s?transcriptor(a|es)?:?\**"
                                       r"\s+\d{0,3}\s?\**\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**Fecha\s?final\s?de\s?(la)?\s?transcripci??n:?\**\s*"
                                       r"((\d{1,2})?\s*\**((\s*de\s*)|/|-)(\w+|\d{2})((\s*de\s*)|/|-|\s)?(\d{2,4})?)?"
                                       r"(\s\**)?",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**"
                                       r"Duraci??n\s?(total)?\s?(del)?\s?(de)?\s?(la)?\s?(audio|entrevista)s?:?\s?"
                                       r"\**"
                                       r"(\s*(((\d{1,2}???{0,2}????)|(\**)):?)+\s*((min\.)|(minutos))?)+"
                                       r"\s*\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Top block
            contents_replaced = re.sub(r"^\s*Transcripci??n\sentrevista:(\s\w+)+\.?\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Second block (header)
            contents_replaced = re.sub(r"^\s*Aclaraci??n\sde\setiquetas\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Aclaraciones\ssobre\sla\sentrevista([^\]]+)\]", "  ", contents_replaced)
            # Second block (actor tags)
            contents_replaced = re.sub(r"^\s*\**Etiquetas(\sTranscripci??n)?(\sUsadas)?\**\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**Hablantes\**\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistadora:\sENT", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sTEST", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Testimoniante:\sTEST", "  ", contents_replaced)
            contents_replaced = re.sub(r"^(\s*Interlocutora?\sdesconocid[oa]:\sX[12])+", "  ", contents_replaced)
            contents_replaced = re.sub(r"^(\s*Entrevistador(a)?\s\(ENT[12]?\):?\s?(\s\w+)*\s{2})+", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Testimoniante\s\(TEST\):\s?(\s\w+)*\.?\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Informante\s\(Inf1\):\s?(\s\w+)*\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Inf2:\s?(\s\w+)*\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Informante:?\s{1,2}\(?Inf\)?:?\s?(\s\w+\.?)*\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*X:\s?(\s\w+)*\s{2}", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*X1:\s?(\s\w+)*\s{2}", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*X2:\s?(\s\w+)*\s{2}", "  ", contents_replaced, flags=re.IGNORECASE)
            # Third block (transcription tags)
            contents_replaced = re.sub(r"^\s*\**\s*(Etiquetas\s)?Transcripci??n\**\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Interrupci??n:\s\[INTERRUP\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Continuaci??n:\s\[CONT\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Inaudible:\s\[INAD\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Dudoso:\s\[DUD\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[TRA\]:\stransliteraci??n", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[DUD\]:\stranscripci??n\sdudosa", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INAD\]:\sinaudible", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Interrup\]:\sinterrupci??n", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Cont\]:\sContinuaci??n", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Corte\s\(de\sla\sgrabaci??n\):\s\[CORTE\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Pausa\s\(en\sel\shilo\sde\sla\sentrevista\):\s\[PAUSA\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Informaci??n\sincluida:\s[\[{]INC[\]\}]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Transliteraci??n:\s\[TRA\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Lenguaje\sno\sverbal\s\(risa\so\sllanto\):\s\[LNV\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA:\s?(\d{1,2}:?\s?)*\s?-\s?(\d{1,2}:?)*\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[CORTE:?\s?(\d{1,2}:?)*\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*{3}\s{2}", "  ", contents_replaced)
            # Custom first block
            contents_replaced = re.sub(r"^\s+Entrevistas", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Investigaci??n\spara\sel\sesclarecimiento\sde\sla\sverdad\s"
                                       r"en\sla\sfrontera\sColombia\sy\sVenezuela",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Datos\sde\sla\sentrevista", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sMaria\sRubiela\sGuti??rrez\s{1}"
                                       r"\s{2}Miembro\sdel\spartido\sde\sla\sUni??n\sPatri??tica,\s"
                                       r"residenciado\sen\sla\sciudad\sde\sC??cuta",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sTania\sAgudelo\s{1}"
                                       r"\s{2}Miembro\sdel\spartido\sde\sla\sUni??n\sPatri??tica,\s"
                                       r"residenciado\sen\sla\sciudad\sde\sC??cuta",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sWilmer\sRangel\s{1}"
                                       r"\s{2}Presidente\sde\sJunta\sdel\sBarrio\sHugo\sChaves,\sSaravena,\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sAdriana\sConstanza\sCorona\s{1}"
                                       r"\s{1}V??ctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sChiquito,\s"
                                       r"municipio\sde\sTib??",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sSoley\sRueda\s"
                                       r"\sV??ctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sLargo,\s"
                                       r"municipio\sde\sTib??",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sObdulio\sCastro\s"
                                       r"\sV??ctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sLargo,\s"
                                       r"municipio\sde\sTib??",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sRodrigo\sEsmigle\sGuti??rrez\sFranco\s"
                                       r"\sDel\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\s"
                                       r"departamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sMarlene\sP??rez\s"
                                       r"\s{2}Del\sasentamiento\sHugo\sChaves,\smunicipio\sde\sSaravena,\s"
                                       r"departamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sDoly\sGranados\s"
                                       r"\s{2}Del\sasentamiento\sHugo\sChaves,\smunicipio\sde\sSaravena,\s"
                                       r"departamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sGuillermo\sMorales\sNoriega\s"
                                       r"\s{2}Del\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\s"
                                       r"departamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sMarta\sEsperanza\sRodr??guez\s"
                                       r"\sDel\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\s"
                                       r"departamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistador:\sMar??a\sAngelica\sGonz??lez,\s"
                                       r"investigadora\spara\scasos\sde\sexilio,\s+"
                                       r"desplazamiento y\s+"
                                       r"despojo en la frontera",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistador:\sTania\sAgudelo,\smiembro\sde\sla\sUP\sy\sMar??a\sAngelica\s"
                                       r"Gonz??lez,\sinvestigadora\spara\s+"
                                       r"casos\sde\sexilio,\sdesplazamiento\sy\sdespojo\sen\sla\sfrontera",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Lugar\sy\sFecha:\s\w+,\s\d{2}\sde\s\w+\sdel\s\d{4}",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Fecha:\sjunio\s18\sdel\s2019", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Lugar:\sLabranzagrande", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Fecha\sde\snacimiento\s3\sde\sfebrero\sde\s1988", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Desarrollo\sde\sla\sentrevista", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[FICHA\s00:01:57-00:11:17\]", "  ", contents_replaced)
            #
            contents_replaced = re.sub(r"^\s*\[CONT\]\s{2}Continuaci??n", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[CORTE\]\s{2}Corte\s\(de\sla\sgrabaci??n\)", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[DUD\]:?\s+Dudoso", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*ENT\s{2}Entrevistador", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INAD\]\s{2}Inaudible", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\[INC\]\s{2}Informaci??n\sincluida", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INTERRUP\]\s{2}Interrupci??n", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA\]\s{2}Pausa\s\(en\sel\shilo\sde\sla\sentrevista\):",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*TEST\s{2}Testimoniante", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*X\s{2}Interlocutor\sdesconocido", "  ", contents_replaced)
            # Top block
            contents_replaced = re.sub(r"^\s*\**Lectura\sy\srepuesta\sdel\sconsentimiento\sinformado\s\(.*\)\**",
                                       "  ", contents_replaced)
            # Top block
            contents_replaced = re.sub(r"^\s*\**\s*_?"
                                       r"INICIO\s?(TRANSCRIPCI??N)?:?\s*"
                                       r"(((\d{2,4}-\d{2}-\d{2,4})|(\d{1,2}:\d{2}))(\s*[-???]*\s*))*"
                                       r"_?\**",
                                       "  ", contents_replaced)
            # Top blocks
            contents_replaced = re.sub(r"^\s*\[Datos\spersonales([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INAD([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA([^\]]+)\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\[SIL([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Datos:([^\]]+)\]\.?", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INC:([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^Explicaci??n\sdel\strabajo\srealizado\spor\sla\sComisi??n\sde\sla\sVerdad\s"
                                       r"y\selconsentimiento\sinformado\s([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\**\d{1,2}:\d{2}\s?(PM)?m?\**", "  ", contents_replaced)
            # Top block
            contents_replaced = re.sub(r"^\s*TEST\s1:\sMujer\.", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*TEST\s2:\sHombre\.", "  ", contents_replaced)
            # Top block
            contents_replaced = re.sub(r"^Ps\s1\s:\sentrevistadora\sPsicosocial\s1", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Ps\s2\s:\sEntrevistadora\sPsicososial\s2", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Rm\s:\sEntrevistadora\sNodo\s1", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Mv\s:\sEntrevistador\sNodo\s2", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Me\s:\sEntrevistada", "  ", contents_replaced)
            # Custom replacements for non-generalizable expressions
            contents_replaced = re.sub(r"^ENT\.", "ENT:", contents_replaced)
            contents_replaced = re.sub(r"^\[Informaci??n\spersonal\s-\sconsentimiento\sinformado\]([^\]]+)\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^19 6:00 pm 8:30 pm 25/11/2019 2:00 pm 4 pm 28-11-2019 2 pm - 6:30 pm",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*29/11/2019 3:00 ??? 5:30", "  ", contents_replaced)
            contents_replaced = re.sub(r"^216ENT:\sVIENT:\s00031", "  ", contents_replaced)
            contents_replaced = re.sub(r"^Entrevista:\sFanny\sNavarro\.", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\*\*Entrevistadora:\*\*\s98", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Lugar\sy\sfecha\sde\sentrevista:\*\*\s"
                                       r"El\sDorado,\sMeta\s-\s21\sde\sagosto\sde\s2019\.",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Lugar\sde\slos\sHechos\*\*\s:\sPuerto\sSiare,\sMapirip??n,\sMeta\.",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Entrevista:\*\*\s23", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Audio\s098-VI-00023-\(36584\)\*\*", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[Consentimiento\sInformado:\s00:50\s???\s5:30\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"\[Consentimiento\sInformado:\s00:39\s-\s8:36\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*[ _*]+\s{2}", "   ", contents_replaced)
            contents_replaced = re.sub(r"^Ingresa tu transcripci??n aqu??\.{3}", "   ", contents_replaced)
            contents_replaced = re.sub(r"^Mar??a\ses\sla\sTEST1", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Bol??var\ses\sel\sTEST2", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Nieta\ses\sel\sTEST3", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*TRANSCRIPCION\sDE\sENTREVISTA\sCODIGO\sTRANSCRIPCI??N\s423-VII-00424",
                                       "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTEVISTA\s220-VI-00047", "   ", contents_replaced)
            contents_replaced = re.sub(r"^Entrevista\s002", "   ", contents_replaced)
            contents_replaced = re.sub(r"^Entrevista\s6", "   ", contents_replaced)
            contents_replaced = re.sub(r"^Entrevista\s15", "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTREVISTA\s51", "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTREVISTA\s52\s{3}AUDIO\s191127_0067", "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTREVISTA\s53\s{3}AUDIO\s191206_0069", "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTREVISTA\s58\s{3}AUDIO", "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTREVISTA\s66???", "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTREVISTA\s{4}67", "   ", contents_replaced)
            contents_replaced = re.sub(r"^ENTREVISTA\s68", "   ", contents_replaced)
            contents_replaced = re.sub(r"^667", "   ", contents_replaced)
            contents_replaced = re.sub(r"^TEST\s\(JuanBautista\sCaicedo\)\s{2}X1\s\(Yolanda\sRegalado\)",
                                       "   ", contents_replaced)
            contents_replaced = re.sub(r"^Bogot??\s27\sde\senero\sde\s2020\s{2}"
                                       r"\*\*Entrevista\srealizada\sa\sla\sse??ora\sFlor\sAlba\sDonato\sBarrios\s"
                                       r"CC39\.548\.628\*\*\s{2}"
                                       r"Entrevista\sNo\.\s347-VI-00004",
                                       "   ", contents_replaced)
            contents_replaced = re.sub(r"^2277-VI-00008", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*AUDIO\s070-VI-00001\s\(280\)", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*ENTREVISTA-\s036-VI-00060", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\[17min\]", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Audio\s01", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Audio\s045-VI-00001\(460\)", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*VI-00007", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*AUDIO\s191206_0069", "   ", contents_replaced)
            contents_replaced = re.sub(r"^175-00025-18-11-2019-205min", "   ", contents_replaced)
            contents_replaced = re.sub(r"^070\s-\s00053", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\.\s{2}", "   ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[No\spermite\spublicar\ssu\snombre\sen\sel\sinforme\sfinal\]",
                                       "   ", contents_replaced)
            contents_replaced = re.sub(r"^Bogot??\s19\sde\snoviembre\sde\s2020\s\s"
                                       r"\*\*Entrevista\srealizada\sal\sSe??or\s"
                                       r"Jes??s\sAntonio\sC??rdoba\sCC\s19057927\*\*\s\s"
                                       r"Entrevista\sNo\.\s4419\s-347-VI-00002",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\[El\saudio\sempieza\scuando\sya\sestaba\shablando\sel\sentrevistado\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\[AUDIOARRANCA\sCORTADO\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Mauricia\.", "  ", contents_replaced)
            # Fixes for wrong transcriptions
            contents_replaced = re.sub(r"^\s*\[(ENT|TEST)\]", "[ENT]:", contents_replaced)
            contents_replaced = re.sub(r"^Yo\sa\sel\ses\sno\slo\stengo,\scon\susted",
                                       "[X]: Yo a el es que no lo tengo en el con usted.",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Hoy\s17\sde\sjulio", "ENT: Hoy 17 de julio", contents_replaced)
            contents_replaced = re.sub(r"^\s*TEST -", "TEST:", contents_replaced)
            contents_replaced = re.sub(r"^Primero\sque\stodo\sme\sda\ssu\snombre\scompleto:\s\[Datos:([^\]]+)\].",
                                       "ENT: Bueno primero que todo me da su nombre completo.  "
                                       "TEST: Esperanza Carlosama.  "
                                       "ENT: Claro.  "
                                       "TEST: Yo tengo es un solo nombre.  "
                                       "ENT: Esperanza Carlosama, ??no? ??En d??nde naci?? usted? ??Y en qu?? fecha?  "
                                       "TEST: Aqu?? en la vereda [INAUD], el 23 de Marzo del 63.  "
                                       "ENT: Bueno. ??Usted es casada?  "
                                       "TEST: No.  "
                                       "ENT: ??Soltera?  "
                                       "TEST: Soltera.  "
                                       "ENT: ??Sufre de alguna discapacidad?  "
                                       "TEST: Diab??tica.  "
                                       "ENT: ??Enfermedad? Bueno diab??tica, ??pero discapacidad como tal?  "
                                       "TEST: No, discapacidad no, pues tengo es una [INAUD].  "
                                       "ENT: ??Usted a qu?? se dedica? ??Cu??l es el oficio suyo?  "
                                       "TEST: Agricultura.  "
                                       "ENT: Ah, a la agricultura, bueno. Espec??ficamente vive aqu?? en la Sancina, "
                                       "pero barrio nada vereda o colinda, ??no?  "
                                       "TEST: No, aqu??.  "
                                       "ENT: ??Usted como se considera? ??Una persona como le dir??a yo? "
                                       "??Ind??gena, campesina?  "
                                       "TEST: Campesina pues como todos, aqu??.", contents_replaced)
            contents_replaced = re.sub(r"^Sara Consuelo Mora Luna "
                                       r"Certifico que conozco las cl??usulas de confidencialidad al tomar este "
                                       r"testimonio, en lo que "
                                       r"respecta a la informaci??n, al tratamiento de la informaci??n, la autorizaci??n "
                                       r"que tengo de la "
                                       r"Comisi??n de la Verdad para realizar esta labor, igual las sanciones a las que "
                                       r"me someto por el "
                                       r"incumplimiento de esta confidencialidad y tambi??n, en lo que se refiere "
                                       r"a garantizar al "
                                       r"entrevistado la protecci??n de sus datos personales. "
                                       r"Voy a tomar el testimonio a Manuela Duque ??lvarez, hoy 30 de julio en "
                                       r"Santiago de Chile, en el "
                                       r"FASIC. "
                                       r"Tema: Testimonio",
                                       "S: Sara Consuelo Mora Luna. "
                                       "S: Certifico que conozco las cl??usulas de confidencialidad al tomar este "
                                       "testimonio, en lo que "
                                       "respecta a la informaci??n, al tratamiento de la informaci??n, la autorizaci??n "
                                       "que tengo de la "
                                       "Comisi??n de la Verdad para realizar esta labor, igual las sanciones a las que "
                                       "me someto por el "
                                       "incumplimiento de este de esta confidencialidad y tambi??n en lo que se refiere "
                                       "a garantizar al "
                                       "entrevistado la protecci??n de sus datos personales. "
                                       "S: Voy a tomar el testimonio a Manuela Duque ??lvarez, hoy 30 de julio en "
                                       "Santiago de Chile, en el FASIC. "
                                       "El tema, testimonio.", contents_replaced)
            contents_replaced = re.sub(r"^ENTBuenos d??as, Do??a Ana Graciela\.",
                                       "ENT: Buenos d??as, Do??a Ana Graciela.",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Entonces en este momento nos encontramos con la se??ora Amparo",
                                       "ENT: Entonces en este momento nos encontramos con la se??ora Amparo",
                                       contents_replaced)
            contents_replaced = re.sub(r"^TEST\. Eso fue en el mandato de Laureano Gomez",
                                       "TEST: Eso fue en el mandato de Laureano Gomez",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*9 de noviembre de 2019 estamoscon",
                                       "ENT: 9 de noviembre de 2019 estamoscon",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Siendo las 11 y diez de la ma??ana",
                                       "ENT: Siendo las 11 y diez de la ma??ana",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*En este momento siendo las 10 y 55 de la ma??ana",
                                       "ENT: En este momento siendo las 10 y 55 de la ma??ana",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Buenos d??as, nos encontramos con el se??or Eustaquio C??rdenas D??az",
                                       "ENT: Buenos d??as, nos encontramos con el se??or Eustaquio C??rdenas Flores",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*ENT Bueno muchas gracias, primero que todo por acceder",
                                       "ENT: Bueno muchas gracias, primero que todo por acceder",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Listo, entonces buenas tardes hoy 12 de septiembre",
                                       "ENT: Listo, entonces buenas tardes hoy 12 de septiembre",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Municipio de San Vicente de Chucur??, con la se??ora Olga Diaz Rueda\.",
                                       "ENT: Entonces muy buenos d??as mi nombres Audrey Robayo Sanchez y me encuentro "
                                       "en el municipio de San Vicente de Chucur??, con la se??ora Hilda Diaz Rueda.",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Entonces, nos encontramos en Puerto Concordia Meta",
                                       "ENT: Listo.  "
                                       "TEST: Uhm ya.  "
                                       "ENT: Entonces, nos encontramos en Puerto Concordia Meta",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Para que quede en la grabaci??n hoy es",
                                       "TEST: [PAUSA: 00:00-00:35] Okay.  "
                                       "ENT: Vale, gracias. Entonces pues para que quede en la grabaci??n hoy es",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*\{ENT: Bueno estoy ac?? en Yond??",
                                       "ENT: Bueno estoy ac?? en Yond??",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*\{ENT: Bueno estoy ac?? en Yond??",
                                       "ENT: Bueno estoy ac?? en Yond??",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*\*{2}\sENT:\slisto,\sentonces,\strata\sde\shablar",
                                       "ENT: listo, entonces, trata de hablar",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Continuamos\s*ENT1:\sSe\scompr??\ssu\smotorcito",
                                       "ENT2: Continuamos.  "
                                       "TEST: Bueno as?? como les cuento.  "
                                       "ENT1: Se compr?? su motorcito.",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Mire\sah??\sest??\sgrabando,\svuelva\sy\.{3}",
                                       "X: Mire ah?? est?? grabando, vuelva y...",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Entrevista\sOsias\sQuejada\s{2}Realizada\sen\sSoacha\s"
                                       r"\(comuna\scuatro,\sAltos\sde\sCazuc??\)\s\s\s\s\s\s\s\sINT:",
                                       "INT: [INICIO: 00:00:11] ",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*\(Diligenciamiento\sde\sformatos\)\s{2}"
                                       r"No\sautoriza\scolocar\sel\snombre\spara\sel\sinforme\sfinal\s{8}"
                                       r"ENT:\slos\snombres\sno\sse\spublican\sen\sel\sinforme\sque\sva\sa\squedar\.",
                                       "ENT: [INICIO: 00:02:38] Los nombres no se publican en el informe",
                                       contents_replaced)
            contents_replaced = re.sub(r"Explicaci??n\sypresentaci??n\sde\slas\stareas\sde\sla\scomisi??n\sde\sla\s"
                                       r"verdad\sy\sel\sconsentimiento\sinformado\sy\sexplicaci??n\ssobre\spormenores\s"
                                       r"de\sla\sentrevista\sen\smodo\svirtual\s"
                                       r"\[Consentimiento\sinformado:\s00\.00:00\s-\s00:08:00\]\.\s{2}"
                                       r"ENT:\s",
                                       "ENT: [INICIO: 00:07:58] ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Carlos\sLlanos\sD??azgranados\s{2}ENT:\s",
                                       "ENT: [INICIO: 00:00:33] ", contents_replaced)
            contents_replaced = re.sub(r"^Si\sme\sdices\sy\ste\straigo\salgo,\ste\svoy\sa\sponer\sal\slado\sdel\stodo\s"
                                       r"lo\sque\snecesito\syo\.\s{4}TEST:\s",
                                       "TEST: [INICIO: 00:00:12] ", contents_replaced)
            contents_replaced = re.sub(r"^Pi??alito\sVista\sHermosa,\sMeta\s18\sde\sjunio\sdel\s2019,\sinicio\s"
                                       r"entrevista\s{10}ENT:\s",
                                       "ENT: Pi??alito Vista Hermosa, Meta 18 de junio del 2019, inicio entrevista. ",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Buenas\stardes\.\sHoy\sestamos\sa\s11\sde\sjulio\sde\s2019",
                                       "ENT: Buenas tardes. Hoy estamos a 11 de julio de 2019",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Buenas\stardes,\smi\snombre\ses\sAndr??s\sRodrigo\sBuitrago\sFranco,\s"
                                       r"pertenezco\sa\sLa Comisi??n de la Verdad",
                                       "ENT: Buenas tardes, mi nombre es Andr??s Rodrigo Buitrago Franco, "
                                       "pertenezco a La Comisi??n de la Verdad",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*Para\sefectos\sde\sregistro,\sse\sda\sinicio\sa\sla\sentrevista\sde\s"
                                       r"car??cter\sindividual",
                                       "ENT: Para efectos de registro, se da inicio a la entrevista de "
                                       "car??cter individual",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Bueno\sDo??a\sFidelia", "ENT: Bueno Do??a Fidelia", contents_replaced)
            contents_replaced = re.sub(r"^(\s*\[Lengua(ind??gena)?\sembera\skat??o([^\]]+)\]"
                                       r"(\sMartha\sCecilia\sDomic??\sDomic??)?)+"
                                       r"\s*Buenas\stardes\.{3}",
                                       "TEST: [INICIO: 00:00:09] Buenas tardes...", contents_replaced)
            contents_replaced = re.sub(r"^HABLADUR??AS\s*TEST:\s??Entonces\shice\sbien\so\shice\smal?",
                                       "TEST: [INICIO: 00:00:13] ??Cierto entonces hice bien o hice mal?",
                                       contents_replaced)
            contents_replaced = re.sub(r"^\s*RUIDO\sEXTERIOR\s{2}"
                                       r"TEST:\s\[INAD:\s00:00\s-\s00:10\]\slo\sconvierte\sen\senemigo",
                                       "TEST: [INICIO: 00:00:08] Cuando ya a uno el estado lo convierte en enemigo",
                                       contents_replaced)
            result = pattern.search(contents_replaced)
            if result is None:
                # print("***{0}***".format(transcript_file))
                print("No match")
            else:
                is_clean_match = contents_replaced == re.sub("\n", " ", contents)
                if is_clean_match:
                    if result.group(1) not in clean_intros.keys():
                        clean_intros[result.group(1)] = []
                    clean_intros[result.group(1)].append(transcript_file)
                    if result.group(2) not in clean_matches.keys():
                        clean_matches[result.group(2)] = []
                    clean_matches[result.group(2)].append(transcript_file)
                else:
                    if result.group(1) not in dirty_intros.keys():
                        dirty_intros[result.group(1)] = []
                    dirty_intros[result.group(1)].append(transcript_file)
                    if result.group(2) not in dirty_matches.keys():
                        dirty_matches[result.group(2)] = []
                    dirty_matches[result.group(2)].append(transcript_file)
        print("Done")
    return {'Clean matches': clean_matches,
            'Clean intros': clean_intros,
            'Dirty matches': dirty_matches,
            'Dirty intros': dirty_intros}


def copy_transcriptions(transcript_files, out_dir):
    """Copy transcriptions to the specified output directory."""
    for transcript_file in transcript_files:
        basename = os.path.basename(transcript_file)
        print("Copying... {0}".format(transcript_file))
        copyfile(transcript_file, "{0}/{1}".format(out_dir, basename))
        print("Done")


def main():
    parser = argparse.ArgumentParser(description="Regex-based transcripts intro cleaner")
    parser.add_argument("--in_dir", type=str, help="Input data directory, where copied data is located",
                        required=True)
    parser.add_argument("--out_dir", type=str, help="Output data directory, where to copy intro-clean transcripts",
                        required=True)

    args = parser.parse_args()

    transcript_files = glob.glob("{0}/*.txt".format(args.in_dir))
    # transcript_files = "ddd-ww-ddddd.txt".split(" ")
    # transcript_files = ["{0}/{1}".format(args.in_dir, transcript_file) for transcript_file in transcript_files]
    intros_and_matches = compute_transcript_headings(transcript_files)

    # Print count of intros and matches
    for res_key in intros_and_matches:
        dict_elem = intros_and_matches[res_key]
        dict_elem_count = functools.reduce((lambda count, dict_elem_value: count + len(dict_elem_value)),
                                           dict_elem.values(), 0)
        print("{0}: {1}".format(res_key, dict_elem_count))
        # print(res_key)
        # pprint.pprint(sorted({key: len(dict_elem[key]) for key in dict_elem}.items(), key=operator.itemgetter(1)))

    # Copy clean match transcriptions
    clean_transcriptions_nested = list(intros_and_matches["Clean matches"].values())
    clean_transcriptions_list = [item for sublist in clean_transcriptions_nested for item in sublist]
    copy_transcriptions(clean_transcriptions_list, args.out_dir)


if __name__ == '__main__':
    main()
