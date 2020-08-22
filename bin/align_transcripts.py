import glob
import operator
import pprint
import re


def compute_transcript_headings(transcript_files):
    pattern = re.compile(r"^.*?\s*?(\**-?\[?\w+(\s\(\w*\))?\]?\s?[12]?\**\s?):")
    matches = {}
    for transcript_file in transcript_files:
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
            contents_replaced = re.sub(r"^\**\[?"
                                       r"(\d{3}-\w{2}-\d{3,5}\s\d{3}-\w{2}-\d{3,5}_\s\(\d{5}\)\s_)?"
                                       r"Audio(\sde\sla\sentrevista)?:?\s?"
                                       r"(\s\(#\d{3,4}\)\s)?"
                                       r"(\d{3}-\w{2}-\d{3,5})?"
                                       r"((-|_|\s)?\(\d{3,5}\)(([\s_]\w+)+)?(\.wav)?)?"
                                       r":?\]?\.?\**\s{1,2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*"
                                       r"https://sim3?\.comisiondelaverdad\.co/expedientes/public/transmitir/\d{5}"
                                       r"\**\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # First block (metadata)
            contents_replaced = re.sub(r"\**Código\s?de\s?la\s?entrevista:?\**\s+\d{2,3}\**\s*-\w{2}-\d{3,5}\s?\**"
                                       r"(_\(\d{3}\))?"
                                       r"(___5d273a5e31c62)?",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\**Código\s?(de)?\s?(del)?\s?entrevistador:?\**\s*(\d{2,3})?\s?\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s*Nombre(s)?\stranscriptor(a|es)?:?\s?(\s\w+)+\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Custom replacements for expressions that could not be captured otherwise without messing things up
            contents_replaced = re.sub(r"\s*Nombre\stranscriptora:\s{3}"
                                       r"Juliana\sRobles\s\(00:00-0:30:24\)\s{2}"
                                       r"Esteban\sZapata\s\(0:30:24 -0:47:00\)\s{2}"
                                       r"Ivonne\sEspitia\s\(0:47:00 – 1:04:00\)\s{2}"
                                       r"Isabel\sGil\s\(1:04:00 -2:00:00\)\s{2}"
                                       r"Juliana\sMateus\s\(2:00:00-2:40:00\)",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"\s*Código\stranscriptora:\s{3}03\s{2}06\s{2}04\s{2}05\s{2}02",
                                       "  ", contents_replaced)
            # End of custom replacements
            contents_replaced = re.sub(r"\s*\**Código\s?(de)?\s?(del)?\s?transcriptor(a|es)?:?\**\s+\d{0,3}\s?\**\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s*\**Fecha\s?final\s?de\s?(la)?\s?transcripción:?\**\s*"
                                       r"((\d{1,2})?\s*\**((\s*de\s*)|/|-)(\w+|\d{2})((\s*de\s*)|/|-|\s)?(\d{4})?)?"
                                       r"(\s\**)?",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"\s*\**Duración\s?(total)?\s?(del)?\s?(de)?\s?(la)?\s?(audio|entrevista)s?:?\s?"
                                       r"\**"
                                       r"(\s*(((\d{1,2}’{0,2}”?)|(\**)):?)+\s*((min\.)|(minutos))?)+"
                                       r"\s*\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Top block
            contents_replaced = re.sub(r"^\s*\**(Transcripción)?\s?entrevista(número)?:?"
                                       r"(\s?\(#\d{3,4}\))?\s?\d{3}\s?-\s?\w{2}\s?-\s?\d{3,5}\**\s?\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Top block
            contents_replaced = re.sub(r"^\s*Transcripción\sentrevista:(\s\w+)+\.?\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Second block (header)
            contents_replaced = re.sub(r"^\s*Aclaración\sde\setiquetas\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Aclaraciones\ssobre\sla\sentrevista([^\]]+)\]", "  ", contents_replaced)
            # Second block (actor tags)
            contents_replaced = re.sub(r"^\s*\**Etiquetas(\sTranscripción)?(\sUsadas)?\**\s{2}",
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
            contents_replaced = re.sub(r"^\s*\**\s*(Etiquetas\s)?Transcripción\**\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Interrupción:\s\[INTERRUP\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Continuación:\s\[CONT\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Inaudible:\s\[INAD\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Dudoso:\s\[DUD\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[TRA\]:\stransliteración", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[DUD\]:\stranscripción\sdudosa", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INAD\]:\sinaudible", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Interrup\]:\sinterrupción", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Cont\]:\sContinuación", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Corte\s\(de\sla\sgrabación\):\s\[CORTE\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Pausa\s\(en\sel\shilo\sde\sla\sentrevista\):\s\[PAUSA\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Información\sincluida:\s[\[{]INC[\]\}]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Transliteración:\s\[TRA\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Lenguaje\sno\sverbal\s\(risa\so\sllanto\):\s\[LNV\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA:\s?(\d{1,2}:?\s?)*\s?-\s?(\d{1,2}:?)*\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[CORTE:?\s?(\d{1,2}:?)*\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*{3}\s{2}", "  ", contents_replaced)
            # Custom first block
            contents_replaced = re.sub(r"^\s+Entrevistas", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Investigación\spara\sel\sesclarecimiento\sde\sla\sverdad\s"
                                       r"en\sla\sfrontera\sColombia\sy\sVenezuela",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Datos\sde\sla\sentrevista", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sMaria\sRubiela\sGutiérrez\s{1}"
                                       r"\s{2}Miembro\sdel\spartido\sde\sla\sUnión\sPatriótica,\s"
                                       r"residenciado\sen\sla\sciudad\sde\sCúcuta",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sTania\sAgudelo\s{1}"
                                       r"\s{2}Miembro\sdel\spartido\sde\sla\sUnión\sPatriótica,\s"
                                       r"residenciado\sen\sla\sciudad\sde\sCúcuta",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sWilmer\sRangel\s{1}"
                                       r"\s{2}Presidente\sde\sJunta\sdel\sBarrio\sHugo\sChaves,\sSaravena,\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sAdriana\sConstanza\sCorona\s{1}"
                                       r"\s{1}Víctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sChiquito,\s"
                                       r"municipio\sde\sTibú",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sSoley\sRueda\s"
                                       r"\sVíctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sLargo,\s"
                                       r"municipio\sde\sTibú",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sObdulio\sCastro\s"
                                       r"\sVíctima\sde\sdesplazamiento\sforzado,\sde\sBarrio\sLargo,\s"
                                       r"municipio\sde\sTibú",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sRodrigo\sEsmigle\sGutiérrez\sFranco\s"
                                       r"\sDel\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\s"
                                       r"departamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistado:\sMarlene\sPérez\s"
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
            contents_replaced = re.sub(r"^\s*Entrevistado:\sMarta\sEsperanza\sRodríguez\s"
                                       r"\sDel\sasentamiento\sel\sRefugio,\smunicipio\sde\sArauca,\s"
                                       r"departamento\sde\sArauca",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistador:\sMaría\sAngelica\sGonzález,\s"
                                       r"investigadora\spara\scasos\sde\sexilio,\s+"
                                       r"desplazamiento y\s+"
                                       r"despojo en la frontera",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Entrevistador:\sTania\sAgudelo,\smiembro\sde\sla\sUP\sy\sMaría\sAngelica\s"
                                       r"González,\sinvestigadora\spara\s+"
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
            contents_replaced = re.sub(r"^\s*\[CONT\]\s{2}Continuación", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[CORTE\]\s{2}Corte\s\(de\sla\sgrabación\)", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[DUD\]:?\s+Dudoso", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*ENT\s{2}Entrevistador", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INAD\]\s{2}Inaudible", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\[INC\]\s{2}Información\sincluida", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INTERRUP\]\s{2}Interrupción", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA\]\s{2}Pausa\s\(en\sel\shilo\sde\sla\sentrevista\):",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*TEST\s{2}Testimoniante", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*X\s{2}Interlocutor\sdesconocido", "  ", contents_replaced)
            # Top block
            contents_replaced = re.sub(r"^(\s*\[Lengua(indígena)?\sembera\skatío([^\]]+)\]"
                                       r"(\sMartha\sCecilia\sDomicó\sDomicó)?)+",
                                       "  ", contents_replaced)
            # Top block
            contents_replaced = re.sub(r"^\s*\**Lectura\sy\srepuesta\sdel\sconsentimiento\sinformado\s\(.*\)\**",
                                       "  ", contents_replaced)
            # Top block
            contents_replaced = re.sub(r"^\s*"
                                       r"\**"
                                       r"("
                                       r"(\s([/\-|])?\s?)|"
                                       r"(\d{3}[-–]\w{2}[-–]\d{5})|"
                                       r"(\d{1,2}:\d{2}\s[apAP][mM])|"
                                       r"(\d{2}[-/]\d{2}[-/]\d{4})"
                                       r")+"
                                       r"(\s|\*)*\s{2}",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Ficha\s?(Corta)?\]?:?([^\]]+)\]",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**\s*\[(Lectura\sde)?\s*consent?it?miento(\sinformado)?([^\]]+)\]\.?\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*Transcripción:((\s\w+)+|(\s\d+))\.?\s{2}", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*Inicio\sde\sentrevista:\s(\d{1,2}’{1,2}:?)+\s{2}", "  ", contents_replaced)
            # The following expression repeats twice on interview 393-VI-00021 the full content repeats twice
            contents_replaced = re.sub(r"^\s*\**Transcriptor:\s\d{3}(\s|\*)*\s{2}",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\**Tiempo:\s(\d{2}:?)+\**",
                                       "  ", contents_replaced, flags=re.IGNORECASE)
            # Top block
            contents_replaced = re.sub(r"^\s*\**\s*_?"
                                       r"INICIO\s?(TRANSCRIPCIÓN)?:?\s*"
                                       r"(((\d{2,4}-\d{2}-\d{2,4})|(\d{1,2}:\d{2}))(\s*[-–]*\s*))*"
                                       r"_?\**",
                                       "  ", contents_replaced)
            # Top blocks
            contents_replaced = re.sub(r"^\s*\[Datos\spersonales([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INAD([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[PAUSA([^\]]+)\]", "  ", contents_replaced, flags=re.IGNORECASE)
            contents_replaced = re.sub(r"^\s*\[SIL([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[Datos:([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\[INC:([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^Explicación\sdel\strabajo\srealizado\spor\sla\sComisión\sde\sla\sVerdad\s"
                                       r"y\selconsentimiento\sinformado\s([^\]]+)\]", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\**\d{1,2}:\d{2}\s?(PM)?m?\**", "  ", contents_replaced)
            # Actor tag fix
            contents_replaced = re.sub(r"^ENT\.", "ENT:", contents_replaced)
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
            contents_replaced = re.sub(r"^\[Información\spersonal\s-\sconsentimiento\sinformado\]([^\]]+)\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^19 6:00 pm 8:30 pm 25/11/2019 2:00 pm 4 pm 28-11-2019 2 pm - 6:30 pm",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*29/11/2019 3:00 – 5:30", "  ", contents_replaced)
            contents_replaced = re.sub(r"^216ENT:\sVIENT:\s00031", "  ", contents_replaced)
            contents_replaced = re.sub(r"^Entrevista:\sFanny\sNavarro\.", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\*\*Entrevistadora:\*\*\s98", "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Lugar\sy\sfecha\sde\sentrevista:\*\*\s"
                                       r"El\sDorado,\sMeta\s-\s21\sde\sagosto\sde\s2019\.",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Lugar\sde\slos\sHechos\*\*\s:\sPuerto\sSiare,\sMapiripán,\sMeta\.",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"^\s*\*\*Entrevista:\*\*\s23", "  ", contents_replaced)
            contents_replaced = re.sub(r"\[Consentimiento\sInformado:\s00:50\s–\s5:30\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"\[Consentimiento\sInformado:\s00:39\s-\s8:36\]",
                                       "  ", contents_replaced)
            contents_replaced = re.sub(r"\[Consentimiento\sinformado:\s00\.00:00\s-\s00:08:00\]",
                                       "  ", contents_replaced)
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
                                       "ENT: Esperanza Carlosama, ¿no? ¿En dónde nació usted? ¿Y en qué fecha?  "
                                       "TEST: Aquí en la vereda [INAUD], el 23 de Marzo del 63.  "
                                       "ENT: Bueno. ¿Usted es casada?  "
                                       "TEST: No.  "
                                       "ENT: ¿Soltera?  "
                                       "TEST: Soltera.  "
                                       "ENT: ¿Sufre de alguna discapacidad?  "
                                       "TEST: Diabética.  "
                                       "ENT: ¿Enfermedad? Bueno diabética, ¿pero discapacidad como tal?  "
                                       "TEST: No, discapacidad no, pues tengo es una [INAUD].  "
                                       "ENT: ¿Usted a qué se dedica? ¿Cuál es el oficio suyo?  "
                                       "TEST: Agricultura.  "
                                       "ENT: Ah, a la agricultura, bueno. Específicamente vive aquí en la Sancina, "
                                       "pero barrio nada vereda o colinda, ¿no?  "
                                       "TEST: No, aquí.  "
                                       "ENT: ¿Usted como se considera? ¿Una persona como le diría yo? "
                                       "¿Indígena, campesina?  "
                                       "TEST: Campesina pues como todos, aquí.", contents_replaced)
            contents_replaced = re.sub(r"^Sara Consuelo Mora Luna "
                                       r"Certifico que conozco las cláusulas de confidencialidad al tomar este "
                                       r"testimonio, en lo que "
                                       r"respecta a la información, al tratamiento de la información, la autorización "
                                       r"que tengo de la "
                                       r"Comisión de la Verdad para realizar esta labor, igual las sanciones a las que "
                                       r"me someto por el "
                                       r"incumplimiento de esta confidencialidad y también, en lo que se refiere "
                                       r"a garantizar al "
                                       r"entrevistado la protección de sus datos personales. "
                                       r"Voy a tomar el testimonio a Manuela Duque Álvarez, hoy 30 de julio en "
                                       r"Santiago de Chile, en el "
                                       r"FASIC. "
                                       r"Tema: Testimonio",
                                       "S: Sara Consuelo Mora Luna. "
                                       "S: Certifico que conozco las cláusulas de confidencialidad al tomar este "
                                       "testimonio, en lo que "
                                       "respecta a la información, al tratamiento de la información, la autorización "
                                       "que tengo de la "
                                       "Comisión de la Verdad para realizar esta labor, igual las sanciones a las que "
                                       "me someto por el "
                                       "incumplimiento de este de esta confidencialidad y también en lo que se refiere "
                                       "a garantizar al "
                                       "entrevistado la protección de sus datos personales. "
                                       "S: Voy a tomar el testimonio a Manuela Duque Álvarez, hoy 30 de julio en "
                                       "Santiago de Chile, en el FASIC. "
                                       "El tema, testimonio.", contents_replaced)
            result = pattern.search(contents_replaced)
            if result is None\
                    or result.group(1) == 'Entrevistada'\
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