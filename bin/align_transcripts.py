import glob
import operator
import pprint
import re


def compute_transcript_headings(transcript_files):
    # pattern = re.compile(r"^.*?\s*?(\w*?):")
    pattern = re.compile(r"^.*?\s*?(\**-?\[?\w+(\s\(\w*\))?\]?\s?[12]?\**\s?):")
    matches = {}
    for transcript_file in transcript_files:
        with open("/home/andresf/data/asr-co/{0}".format(transcript_file)) as f:
            contents = f.read()
            contents_replaced = re.sub("\n", " ", contents)
            contents_replaced = re.sub(r"Enter your transcript here\.{3}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"Quick tips:", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\\- _Ctrl+I_ adds _italic_ formatting and "
                                       r"\*\*Ctrl+B\*\* adds \*\*bold\*\* formatting\.", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\\- Press ESC to play/pause, and Ctrl+J to insert the current timestamp\.", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"https://sim3?\.comisiondelaverdad\.co/expedientes/public/transmitir/\d{5}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**Audio:?\s?\d{3}-\w{2}-\d{3,5}((-|_|\s)?\(\d{5}\))?:?\**", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**Código\s?de\s?la\s?entrevista:?\**\s+\d{2,3}\**\s*-\w{2}-\d{3,5}\s?\**"
                                       r"(_\(\d{3}\))?"
                                       r"(___5d273a5e31c62)?",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**Código\s?(de)?\s?(del)?\s?entrevistador:?\**\s*(\d{2,3})?\s?\**", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s*Nombre(s)?\stranscriptor(a|es)?:?\s?(\s\w+)+\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s*\**Código\s?(de)?\s?(del)?\s?transcriptor(a|es)?:?\**\s+\d{0,3}\s?\**\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s*\**Fecha\s?final\s?de\s?(la)?\s?transcripción:?\**\s*"
                                       r"((\d{1,2})?\s*\**((\s*de\s*)|/|-)(\w+|\d{2})((\s*de\s*)|/|-|\s)?(\d{4})?)?"
                                       r"(\s\**)?", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s*\**Duración\s?(total)?\s?(del)?\s?(de)?\s?(la)?\s?(audio|entrevista)s?:?\s?"
                                       r"\**"
                                       r"(\s*(((\d{1,2}’{0,2}”?)|(\**)):?)+\s*((min\.)|(minutos))?)+"
                                       r"\s*\**", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**Transcriptor:\s\d{3}\**", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**Tiempo: (\d{2}:?)+\**", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**_?"
                                       r"INICIO\s?(TRANSCRIPCIÓN)?:?\s*"
                                       r"(((\d{2,4}-\d{2}-\d{2,4})|(\d{1,2}:\d{2}))(\s*[-–]*\s*))*"
                                       r"_?\**", "  ",
                                       contents_replaced)
            contents_replaced = re.sub(r"\**(Transcripción)?\s?entrevista(número)?:?"
                                       r"(\s?\(#\d{3,4}\))?\s\d{3}\s?-\s?\w{2}\s?-\s?\d{3,5}\**\s?\**", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"Transcripción\sentrevista:(\s\w+)+\.?\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**\[(Lectura\sde)?\s*consen(ti|it)miento(\sinformado)?([^\]]+)\]\**", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"Aclaración\sde\setiquetas\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"\s{2}\**Etiquetas(\sTranscripción)?(\sUsadas)?\**\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s{2}\**Hablantes\**\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistadora:\sENT", "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sTEST", "  ", contents_replaced)
            contents_replaced = re.sub(r"Testimoniante:\sTEST", "  ", contents_replaced)
            contents_replaced = re.sub(r"Interlocutora?\sdesconocid[oa]:\sX[12]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^(\s*Entrevistador(a)?\s\(ENT[12]?\):\s?(\s\w+)*\s{2})+", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Testimoniante\s\(TEST\):\s?(\s\w+)*\.?\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Informante\s\(Inf1\):\s?(\s\w+)*\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Inf2:\s?(\s\w+)*\s{2}", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"Informante:?\s{1,2}\(?Inf\)?:?\s?(\s\w+\.?)*\s{2}", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*X:\s?(\s\w+)*\s{2}", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*X1:\s?(\s\w+)*\s{2}", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*X2:\s?(\s\w+)*\s{2}", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s{2}\**Transcripción\**\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"Interrupción:\s\[INTERRUP\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\[Interrup\]:\sinterrupción", "  ", contents_replaced)
            contents_replaced = re.sub(r"Continuación:\s\[CONT\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\[Cont\]:\sContinuación", "  ", contents_replaced)
            contents_replaced = re.sub(r"Inaudible:\s\[INAD\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[INAD\]:\sinaudible", "  ", contents_replaced)
            contents_replaced = re.sub(r"Dudoso:\s\[DUD\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[TRA\]:\stransliteración", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[DUD\]:\stranscripción\sdudosa", "  ", contents_replaced)
            contents_replaced = re.sub(r"Corte\s\(de\sla\sgrabación\):\s\[CORTE\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"Pausa\s\(en\sel\shilo\sde\sla\sentrevista\):\s\[PAUSA\]", "  ",
                                       contents_replaced)
            contents_replaced = re.sub(r"Información\sincluida:\s[\[{]INC[\]\}]", "  ", contents_replaced)
            contents_replaced = re.sub(r"Transliteración:\s\[TRA\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"Lenguaje\sno\sverbal\s\(risa\so\sllanto\):\s\[LNV\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA:\s?(\d{1,2}:?\s?)*\s?-\s?(\d{1,2}:?)*\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[CORTE:?\s?(\d{1,2}:?)*\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[Aclaraciones\ssobre\sla\sentrevista([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s+Entrevistas", "  ", contents_replaced)
            contents_replaced = re.sub(r"Investigación\spara\sel\sesclarecimiento\sde\sla\sverdad\sen\sla\sfrontera\sColombia\sy\sVenezuela",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Datos\sde\sla\sentrevista", "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sMaria\sRubiela\sGutiérrez\s{1}"
                                       r"\s{2}Miembro\sdel\spartido\sde\sla\sUnión\sPatriótica,\sresidenciado\sen\sla\sciudad\sde\sCúcuta",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sTania\sAgudelo\s{1}"
                                       r"\s{2}Miembro\sdel\spartido\sde\sla\sUnión\sPatriótica,\sresidenciado\sen\sla\sciudad\sde\sCúcuta",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sWilmer\sRangel\s{1}"
                                       r"\s{2}Presidente\sde\sJunta\sdel\sBarrio\sHugo\sChaves,\sSaravena,\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sAdriana\sConstanza\sCorona\s{1}"
                                       r"\s{1}Víctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sChiquito,\smunicipio\sde\sTibú",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sSoley\sRueda\s{1}"
                                       r"\s{1}Víctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sLargo,\smunicipio\sde\sTibú",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sObdulio\sCastro\s{1}"
                                       r"\s{1}Víctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sLargo,\smunicipio\sde\sTibú",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sRodrigo\sEsmigle\sGutiérrez\sFranco\s{1}"
                                       r"\s{1}Del\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\sdepartamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sMarlene\sPérez\s{1}"
                                       r"\s{2}Del\sasentamiento\sHugo\sChaves,\smunicipio\sde\sSaravena,\sdepartamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sDoly\sGranados\s{1}"
                                       r"\s{2}Del\sasentamiento\sHugo\sChaves,\smunicipio\sde\sSaravena,\sdepartamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sGuillermo\sMorales\sNoriega\s{1}"
                                       r"\s{2}Del\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\sdepartamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistado:\sMarta\sEsperanza\sRodríguez\s{1}"
                                       r"\s{1}Del\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\sdepartamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistador:\sMaría\sAngelica\sGonzález,\s"
                                       r"investigadora\spara\scasos\sde\sexilio,\s+"
                                       r"desplazamiento y\s+"
                                       r"despojo en la frontera",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevistador:\sTania\sAgudelo,\smiembro\sde\sla\sUP\sy\sMaría\sAngelica\s"
                                       r"González,\sinvestigadora\spara\s+"
                                       r"casos\sde\sexilio,\sdesplazamiento\sy\sdespojo\sen\sla\sfrontera",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"Lugar\sy\sFecha:\s\w+,\s\d{2}\sde\s\w+\sdel\s\d{4}", "  ", contents_replaced)
            contents_replaced = re.sub(r"Fecha:\sjunio\s18\sdel\s2019", "  ", contents_replaced)
            contents_replaced = re.sub(r"Lugar:\sLabranzagrande", "  ", contents_replaced)
            contents_replaced = re.sub(r"Fecha\sde\snacimiento\s3\sde\sfebrero\sde\s1988", "  ", contents_replaced)
            contents_replaced = re.sub(r"Desarrollo\sde\sla\sentrevista", "  ", contents_replaced)
            contents_replaced = re.sub(r"Transcripción:((\s\w+)+|(\s\d+))\.?\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"Inicio\sde\sentrevista:\s(\d{1,2}’{1,2}:?)+\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[CONT\]\s{2}Continuación", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[CORTE\]\s{2}Corte\s\(de\sla\sgrabación\)", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[DUD\]:?\s+Dudoso", "  ", contents_replaced)
            contents_replaced = re.sub(r"ENT\s{2}Entrevistador", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[INAD\]\s{2}Inaudible", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\[INC\]\s{2}Información\sincluida", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[INTERRUP\]\s{2}Interrupción", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[PAUSA\]\s{2}Pausa\s\(en\sel\shilo\sde\sla\sentrevista\):", "  ", contents_replaced)
            contents_replaced = re.sub(r"TEST\s{2}Testimoniante", "  ", contents_replaced)
            contents_replaced = re.sub(r"X\s{2}Interlocutor\sdesconocido", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[Lengua(indígena)?\sembera\skatío([^\]]+)\]"
                                       r"(\sMartha\sCecilia\sDomicó\sDomicó)?",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"\**Lectura\sy\srepuesta\sdel\sconsentimiento\sinformado\s\(.*\)\**",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*"
                                       r"\**"
                                       r"("
                                       r"(\s([/\-|])?\s?)|"
                                       r"(\d{3}-\w{2}-\d{5})|"
                                       r"(\d{1,2}:\d{2}\s[apAP][mM])|"
                                       r"(\d{2}[-/]\d{2}[-/]\d{4})"
                                       r")+"
                                       r"\**",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Datos\spersonales([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INAD([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA([^\]]+)\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\[SIL([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Datos:([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INC:([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"Explicación\sdel\strabajo\srealizado\spor\sla\sComisión\sde\sla\sVerdad\s"
                                       r"y\selconsentimiento\sinformado\s([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\**\d{1,2}:\d{2}\s?(PM)?m?\**", "  ", contents_replaced)
            contents_replaced = re.sub(r"^ENT\.", "ENT:", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[(ENT|TEST)\]", "[ENT]:", contents_replaced)
            contents_replaced = re.sub(r"TEST\s1:\sMujer\.", "ENT:", contents_replaced)
            contents_replaced = re.sub(r"TEST\s2:\sHombre\.", "ENT:", contents_replaced)
            contents_replaced = re.sub(r"Ps\s1\s:\sentrevistadora\sPsicosocial\s1", "  ", contents_replaced)
            contents_replaced = re.sub(r"Ps\s2\s:\sEntrevistadora\sPsicososial\s2", "  ", contents_replaced)
            contents_replaced = re.sub(r"Rm\s:\sEntrevistadora\sNodo\s1", "  ", contents_replaced)
            contents_replaced = re.sub(r"Mv\s:\sEntrevistador\sNodo\s2", "  ", contents_replaced)
            contents_replaced = re.sub(r"Me\s:\sEntrevistada", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\[Información\spersonal\s-\sconsentimiento\sinformado\]([^\]]+)\]", "  ",
                                       contents_replaced)
            # [FICHA 00:01:57-00:11:17]
            # Custom replacements for wrong transcriptions
            contents_replaced = re.sub(r"Yo\sa\sel\ses\sno\slo\stengo,\scon\susted\s\[DUD:([^\]]+)\]\.",
                                       "X: Yo a el es que no lo tengo en el con usted.",
                                       contents_replaced)
            contents_replaced = re.sub(r"^Hoy\s17\sde\sjulio", "ENT: Hoy 17 de julio", contents_replaced)
            contents_replaced = re.sub(r"19 6:00 pm 8:30 pm 25/11/2019 2:00 pm 4 pm 28-11-2019 2 pm - 6:30 pm", "  ",
                                       contents_replaced)
            contents_replaced = re.sub(r"29/11/2019 3:00 – 5:30", "  ", contents_replaced)
            contents_replaced = re.sub(r"TEST -", "TEST:", contents_replaced)
            contents_replaced = re.sub(r"Primero\sque\stodo\sme\sda\ssu\snombre\scompleto:\s\[Datos:([^\]]+)\].",
                                       "ENT: Bueno primero que todo me da su nombre completo.\n"
                                       "TEST: Esperanza Carlosama.\nENT: Claro.\nTEST: Yo tengo es un solo nombre.\n"
                                       "ENT: Esperanza Carlosama, ¿no? ¿En dónde nació usted? ¿Y en qué fecha?\n"
                                       "TEST: Aquí en la vereda [INAUD], el 23 de Marzo del 63.\n"
                                       "ENT: Bueno. ¿Usted es casada?\nTEST: No.\nENT: ¿Soltera?\nTEST: Soltera.\n"
                                       "ENT: ¿Sufre de alguna discapacidad?\nTEST: Diabética.\n"
                                       "ENT: ¿Enfermedad? Bueno diabética, ¿pero discapacidad como tal?\n"
                                       "TEST: No, discapacidad no, pues tengo es una [INAUD].\n"
                                       "ENT: ¿Usted a qué se dedica? ¿Cuál es el oficio suyo?\n"
                                       "TEST: Agricultura.\n"
                                       "ENT: Ah, a la agricultura, bueno. Específicamente vive aquí en la Sancina, "
                                       "pero barrio nada vereda o colinda, ¿no?\n"
                                       "TEST: No, aquí."
                                       "\nENT: ¿Usted como se considera? ¿Una persona como le diría yo? "
                                       "¿Indígena, campesina?\n"
                                       "TEST: Campesina pues como todos, aquí.", contents_replaced)
            contents_replaced = re.sub(r"Tema:\sTestimonio", "ENT: El tema testimonio.", contents_replaced)
            contents_replaced = re.sub(r"216ENT:\sVIENT:\s00031", "  ", contents_replaced)
            contents_replaced = re.sub(r"Entrevista:\sFanny\sNavarro.", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\*\*Entrevistadora:\*\*\s98", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Lugar\sy\sfecha\sde\sentrevista:\*\*\s"
                                       r"El\sDorado,\sMeta\s-\s21\sde\sagosto\sde\s2019\.",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Lugar\sde\slos\sHechos\*\*\s:\sPuerto\sSiare,\sMapiripán,\sMeta\.",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Entrevista:\*\*\s23", "  ", contents_replaced)
            # Bottom expressions that gotta be run after removing interview code
            contents_replaced = re.sub(r"^\s*\[Ficha\s?(Corta)?\]?:?([^\]]+)\]", "  ",
                                       contents_replaced, flags=re.IGNORECASE)
            result = pattern.search(contents_replaced)
            if result is None\
                    or result.group(1) == 'Entrevistada'\
                    or result.group(1) == 'transcriptora'\
                    or result.group(1) == 'dije'\
                    or result.group(1) == 'dice'\
                    or result.group(1) == 'Dijo':
                print("***{0}***".format(transcript_file))
                print("No match")
            elif result is not None and (result.group(1) == 'testimonios' or result.group(1) == 'Actividad'):
                print("***{0}***".format(transcript_file))
                print("Cannot be used")
            else:
                if result.group(1) not in matches.keys():
                    matches[result.group(1)] = []
                matches[result.group(1)].append(transcript_file)
    return matches


def main():
    transcript_files = glob.glob('*.txt')
    transcript_files = ["043-VI-00025.txt"]
    matches = compute_transcript_headings(transcript_files)
    matches.keys()
    pprint.pprint(sorted({key: len(matches[key]) for key in matches}.items(), key=operator.itemgetter(1)))
    # print("Files to check manually: {0}".format(len(transcript_files) - len(matches['ENT'])))


if __name__ == '__main__':
    main()
