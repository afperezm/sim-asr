import argparse
import glob
import operator
import os
import pprint
import re
# import unicodedata
from num2words import num2words


def main():
    parser = argparse.ArgumentParser(description="Regex-based transcripts tag cleaner")
    parser.add_argument("--in_dir", type=str, help="Input data directory, where intro-clean transcripts are located",
                        required=True)
    parser.add_argument("--out_dir", type=str, help="Output data directory, where to copy tag-clean transcripts",
                        required=True)

    args = parser.parse_args()

    transcript_files = glob.glob("{0}/*.txt".format(args.in_dir))

    actor_tags = {}
    trans_tags = {}
    time_tags = {}

    actor_tags_black_list = ['Transcriptor', 'Y dijieron', 'Objetivos principales', 'Y', 'Primer fracaso', 'Dije',
                             'Papá', 'Dijo ', 'Entonces dijo ', 'Entonces dije', 'Ella dice', 'Y allá', 'Bueno',
                             'Después decía', '**Me dijo', 'Otro', 'Don Dilson', 'Vea', 'Cuando dijo', 'Él dijo ',
                             'Dije yo', 'yo ', 'Entonces', 'Pausa', 'Y entonces', 'Tonces decía', 'Y yo', 'Ella dijo',
                             'Toes dijimos', 'habían ahí', 'Decían', 'Y dijeron', 'Y nosotros', 'Pues mire',
                             'Y nosotras', 'Dice', 'Dijo alberto', 'Aquí está', 'Él decía', 'Monté tutelas',
                             'Le cuento', 'Yo digo', 'El contexto', 'Dijeron', 'A ver', 'Datos', 'PAUSA', 'Me dijeron',
                             'Les dijeron', 'Entonces dijeron', 'Ya dijeron', 'Les dije', 'Y dijo', 'Yo dije',
                             'Le dije', 'Entonces dijo', 'Dijo']

    for transcript_file in sorted(transcript_files):

        basename = os.path.splitext(os.path.basename(transcript_file))[0]

        print("Processing... {0}".format(basename))

        with open(transcript_file) as f:
            contents = f.read()

        # Fixes for wrong tags
        contents = re.sub(r"\[de,\sde,\sde\}",
                          "[de, de, de]", contents)
        contents = re.sub(r"\[INTERRUP\n\n\s\s\n\nENT:\sUno\sde\sellos\.",
                          "[INTERRUP]\n\nENT: Uno de ellos.", contents)
        contents = re.sub(r"\[Departamento\sdel\sSur\sde\sColombia\?",
                          "[Departamento del Sur de Colombia]?", contents)
        contents = re.sub(r"\[INAD\n1:35:02\}",
                          "[INAD\n1:35:02]", contents)
        contents = re.sub(r"\[INAD: Los helenos",
                          "[INAD:] Los helenos", contents)
        contents = re.sub(r"\[INBAD:38:04",
                          "[INBAD:38:04]", contents)
        contents = re.sub(r"\[INBAD:38:04",
                          "[INBAD:38:04]", contents)
        contents = re.sub(r"\[Fondo\sde\sSolidaridad\scon\slos\nJueces\sColombianos\?",
                          "[Fondo de Solidaridad con los\nJueces Colombianos]", contents)
        contents = re.sub(r"\[INTERRUP\n\n\s\s\n\nENT:\sAdicción",
                          "[INTERRUP]\n\n\n\nENT: Adicción", contents)
        contents = re.sub(r"\[Ismaelina",
                          "Ismaelina", contents)
        contents = re.sub(r"¿Cuántos\s\[cuántos\sson\sniños\?",
                          "¿Cuántos cuántos son niños?", contents)
        contents = re.sub(r"\[PAUSA:\s38:51-39:03\?",
                          "[PAUSA: 38:51-39:03]", contents)
        contents = re.sub(r"\[audio:\s¿mm\?\?",
                          "[audio: ¿mm?]", contents)
        contents = re.sub(r"\[INTERRUP\n\nENT:\sLo\sque\sle\sdecía\sÓscar",
                          "[INTERRUP]\n\nENT: Lo que le decía Óscar", contents)
        contents = re.sub(r"\[PAUSA\s18:40\s-\s18:50",
                          "[PAUSA 18:40 - 18:50]", contents)
        contents = re.sub(r"\[INC:\sAsociación\sde\sCabildos\sIndígenas\ndel\sValle\"",
                          "[INC: Asociación de Cabildos Indígenas\ndel Valle]", contents)
        contents = re.sub(r"\[que\}",
                          "[que]", contents)
        contents = re.sub(r"TEST:\sBueno,\scuando,\svuelvo\sy\sle\srepito,\sellos\sincursionan\.\.\.\n\nINTERRUP\[",
                          "TEST: Bueno, cuando, vuelvo y le repito, ellos incursionan...\n\n[INTERRUP]", contents)
        contents = re.sub(r"\[susurro\}",
                          "[susurro]", contents)
        contents = re.sub(r"\[INTERRUP\n\n\s\s\n\nENT:\s¿Medico,\senfermeros\so\?",
                          "[INTERRUP]\n\n\n\nENT: ¿Medico, enfermeros o?", contents)
        contents = re.sub(r"Allá\scerca\sde\sCartagena,\sen\suna\s\[INTERRUP\.",
                          "Allá cerca de Cartagena, en una [INTERRUP].", contents)
        contents = re.sub(r"\[susurra\}",
                          "[susurro]", contents)
        contents = re.sub(r"vuelticas\s\[\sde\scomida", "vuelticas de comida", contents)
        contents = re.sub(r"\[PAUSA\s00:28\s00:56",
                          "[PAUSA 00:28 00:56]", contents)
        contents = re.sub(r"\[FORMATO\n00:37:34\s-\s00:",
                          "[FORMATO\n00:37:34 - 00:]", contents)
        contents = re.sub(r"\[y\[", "[y]", contents)
        contents = re.sub(r"TEST:\sen\sese\sentonces\sera\sde\sla\sAutodefensa\s"
                          r"\[INC:\sAutodefensas\sUnidas\sde\nColombia\.",
                          "TEST: en ese entonces era de la Autodefensa "
                          "[INC: Autodefensas Unidas de\nColombia].", contents)
        contents = re.sub(r"\[Fuerzas\sArmadas\sRevolucionarias\sde\sColombia\?",
                          "[Fuerzas Armadas Revolucionarias de Colombia]?", contents)
        contents = re.sub(r"\[INAD:\s13:26-13:28\[",
                          "[INAD: 13:26-13:28]", contents)
        contents = re.sub(r"\[INAUD:\s00:22:41\?",
                          "[INAUD: 00:22:41]", contents)
        contents = re.sub(r"\[INTERRUP\[",
                          "[INTERRUP]", contents)
        contents = re.sub(r"\[CONT\[",
                          "[CONT]", contents)
        contents = re.sub(r"\[INC:\nComunidad\sde\sPaz\sde\sSan\sJosé\sde\sApartadó\?",
                          "[INC:\nComunidad de Paz de San José de Apartadó]", contents)
        contents = re.sub(r"\[INTERRUP\n\nENT:",
                          "[INTERRUP]\n\nENT:", contents)
        contents = re.sub(r"\[haaa\}", "{haaa}", contents)
        contents = re.sub(r"\[CONT:\sElla\ses\sdel\s93",
                          "[CONT] Ella es del 93", contents)
        contents = re.sub(r"\[risas\}",
                          "[risas]", contents, flags=re.IGNORECASE)
        contents = re.sub(r"\[audio:\sAjam,",
                          "[audio: Ajam],", contents)
        contents = re.sub(r"\[risas\.",
                          "[risas].", contents, flags=re.IGNORECASE)
        contents = re.sub(r"\[INC:\sCaldono,\sCauca\.",
                          "[INC: Caldono, Cauca].", contents)
        contents = re.sub(r"\*\*_\[En\sel\sminuto\s10:01\sse\sregistra\suna\spausa\sen\sel\saudio\?_\*\*",
                          "ENT: Sigamos que hubo ruido raro, hubo una música que nos iba a dañar la grabación "
                          "y por eso la paramos.",
                          contents)
        contents = re.sub(r"aquí\sen\sel\sbarrio\s\[INTERRUP",
                          "aquí en el barrio [INTERRUP]", contents)
        contents = re.sub(r"\[Plan\sde\sAtención\sAsistencia\sy\sReparación\sIntegral,",
                          "[Plan de Atención Asistencia y Reparación Integral],", contents)
        contents = re.sub(r"\[INT\[",
                          "[INT]", contents)
        contents = re.sub(r"\[Risas\[",
                          "[Risas]", contents, flags=re.IGNORECASE)
        contents = re.sub(r"Jorge\s40\s\[baja\sla\svoz",
                          "Jorge 40 [baja la voz]", contents)
        contents = re.sub(r"\[Unidad para la Atención y Reparación Integral de las\nVíctimas?",
                          "[Unidad para la Atención y Reparación Integral de las\n Víctimas]?", contents)
        contents = re.sub(r"\[\ssúper\scomplicada\.",
                          "[súper complicada].", contents)
        contents = re.sub(r"\[INAD\[",
                          "[INAD]", contents)
        contents = re.sub(r"\[INAD:\s,",
                          "[INAD:],", contents)
        contents = re.sub(r"\[INC: Parques\nNacionales Naturales de Colombia\?",
                          "[INC: Parques\nNacionales Naturales de Colombia]?", contents)
        contents = re.sub(r"\[INAD:\n\nENT:\sDentro\sde\sla\scaja",
                          "[INAD:]\n\nENT: Dentro de la caja.", contents)
        contents = re.sub(r"INTERRUP\]\[",
                          "[INTERRUP]", contents)
        contents = re.sub(r"\[Ahhh\}",
                          "[Ahhh]", contents)
        contents = re.sub(r"\[INC:\sE\.S\.E\.\sHospital\sSan\nVicente\sde\sPaul,\s¿cierto\?",
                          "[INC: E.S.E. Hospital San\nVicente de Paul], ¿cierto?", contents)
        contents = re.sub(r"\[Diligenciamiento\sde\sfichas:\s00:20\s-\s00:55",
                          "[Diligenciamiento de fichas: 00:20 - 00:55]", contents)
        contents = re.sub(r"\[la\npaz\}",
                          "[la\npaz]", contents)
        contents = re.sub(r"\[INAD\}",
                          "[INAD]", contents)
        contents = re.sub(r"\[risa\}",
                          "[risa]", contents)
        contents = re.sub(r"\[INC:\sINSTITUTO\sNACIONAL\sDE\sVIVIENDA\sDE\sINTERÉS\sSOCIAL\sY\sREFORMA\sURBANA\)",
                          "[INC: INSTITUTO NACIONAL DE VIVIENDA DE INTERÉS SOCIAL Y REFORMA URBANA]", contents)
        contents = re.sub(r"\[DUD:\s¿Jaider\?\s27:20\s¿Heider\?",
                          "[DUD: 27:20] Jaider", contents)
        contents = re.sub(r"\[estuve\strabajando",
                          "estuve trabajando", contents)
        contents = re.sub(r"\[CONT: 11 y media de la noche",
                          "[CONT:] 11 y media de la noche", contents)
        contents = re.sub(r"\[eh\}",
                          "[eh]", contents)
        contents = re.sub(r"\[de lo\}",
                          "{de lo}", contents)
        contents = re.sub(r"\[audio:\s¿um\?",
                          "[audio: ¿um?]", contents)
        contents = re.sub(r"\[INC:\sUniversidad\sSurcolombiana\?",
                          "[INC: Universidad Surcolombiana]?", contents)
        contents = re.sub(r"\[pícara",
                          "pícara", contents)
        contents = re.sub(r"\[llanto\}",
                          "[llanto]", contents)
        contents = re.sub(r"\[DUD: cedió 03:44",
                          "[DUD: 03:44] se dió", contents)
        contents = re.sub(r"\[Ficha\sCorta:\s00:45\s03:29",
                          "[Ficha Corta: 00:45 03:29]", contents)
        contents = re.sub(r"\[CONT\n\nTEST:\sSí,\sseñor\.",
                          "[CONT]\n\nTEST: Sí, señor.", contents)
        contents = re.sub(r"\[INC:\sentonces\}",
                          "[INC: entonces]", contents)
        contents = re.sub(r"\[INTERRUPT\n\nENT:\s¿Cómo\ses\sque\sse\sllamaba\?",
                          "[INTERRUPT]\n\nENT: ¿Cómo es que se llamaba?", contents)
        contents = re.sub(r"\[INTERRUP]\n\nTEST:\sSi,\ses\sque\sLeonardo\sy\sel\sPadre\sEduardo\sDiaz",
                          "[INTERRUP]\n\nTEST: Si, es que Leonardo y el Padre Eduardo Diaz", contents)
        contents = re.sub(r"\[risas\+",
                          "[risas]", contents)
        contents = re.sub(r"\[INAD:\s09:53\s09:54\[",
                          "[INAD: 09:53 09:54]", contents)
        contents = re.sub(r"\[Llanto,",
                          "[Llanto],", contents)
        contents = re.sub(r"\[INAD:\sy\sla\shija\sestá\sen\sBogotá,",
                          "[INAD:] y la hija está en Bogotá,", contents)
        contents = re.sub(r"\[Datos\sPersonales:\s20:02\?",
                          "[Datos Personales: 20:02]?", contents)
        contents = re.sub(r"\[INC:\sÉL\sle\srespondió",
                          "[INC:] Él le respondió", contents)
        contents = re.sub(r"\[surniar\}",
                          "[surniar]", contents)
        contents = re.sub(r"\[Audio:\s¿mmmm\?",
                          "[Audio:] ¿mmmm?", contents, flags=re.IGNORECASE)
        contents = re.sub(r"\[Mmm, déjeme quieto",
                          "Mmm, déjeme quieto", contents)
        contents = re.sub(r"\[Análisis\nEstratégico\sB2\"",
                          "[Análisis\nEstratégico B2]", contents)
        contents = re.sub(r"si\susted\sve\sla\sgente\sde\nlos\scarros\.\.\.\s\[",
                          "si usted ve la gente de\nlos carros...", contents)
        contents = re.sub(r"Los\sparamilitares,\sla\sguerrilla\sno\.\.\.\[INTERRUP",
                          "Los paramilitares, la guerrilla no...[INTERRUP]", contents)
        contents = re.sub(r"organización\s\[INA\.",
                          "organización [INAUD].", contents)
        contents = re.sub(r"\[homosexuales,\slesbianas,\stravestis\)\?",
                          "[homosexuales, lesbianas, travestis]?", contents)
        contents = re.sub(r"\[INC:\sUnidad\sde\sAtención\nde\sVictimas\.",
                          "[INC: Unidad de Atención\nde Victimas].", contents)
        contents = re.sub(r"\[CORTE:43:30",
                          "[CORTE:43:30]", contents)
        contents = re.sub(r"\[Datos personales26:22 -26:39",
                          "[Datos personales: 26:22-26:39]", contents)
        contents = re.sub(r"\[Fuerzas\sArmadas\nRevolucionarias\sde\sColombia\?",
                          "[Fuerzas Armadas\nRevolucionarias de Colombia]?", contents)
        contents = re.sub(r"\[Porque no querían dejar rastro",
                          "Porque no querían dejar rastro", contents)
        contents = re.sub(r"\[INAP: 1:20:40 - 1:20:42",
                          "[INAUD:1:20:40-1:20:42]", contents)
        contents = re.sub(r"\[FICHA\s00:46-0",
                          "[FICHA 00:46-0]", contents)
        contents = re.sub(r"\[INTERRUp\n\nENT:\sSe\slo\sllevaba",
                          "[INTERRUP]\n\nENT: Se lo llevaba", contents)
        contents = re.sub(r"\[Continuación\saudio\spor\smódulo\sde\scapture",
                          "[Continuación audio por módulo de capture]", contents)
        contents = re.sub(r"\[INTERRUP\n\nTES:\sHubieron\s4\smuertos",
                          "[INTERRUP]\n\nTES: Hubieron 4 muertos", contents)
        contents = re.sub(r"ah’\[i",
                          "ahí", contents)
        contents = re.sub(r"\[INTERRUP\n\n\s\s\n\nTEST:\sUn\ssubsidio\sde\svivienda\.",
                          "[INTERRUP]\n\n\n\nTEST: Un subsidio de vivienda.", contents)
        contents = re.sub(r"toes\s\[INC:\sentonces",
                          "toes [INC: entonces]", contents)
        contents = re.sub(r"\[sorprendida¨",
                          "[sorprendida]", contents)
        contents = re.sub(r"\[jumm\}",
                          "[jumm]", contents)
        contents = re.sub(r"en la \[DUD:\nautoridad\?\scarretera\?\s13:49",
                          "a estudiar", contents)
        contents = re.sub(r"\[INC:\shaya\}",
                          "[INC: haya]", contents)
        contents = re.sub(r"\[CONT:\sBueno,\sla\sguerrilla",
                          "[CONT] Bueno, la guerrilla", contents)
        contents = re.sub(r"\[audio:\s¿mm\?",
                          "[audio: ¿mm?]", contents)
        contents = re.sub(r"\[INTERRUP\n\nTEST:\sSi,\ses\sque\sLeonardo\sy\sel\sPadre\sEduardo\sDiaz",
                          "[INTERRUP]\n\nTEST: Si, es que Leonardo y el Padre Eduardo Diaz", contents)
        contents = re.sub(r"¡Ustedes\ssalían\shasta\sBarranca\s\[INC:\sBarrancabermeja!",
                          "¡Ustedes salían hasta Barranca [INC: Barrancabermeja]!", contents)
        contents = re.sub(r"ENT:\s¿Cuánto\s\[INTERRUP\?",
                          "ENT: ¿Cuánto [INTERRUP]?", contents)
        contents = re.sub(r"ENTENT:\sENT:",
                          "ENT:", contents)
        contents = re.sub(r"ENT:\s¿ENTENT:\s¿ENENT:",
                          "ENT:", contents)
        contents = re.sub(r"INAD:05:46-05:55",
                          "[INAD:05:46-05:55]", contents)
        contents = re.sub(r"A\spartir\sdel\s1:12:00\sse\sencuentran\sllenando\sla\sficha\slar\so\scorta-\s1:12:54\n\n"
                          r"1:12:55",
                          "[A partir del 1:12:00 se encuentran llenando la ficha lar o corta- 1:12:54\n\n"
                          "1:12:55]", contents)
        contents = re.sub(r"\[INTERRUP\]06:12",
                          "[INTERRUP: 06:12]", contents)
        contents = re.sub(r"06:16\s\[CONT\]",
                          "[CONT: 06:16]", contents)
        contents = re.sub(r"\[PAUSA\]1:41:05\]",
                          "[PAUSA: 1:41:05]", contents)
        contents = re.sub(r"TEST:1:",
                          "TEST1:", contents)
        contents = re.sub(r"\[DUD\n\n33:22\sQuintines\]",
                          "[DUD: 33:22] Quintines", contents)
        contents = re.sub(r"T:EST:",
                          "TEST:", contents)
        contents = re.sub(r"TES:T",
                          "TEST:", contents)
        contents = re.sub(r"\[Ficha\scorta:\s1:14:38\s1:23:24",
                          "[Ficha corta: 1:14:38-1:23:24]", contents)
        contents = re.sub(r"\[\[\s_El\sviento\sno\sdeja\sescuchar\sgran\sparte\sdel\saudio_\s\]",
                          "[INAD]", contents)
        contents = re.sub(r",:\s\[\suna\ses\sel\scambio\sclimático",
                          ", una es el cambio climático", contents)
        contents = re.sub(r"\[mm,\smmm\}",
                          "[mm, mmm]", contents)
        contents = re.sub(r"\[Heee\}",
                          "[Heee]", contents)
        contents = re.sub(r"\[de\saquí\sde\saquí\}",
                          "[de aquí de aquí]", contents)
        contents = re.sub(r"\[que\[",
                          "[que]", contents)
        contents = re.sub(r"\[tenía\)",
                          "[tenía]", contents)
        contents = re.sub(r"\[voy\sbien\scon\sla\sPersonera",
                          "[voy bien] con la Personera", contents)
        contents = re.sub(r"\[Contesta\ssu\steléfono\scelular",
                          "[Contesta su teléfono celular]", contents)
        contents = re.sub(r"\[balbucea\s1:00:40",
                          "[balbucea 1:00:40]", contents)
        contents = re.sub(r"\[el\sdía\sque\ssacaron\slas\sarmas",
                          "[el día que sacaron las armas]", contents)
        contents = re.sub(r"Consentimiento\s07:32",
                          "[Consentimiento 07:32]", contents)
        contents = re.sub(r"Pausa:\s19:54\s-20:02\]",
                          "[Pausa: 19:54 -20:02]", contents)
        contents = re.sub(r"PAUSA:\s37:38\s-\s37:52",
                          "[PAUSA: 37:38 - 37:52]", contents)
        contents = re.sub(r"\[DUD:\s00:22:01\s-\sDUD:\s00:22:03\]",
                          "[DUD: 00:22:01-00:22:03]", contents)
        contents = re.sub(r"\[DUD:43:01\s43:04\[",
                          "[DUD:43:01-43:04", contents)
        contents = re.sub(r"\[INTERRUP:\s1\.27:55\]",
                          "[INTERRUP: 1:27:55]", contents)
        contents = re.sub(r"\[INTERRUP:\sesposa\s00:38:18\shasta\s00:38:30\]",
                          "[INTERRUP: 00:38:18-00:38:30]", contents)
        contents = re.sub(r"ocupada\s\[risas\]\s\[INTERRUP",
                          "ocupada [risas] [INTERRUP]", contents)
        contents = re.sub(r"presentó\s\[INTERRUP\.",
                          "presentó [INTERRUP].", contents)
        contents = re.sub(r"\[CONT:\sDel\sGolfo",
                          "[CONT] Del Golfo", contents)
        contents = re.sub(r"\[PAUSA:\sDiligenciamiento\sde\sfichas:\s09:12-12:11\]",
                          "[PAUSA: 09:12-12:11]", contents)
        contents = re.sub(r"\[DUD:1:22:23\[",
                          "[DUD:1:22:23]", contents)
        contents = re.sub(r"\(INAD:\s23:15\)",
                          "[INAD: 23:15]", contents)
        contents = re.sub(r"vaina\.\s1:19:33",
                          "vaina.", contents)
        contents = re.sub(r"mantiene\.\s1:10:35",
                          "mantiene.", contents)
        contents = re.sub(r"DUD\s11:09\s\\-\s11:13",
                          "[DUD: 11:09-11:13]", contents)
        contents = re.sub(r"\[PAUSA\]:\s1:17:22\s-\s1:17:25]",
                          "[PAUSA: 1:17:22-1:17:25]", contents)
        contents = re.sub(r"Consentimiento\sinformado:\s00:20\s\\-\s01:18\]",
                          "[Consentimiento informado: 00:20-01:18]", contents)
        contents = re.sub(r"Datos\ssensibles\s49:10]",
                          "[Datos sensibles: 49:10]", contents)
        contents = re.sub(r"\.\s\(PAUSA:12:52\)",
                          "[PAUSA: 12:52]", contents)
        contents = re.sub(r"INAD:\s06:09-\s06:12]",
                          "[INAD: 06:09-06:12]", contents)
        contents = re.sub(r"1:00:47entonces",
                          "entonces", contents)
        contents = re.sub(r"\[Consentimiento\sInformado:\n1:04:42\s\\-\s1:05:12\.",
                          "[Consentimiento Informado:\n1:04:42-1:05:12]", contents)
        contents = re.sub(r"estas\s1:19:35",
                          "estas!", contents)
        contents = re.sub(r"vendida42:10",
                          "vendida.", contents)
        contents = re.sub(r"región01:12",
                          "región", contents)
        contents = re.sub(r"DUD:\s54:15",
                          "[DUD: 54:15]", contents)
        contents = re.sub(r"DUD:\s52:07-52:13",
                          "[DUD: 52:07-52:13]", contents)
        contents = re.sub(r"preguntó\sDUD:\s47:18",
                          "preguntó [DUD: 47:18]", contents)
        contents = re.sub(r"para\sDUD:\s44:16",
                          "para [DUD: 44:16]", contents)
        contents = re.sub(r"daban\sDUD:39:13",
                          "daban [DUD:39:13]", contents)
        contents = re.sub(r"que\sDUD:\s23:11",
                          "que [DUD: 23:11]", contents)
        contents = re.sub(r"Si,\sDUD:17:20",
                          "Si, [DUD:17:20]", contents)
        contents = re.sub(r"en\sel\sDUD:\s17:17",
                          "en el [DUD: 17:17]", contents)
        contents = re.sub(r"la\.\.\.\sDUD:\s15:17",
                          "la... [DUD: 15:17]", contents)
        contents = re.sub(r"viniera\sel\sDUD:\s03:17",
                          "viniera el [DUD: 03:17]", contents)
        contents = re.sub(r"\[PAUSA\.\sDoña\sMercedes\srecibe\sllamada\scelular\s1:19:05\s-\s1:19:36\]",
                          "[PAUSA: 1:19:05-1:19:36]", contents)
        contents = re.sub(r"¿qué\stiene?\s1:01:19",
                          "¿qué tiene?", contents)
        contents = re.sub(r"\[DUD:\sAllá\sla\svida\ses\sdura\s03:16\]",
                          "[DUD: 03:16]", contents)
        contents = re.sub(r"boconcita27:14",
                          "boconcita", contents)
        contents = re.sub(r"\[DUD:\ntrataban\s05:16-05:17\]",
                          "[DUD:\n05:16-05:17]", contents)
        contents = re.sub(r"DUD:14:29\.\.\.",
                          "[DUD:14:29]", contents)
        contents = re.sub(r"muchas\sDUD:25:16",
                          "muchas [DUD:25:16]", contents)
        contents = re.sub(r"eso\sque\sDUD:\s26:15",
                          "eso que [DUD: 26:15]", contents)
        contents = re.sub(r"Marulanda\sDUD:14:19",
                          "Marulanda [DUD:14:19]", contents)
        contents = re.sub(r"jugo\sa\sDUD: 04:10",
                          "jugo a [DUD: 04:10]", contents)
        contents = re.sub(r"ilícitos en\nINAD:49:15",
                          "ilícitos en\n[INAD:49:15]", contents)
        contents = re.sub(r"presentan\sDUD:\s38:16",
                          "presentan [DUD: 38:16]", contents)
        contents = re.sub(r"mataron\sa\sDUD:\s23:13",
                          "mataron a [DUD: 23:13]", contents)
        contents = re.sub(r"este\sDUD:\s22:58",
                          "este [DUD: 22:58]", contents)
        contents = re.sub(r"1:08:16 Liz Vega",
                          "Liz Vega", contents)
        contents = re.sub(r"\[DUD:\sTiempo\]\s13:17\sRP\?\]",
                          "[DUD: 13:17]", contents)
        contents = re.sub(r"\[DUD:\s04:56\sconsigue\sjoda\?\]\spara\sarreglar\s10\stubos,",
                          "Alvaro Reinaldi", contents)
        contents = re.sub(r"\[DUD:\s05:04\sde\slenguajes,\nentoncé\shagamó\seso,\ssino\ssá\"\?\]\.",
                          "en ese entonces Adamos Espinoza", contents)
        contents = re.sub(r"05:13\sRenaldi\?\]",
                          "Alvaro Reinaldi", contents)
        contents = re.sub(r"vida59:18",
                          "vida", contents)
        contents = re.sub(r"Célimo\sPortilla\s05:14",
                          "Célimo Portilla", contents)
        contents = re.sub(r"11\+\s4:\s14\s\+4:18\+7:25",
                          "once, cuatro, catorce y cuatro diecocho y siete veinticinco", contents)
        contents = re.sub(r"\(Silencio\s33:18\s-\s33:38\)",
                          "[Silencio 33:18-33:38]", contents)
        contents = re.sub(r"\(silencio\)\s00:54\s-01:13",
                          "[silencio: 00:54-01:13]", contents)
        contents = re.sub(r"30:19mucha gente",
                          "mucha gente", contents)
        contents = re.sub(r"\(hay\sun\smomento\sen\sel\sque\sse\scorta\suna\sfrase\)\s\(35:10\)",
                          "[hay un momento en el que se corta una frase 35:10]", contents)
        contents = re.sub(r"\[ficha\s\(corta\]\stestimonio\svíctima:\s00:55\n-\s01:14\]",
                          "[ficha corta testimonio víctima: 00:55\n-01:14]", contents)
        contents = re.sub(r"\[inad\]\s53:10",
                          "[INAD: 53:10]", contents)
        contents = re.sub(r"\[INAD:\s\*\*\*\*\s07:13\\-\s07:14\]",
                          "[INAD: 07:13-07:14]", contents)
        contents = re.sub(r"07:15\s¡ah!",
                          "¡ah!", contents)
        contents = re.sub(r"\[DUD:\sMi\snombre\s06:10\]",
                          "[DUD: 06:10]", contents)
        contents = re.sub(r"\(Consentimiento\sInformado\sy\sTratamiento\sde\sDatos:\s00:50\s-\s06:19\)",
                          "[Consentimiento Informado y Tratamiento de Datos: 00:50-06:19]", contents)
        contents = re.sub(r"\(Diligenciamiento\sde\sConsentimiento\sInformado:\s00:47\s-\s01:36\)",
                          "[Diligenciamiento de Consentimiento Informado: 00:47-01:36]", contents)
        contents = re.sub(r"\(Tratamiento\sde\sDatos\spersonales\sy\ssensibles:\s01:37\s-\s05:11\)",
                          "[Tratamiento de Datos personales y sensibles: 01:37-05:11]", contents)
        contents = re.sub(r"\[Tratamiento\sde\sDatos\sPersonales\s00:37\s-\s05:16",
                          "[Tratamiento de Datos Personales: 00:37-05:16]", contents)
        contents = re.sub(r"INAD:\s32:13\s-\n32:16",
                          "[INAD: 32:13-32:16]", contents)
        contents = re.sub(r"PAUSA:19:03-19:14\]",
                          "[PAUSA:19:03-19:14]", contents)
        contents = re.sub(r"\[DUD:\sMusso1:20:15\]",
                          "[DUD: 1:20:15]", contents)
        contents = re.sub(r"\[INAD\.\n24:13\]",
                          "[INAD: 24:13]", contents)
        contents = re.sub(r"Datos:\s23:13\shasta\s31:25",
                          "[Datos: 23:13-31:25]", contents)
        contents = re.sub(r"\[DUD:\s1:17:54\\-\s1:17:58\"",
                          "[DUD: 1:17:54-1:17:58]", contents)
        contents = re.sub(r"Un\s1:12:50,\sun\scañamon",
                          "Un, un cañamon", contents)
        contents = re.sub(r"\[INAD:\s45:54\\-\s46:12\sProblemas\scon\sel\saudio,\ssuena\sentrecortado\]",
                          "[INAD: 45:54-46:12]", contents)
        contents = re.sub(r"porque\nverdaderamente\s1:11:02\s1:11:07",
                          "porque\nverdaderamente", contents)
        contents = re.sub(r"\[DUD:\sEl\sCascajo\s00:16\]",
                          "[DUD: 00:16]", contents)
        contents = re.sub(r"¿cómo\sel\sEstado\s1:11:14",
                          "¿cómo el Estado?", contents)
        contents = re.sub(r"eso\sno\ses\s1:10:43",
                          "eso no es", contents)
        contents = re.sub(r"INAD:\s04:05-04:10\]",
                          "[INAD: 04:05-04:10]", contents)
        contents = re.sub(r"DUD:18:15/18:16\]",
                          "[DUD:18:15-18:16]", contents)
        contents = re.sub(r"\[Ficha\scorta:\s39:49\s\\-\s40:48",
                          "[Ficha corta: 39:49-40:48]", contents)
        contents = re.sub(r"\.\.\.\sINAD:21:06\]",
                          "... [INAD: 21:06]", contents)
        contents = re.sub(r"\(no\sentiendo:07:08\)",
                          "[DUD: 07:08]", contents)
        contents = re.sub(r"38:56la",
                          "[DUD: 38:56] la", contents)
        contents = re.sub(r",\s44:30",
                          "[DUD: 44:30]", contents)
        contents = re.sub(r",\s43:35",
                          "[DUD: 43:35]", contents)
        contents = re.sub(r",\[DUD:\sEstuviste\sesta\sRoblé,\sde\sAyda\stambién\s35:46\n35:47\]",
                          "[DUD: 35:46-35:47]", contents)
        contents = re.sub(r"\(no\srecuerda\nbien\)\]",
                          "[no recuerda\nbien]", contents)
        contents = re.sub(r"\[risas que tengo",
                          "[risas] que tengo", contents)
        contents = re.sub(r"\[ahí,\sahí\}",
                          "{ahí, ahí}", contents)
        contents = re.sub(r"\[\]INTERRUP\]",
                          "[INTERRUP]", contents)
        contents = re.sub(r"\[Tratamiento\sde\sDatos:\s11:52\s-\s12:28",
                          "[Tratamiento de Datos: 11:52 - 12:28]", contents)
        contents = re.sub(r"\[INAD:\s27:17-27:26\[",
                          "[INAD: 27:17-27:26]", contents)
        contents = re.sub(r"\[Ficha\sCorta:\s1:59:38\s\\-\s2:07:43",
                          "[Ficha Corta: 1:59:38-2:07:43]", contents)
        contents = re.sub(r"\[mm\smm\]\[",
                          "{mm mm}", contents)
        contents = re.sub(r"\[\]presentadora\sde\snoticias\]",
                          "[presentadora de noticias]", contents)
        contents = re.sub(r"\nINTERRUPCIÓN\n",
                          "[INTERRUP]", contents)
        contents = re.sub(r"fumigar al ejército INTERRUP",
                          "fumigar al ejército [INTERRUP]", contents)
        contents = re.sub(r"la\scolaboración\sque\.\.\.\sINTERUMP",
                          "la colaboración que... [INTERUMP]", contents)
        contents = re.sub(r"vereda\sINTERUMP",
                          "vereda [INTERRUP]", contents)
        contents = re.sub(r"imagino\.\.\.\sINTERUMP",
                          "imagino... [INTERRUP]", contents)
        contents = re.sub(r"INTERUMP\sENT:\s¿Cuántos\saños\stenía\susted\sen\sese\stiempo\?",
                          "[INTERUMP] ENT: ¿Cuántos años tenía usted en ese tiempo?", contents)
        contents = re.sub(r"\*INTERRUMP\]",
                          "[INTERRUP]", contents)
        contents = re.sub(r"\[Clímaco\sRamos\sDUD38:42\]",
                          "[DUD: 38:42]", contents)
        contents = re.sub(r"\[56:47\s-56:49\sINAD\]",
                          "[INAD: 56:47-56:49]", contents)
        contents = re.sub(r"\[Colegio\sIFI\sde\nCartagena\sDUD:\s09:24\]",
                          "Colegio IFI de\nCartagena [DUD: 09:24]", contents)
        contents = re.sub(r"\[ficha\s\(corta\]\stestimonio\svíctima:\s24:54\s-\n25:34\]",
                          "[ficha (corta) testimonio víctima: 24:54-\n25:34]", contents)
        contents = re.sub(r"\[DUD:\schaparranunas09:37\]",
                          "chaparranunas [DUD: 09:37]", contents)
        contents = re.sub(r"\[DUD:\sTarcisio\sÁlvarez\s03:55\]",
                          "Tarcisio Álvarez [DUD: 03:55]", contents)
        contents = re.sub(r"\[38:06\s\\-\s38:20\nINAD\]",
                          "[INAD: 38:06-38:20]", contents)
        contents = re.sub(r"\[INC:\sFiscalía,\sDUD:\s08:14]",
                          "[INC: Fiscalía] [DUD: 08:14]", contents)
        contents = re.sub(r"\[INC:\n\[INTERRUP\]",
                          "[INC]\n[INTERRUP]", contents)
        contents = re.sub(r"\[INC:\sexplicación\s–\sDUD\s10:31\]",
                          "[INC: explicación] [DUD 10:31]", contents)
        contents = re.sub(r"Datos\spersonales:\s00:25:08\]",
                          "[Datos personales: 00:25:08]", contents)
        contents = re.sub(r"Datos\spersonales:\s01:00:13\]",
                          "[Datos personales: 01:00:13]", contents)
        contents = re.sub(r"\[Corte\sde\sla\sgrabación:\s01:22:30\]",
                          "[Corte de la grabación: 01:22:30]", contents)
        contents = re.sub(r"\(Silencio\sal\sparecer\smuestra\sfotos\s1:23:23\)\s1:23:40",
                          "[Silencio al parecer muestra fotos 1:23:23-1:23:40]", contents)
        contents = re.sub(r"\(1:02:39\ssilencio-1:02:47\)",
                          "[Silencio: 1:02:39-1:02:47]", contents)
        contents = re.sub(r"\[PAUSA\s\(Timbra\scelular\):1:14:01\n-1:14:43\s\]",
                          "[PAUSA: 1:14:01\n-1:14:43]", contents)
        contents = re.sub(r"\[DUD:\ssolenciado1:32:15\]",
                          "solenciado [DUD: 1:32:15]", contents)
        contents = re.sub(r"\[DUD:\nNaiso1:09:24\]",
                          "Naiso [DUD: 1:09:24]", contents)
        contents = re.sub(r"\[DUD:\s\"penejues\"\s1:05:34\]",
                          "penejues [DUD: 1:05:34]", contents)
        contents = re.sub(r"\[DUD:\sMulFincarton\s1:33:37\]",
                          "MulFincarton [DUD: 1:33:37]", contents)
        contents = re.sub(r"\[DUD:\sCumbarco1:24:55\]",
                          "Cumbarco [DUD: 1:24:55]", contents)
        contents = re.sub(r"\[DUD:\namotis\s1:01:19\]",
                          "amotis [DUD: 1:01:19]", contents)
        contents = re.sub(r"\[DUD:\smete1:31:04\]",
                          "mete [DUD: 1:31:04]", contents)
        contents = re.sub(r"\[DUD:\sMiry1:41:19\]",
                          "Miry [DUD: 1:41:19]", contents)
        contents = re.sub(r"\[DUD:\sSAIS\s\[INC:\sServicios\nAeroportuarios\sIntegrados\]\s1:02:57\]",
                          "SAIS [DUD: 1:02:57] [INC: Servicios\nAeroportuarios Integrados]", contents)
        contents = re.sub(r"\[PAUSA:\sinformación\sficha\s2:47:04\s\\-\s2:47:54\s\]",
                          "[PAUSA: 2:47:04-2:47:54]", contents)
        contents = re.sub(r"\[DUD:\smete1:31:04\]",
                          "mete [DUD: 1:31:04]", contents)
        contents = re.sub(r"allá\s1:28:43\]",
                          "allá [DUD: 1:28:43]", contents)
        contents = re.sub(r"\[DUD:\sNielsen\s1:21:08\]",
                          "Nielsen [DUD: 1:21:08]", contents)
        contents = re.sub(r"_En\sel\sminuto_\s1:36:02\s_inicia\sun\scorte\sen\sel\saudio_",
                          "[CORTE: 1:36:02]", contents)
        contents = re.sub(r"\[INAD\s\*\*\s1:17:40\*\*\]",
                          "[INAD: 1:17:40]", contents)
        contents = re.sub(r"En\sel\sminuto\s2:35:00\sla\sentrevista\sse\stermina\sintempestivamente\.",
                          "[CORTE: 2:35:00]", contents)
        contents = re.sub(r"\[Eh\[",
                          "[Eh]", contents)
        contents = re.sub(r"{risas\]",
                          "[risas]", contents)
        contents = re.sub(r"\[INAD:\s\|21:47-21:49\]",
                          "[INAD: 21:47-21:49]", contents)
        contents = re.sub(r"\[DUD:\nbaldiaban07:56\]",
                          "baldiaban [DUD: 07:56]", contents)
        contents = re.sub(r"\[DUD: benjén07:29\]",
                          "benjén [DUD: 07:29]", contents)
        contents = re.sub(r"\[INAD 28:41 ENT: 28:46\]",
                          "[INAD: 28:41-28:46]", contents)
        contents = re.sub(r"\[PAUSA: 29:10 ,29:31\]",
                          "[PAUSA: 29:10-29:31]", contents)
        contents = re.sub(r"\[DUD: PIV 34:56\]",
                          "PIV [DUD: 34:56]", contents)
        contents = re.sub(r"\[DUD: Emeteri 58:36\]",
                          "Emeteri [DUD: 58:36]", contents)
        contents = re.sub(r"\[DUD: Olmedo\nPisimué26:11\]",
                          "Olmedo\nPisimué [DUD: 26:11]", contents)
        contents = re.sub(r"\[DUD: dirección de nosotros\nera esa 13:56\]",
                          "dirección de nosotros\nera esa [DUD: 13:56]", contents)
        contents = re.sub(r"\[DUD: estudianda32:42\]",
                          "estudianda [DUD: 32:42]", contents)
        contents = re.sub(r"\[DUD: la han en la lista09:50\]",
                          "la han en la lista [DUD: 09:50]", contents)
        contents = re.sub(r"\[DUD:\nbimbronazos02:42\]",
                          "bimbronazos\n[DUD:02:42]", contents)
        contents = re.sub(r"\[DUD: ¿entieso\? 17:02\]",
                          "¿entieso? [DUD: 17:02]", contents)
        contents = re.sub(r"\[DUD: aida\? aeda\? 00:32\]",
                          "Aeda [DUD: 00:32]", contents)
        contents = re.sub(r"por lo 05:20\]",
                          "por lo [05:20]", contents)
        contents = re.sub(r"\[DUD: pildoro 52:27\]",
                          "pildoro [DUD: 52:27]", contents)
        contents = re.sub(r"\[DUD: Letará19:55\]",
                          "Letará [DUD: 19:55]", contents)
        contents = re.sub(r"\[DUD: Cardapal 01:59\]",
                          "Cardapal [DUD: 01:59]", contents)
        contents = re.sub(r"\[DUD: Carcuel 30:11\]",
                          "Carcuel [DUD: 30:11]", contents)
        contents = re.sub(r"\[DUD: sanal 29:47\]",
                          "sanal [DUD: 29:47]", contents)
        contents = re.sub(r"\[DUD: mujeras 06:19\]",
                          "mujeras [DUD: 06:19]", contents)
        contents = re.sub(r"\[DUD: sin embargo 03:37\]",
                          "sin embargo [DUD: 03:37]", contents)
        contents = re.sub(r"\[DUD: ARACI12:59\]",
                          "ARACI [DUD: 12:59]", contents)
        contents = re.sub(r"\[DUD:\nestersionaría12:30\]",
                          "estersionaría\n[DUD: 12:30]", contents)
        contents = re.sub(r"\[DUD: Ruanoyela13:31\]",
                          "Ruanoyela [DUD: 13:31]", contents)
        contents = re.sub(r"\[DUD: Buenoyela02:48\]",
                          "Buenoyela [DUD: 02:48]", contents)
        contents = re.sub(r"\[DUD: diario 01:05\]",
                          "diario [DUD: 01:05]", contents)
        contents = re.sub(r"\[DUD: combe 27:45\]",
                          "combe [DUD: 27:45]", contents)
        contents = re.sub(r"\[DUD: dubitaba 11:42\]",
                          "dubitaba [DUD: 11:42]", contents)
        contents = re.sub(r"\[DUD: susiro08:00\]",
                          "susiro [DUD: 08:00]", contents)
        contents = re.sub(r"\[DUD: Puerto López13:31\]",
                          "Puerto López [DUD: 13:31]", contents)
        contents = re.sub(r"\[DUD: Mamia32:19\]",
                          "Mamia [DUD: 32:19]", contents)
        contents = re.sub(r"\[DUD: uno nació muerto10:41\]",
                          "uno nació muerto [DUD: 10:41]", contents)
        contents = re.sub(r"\[DUD: Lucho 07:23\]",
                          "Lucho [DUD: 07:23]", contents)
        contents = re.sub(r"\[DUD: Trinolozepan41:18\]",
                          "Trinolozepan [DUD: 41:18]", contents)
        contents = re.sub(r"\[DUD:\nescuadras47:05\]",
                          "escuadras\n[DUD: 47:05]", contents)
        contents = re.sub(r"\[DUD: Nerys15:54\]",
                          "Nerys [DUD: 15:54]", contents)
        contents = re.sub(r"\[PAUSA: información personal para diligenciar\nlas fichas 2:34:34\\- 2:35:34\]",
                          "[PAUSA: 2:34:34-2:35:34]", contents)
        contents = re.sub(r"\[INAD: interferencia por la misma situación de señal 28:09-28:26\]",
                          "[INAD: 28:09-28:26]", contents)
        contents = re.sub(r"\[DUD: ¿Simoa\? 05:39\]",
                          "¿Simoa? [DUD: 05:39]", contents)
        contents = re.sub(r"\[ficha \(corta\] testimonio víctima: 18:34 - 24:02\]",
                          "[ficha (corta) testimonio víctima: 18:34-24:02]", contents)
        contents = re.sub(r"\[DUD: \"mixtos\" 59:52\]",
                          "\"mixtos\" [DUD: 59:52]", contents)
        contents = re.sub(r"\[INC: Vale Pavas o Vale Adentro\]\n14:27\]",
                          "[INC: Vale Pavas o Vale Adentro]\n[DUD: 14:27]", contents)
        contents = re.sub(r"\[INAD: \*\*14\*\* :42\]",
                          "[INAD: 14:42]", contents)
        contents = re.sub(r"\[DUD:\nMezolana 24:45\]",
                          "Mezolana\n[DUD: 24:45]", contents)
        contents = re.sub(r"\[DUD: Estorbio Silva24:17\]",
                          "Estorbio Silva [DUD: 24:17]", contents)
        contents = re.sub(r"\[DUD: pisteando la casa con un celular 03:47\]",
                          "pisteando la casa seguro [DUD: 03:47]", contents)
        contents = re.sub(r"\[DUD: Nielsen de León 56:21\]",
                          "Nielsen de León [DUD: 56:21]", contents)
        contents = re.sub(r"\[DUD:\s-15:3915:42\]",
                          "[DUD: 15:39-15:42]", contents)
        contents = re.sub(r"\[DUD: Joime53:50\]",
                          "Joime [DUD: 53:50]", contents)
        contents = re.sub(r"\[DUD: Neva 47:17\]",
                          "Neva [DUD: 47:17]", contents)
        contents = re.sub(r"\[PAUSA 26:50 descanso por el estado emocional de la entrevistada 27:15\]",
                          "[PAUSA 26:50-27:15]", contents)
        contents = re.sub(r"\[DU:31\]D\s15:24\]",
                          "[DUD: 15:24]", contents)
        contents = re.sub(r"\[DUD:\nSixe45:43\]",
                          "Sixe\n[DUD: 45:43]", contents)
        contents = re.sub(r"\[DUD: Buselas 43:28\]",
                          "Buselas [DUD: 43:28]", contents)
        contents = re.sub(r"\[DUD: Michalan 10:01\]",
                          "Michalan [DUD: 10:01]", contents)
        contents = re.sub(r"\[DUD: GRAIG 53:03\]",
                          "GRAIG [DUD: 53:03]", contents)
        contents = re.sub(r"\[DUD: GRAIG\n52:57\]",
                          "GRAIG\n[DUD: 52:57]", contents)
        contents = re.sub(r"\[DUD:\nDolila 13:41\]",
                          "Dolila\n[DUD: 13:41]", contents)
        contents = re.sub(r"\[DUD: Colegio Fray Isidoro de Monclar 30:01\]",
                          "Colegio Fray Isidoro de Monclar [DUD: 30:01]", contents)
        contents = re.sub(r"\[DUD: fertitura01:32\]",
                          "fertitura [DUD: 01:32]", contents)
        contents = re.sub(r"\[ficha \(corta\] testimonio víctima 49:24 - 57:24\]",
                          "[ficha (corta) testimonio víctima: 49:24-57:24]", contents)
        contents = re.sub(r"\[ficha \(corta\] testimonio víctima: 00:32 -\n00:36\]",
                          "[ficha (corta) testimonio víctima: 00:32-\n00:36]", contents)
        contents = re.sub(r"\[DATOSPERSONALES\] 56:37\]",
                          "[Datos personales: 56:37]", contents)
        contents = re.sub(r"\[INAD\s39:59\sENT:\s40:09\]",
                          "llamo a mi al celular,\n"
                          "porque el sabía mi número celular. Pero yo nunca recibi una llamada de él, ¿si?", contents)
        contents = re.sub(r"\[DUD: revolpiar12:05\]",
                          "revolpiar [DUD: 12:05]", contents)
        contents = re.sub(r"\[DUD: Coronado 05:33\]",
                          "Coronado [DUD: 05:33]", contents)
        contents = re.sub(r"\[DUD: Estuviste esta Roblé, de Ayda también 35:46\n35:47\]",
                          "Estuviste esta Roblé, de Ayda también [DUD: 35:46\n35:47]", contents)
        contents = re.sub(r"\[DUD: Tayaeque 32:40\]",
                          "Tayaeque [DUD: 32:40]", contents)
        contents = re.sub(r"\[DUD: Dalmaco Hoyos 26:47\]",
                          "Dalmaco Hoyos [DUD: 26:47]", contents)
        contents = re.sub(r"\[DUD: Evelecer 27:24\]",
                          "Evelecer [DUD: 27:24]", contents)
        contents = re.sub(r"\[DUD Benecer10:25\]",
                          "Benecer [DUD 10:25]", contents)
        contents = re.sub(r"\[DUD: Inbanaco18:53\]",
                          "Inbanaco [DUD: 18:53]", contents)
        contents = re.sub(r"\[INAD:\sENT:\s42:11\]",
                          "[INAD: 42:11]", contents)
        contents = re.sub(r"\[DUD:\nFray\sIsidoro\sde\sMonclar10:03\]",
                          "Fray Isidoro de Monclar [DUD: 10:03]", contents)
        contents = re.sub(r"\[DUD:\scataré09:54\]",
                          "cataré [DUD: 09:54]", contents)
        contents = re.sub(r"\[datos\]\s00:25\s00:30",
                          "[Datos sensibles: 00:25-00:30]", contents)
        contents = re.sub(r"01:31\s01:34",
                          "[Datos sensibles: 1:31-1:34]", contents)
        contents = re.sub(r"\[INAD\]\s03:21",
                          "[INAD: 3:21]", contents)
        contents = re.sub(r"\[DUD\]03:24",
                          "[DUD: 3:24]", contents)
        contents = re.sub(r"\[DUD;\s03:36-03:37\sacá,\stenía\sbakí\]",
                          "vaqui [DUD: 3:36-3:37]", contents)
        contents = re.sub(r"\(CORTE:\s04:52\)",
                          "[CORTE: 4:52]", contents)
        contents = re.sub(r"\[inad]\s05:07",
                          "[INAD: 5:07]", contents)
        contents = re.sub(r"\[DUD\]\s05:43",
                          "[DUD: 5:43]", contents)
        contents = re.sub(r"\[INAD:\]\s06:32",
                          "[INAD: 6:32]", contents)
        contents = re.sub(r"\[inad\]\s07:03",
                          "[INAD: 7:03]", contents)
        contents = re.sub(r"\\-------\s08:38\sHasta\sacá\sse\sescucha\scon\smucha\sdificultad\sel\saudio\s"
                          r"y\sse\sescucha\nun\scorto\.\s----------",
                          "[CORTE: 8:38]", contents)
        contents = re.sub(r"\[inad\]\s09:04",
                          "[INAD: 9:04]", contents)
        contents = re.sub(r"\[DUD:01:56/01:57]",
                          "[DUD: 1:56-1:57]", contents)
        contents = re.sub(r"\[INAD:\n18:40\s-\s10:42\]",
                          "[INAD: 18:40-10:42]", contents)
        contents = re.sub(r"Eso\sfue\scomo\sa\slas\s12:00\sm\sque",
                          "Eso fue como a las 12:00 p.m. que", contents)
        contents = re.sub(r"como\sse\siba\sa\slas\s12:00m\sno\svino\sa\salmorzar",
                          "como se iba a las 12:00 p.m. no vino a almorzar", contents)
        contents = re.sub(r"salió\sa\slas\s12:00m\sa\salmorzar",
                          "salió a las 12:00 p.m. a almorzar", contents)
        contents = re.sub(r"\(Dud:\s12:55\)",
                          "[DUD: 12:55]", contents)
        contents = re.sub(r"\(se\scorta\sun\spoco\s4:16\)",
                          "[se corta un poco 4:16]", contents)
        contents = re.sub(r"\(Min 8:23 llora se reinicia 9:12\)",
                          "[Min 8:23 llora se reinicia 9:12]", contents)
        contents = re.sub(r"una casa y 01:56 y uno que sigue metido entre el conflicto",
                          "una casa y [DUD: 1:56] y uno que sigue metido entre el conflicto", contents)
        contents = re.sub(r"como un 02:04 como un personal",
                          "como un [DUD: 2:04] como un personal", contents)
        contents = re.sub(r"yo no tengo 02:50",
                          "yo no tengo [DUD: 2:50]", contents)
        contents = re.sub(r"pude educarlos\.03:38",
                          "pude educarlos.[DUD: 3:38]", contents)
        contents = re.sub(r"Y como acá mandaban eran ellos, que 04:42",
                          "Y como acá mandaban eran ellos, que [DUD: 4:42]", contents)
        contents = re.sub(r"Sí, en toda la avenida\. 04:58",
                          "Sí, en toda la avenida. [DUD: 4:58]", contents)
        contents = re.sub(r"en la Personería del Dorado\.05:59",
                          "en la Personería del Dorado.[DUD: 5:59]", contents)
        contents = re.sub(r"Familiares todos, amigos, paisanos\. 06:12",
                          "Familiares todos, amigos, paisanos. [DUD: 6:12]", contents)
        contents = re.sub(r"ya paso el tiempo y06:31",
                          "ya paso el tiempo y[DUD: 06:31]", contents)
        contents = re.sub(r"todo \[llanto\]\. 07:12",
                          "todo [llanto 7:12].", contents)
        contents = re.sub(r"hata ahí llegué\. 07:33",
                          "hasta ahí llegué. [DUD: 7:33]", contents)
        contents = re.sub(r"en adelante 09:11 hasta las 8",
                          "en adelante [DUD: 9:11] hasta las 8", contents)
        contents = re.sub(r"¿Las vacunas eran para quién\? 10:01",
                          "¿Las vacunas eran para quién? [DUD: 10:01]", contents)
        contents = re.sub(r"conmigo\s\[llanto\]\s06:32",
                          "conmigo [llanto 6:32]", contents)
        contents = re.sub(r"\[DUD:\shabían\nmandado\?\s02:45\s\]",
                          " habían mandado\n[DUD: 2:45]", contents)
        contents = re.sub(r"\[dud\]\s02:08",
                          "[DUD: 2:08]", contents)
        contents = re.sub(r"\[DUD:27:43:27:45\]",
                          "[DUD: 27:43-27:45]", contents)
        contents = re.sub(r"\[INAD:\s01:27:55\s–\s01:2759\]",
                          "[INAD: 1:27:55-1:27:59]", contents)
        contents = re.sub(r"\[DUD: 10:13:10:15\]",
                          "[DUD: 10:13-10:15]", contents)
        contents = re.sub(r"\[DUD: 10:37:10:39\]",
                          "[DUD: 10:37-10:39]", contents)
        contents = re.sub(r"\[DUD: 10:44:10:45\]",
                          "[DUD: 10:44-10:45]", contents)
        contents = re.sub(r"\[DUD: 19:23:19:24\]",
                          "[DUD: 19:23-19:24]", contents)
        contents = re.sub(r"\[DUD: 21:16:21:17\]",
                          "[DUD: 21:16-21:17]", contents)
        contents = re.sub(r"\[DUD: 23:25:23:28\]",
                          "[DUD: 23:25-23:28]", contents)
        contents = re.sub(r"\[DUD: 17:35:17:37\]",
                          "[DUD: 17:35-17:37]", contents)
        contents = re.sub(r"\[INAD:\n52:!4\]",
                          "[INAD:\n52:14]", contents)
        contents = re.sub(r"\[DUD: 17:16:17:17\]",
                          "[DUD: 17:16-17:17]", contents)
        contents = re.sub(r"\[DUD: 47-53: 47:54\]",
                          "[DUD: 47-53-47:54]", contents)
        contents = re.sub(r"\[DUD: 11:11 con la ley 636\]",
                          "con la ley 636 [DUD: 11:11]", contents)
        contents = re.sub(r"\[DUD: Eso fue como en el 78\]",
                          "Eso fue como en el 78 [DUD]", contents)
        contents = re.sub(r"\[DUD 53:29, 1992\]",
                          " 1992 [DUD 53:29]", contents)
        contents = re.sub(r"\[DUD: 03:11:39:22\]",
                          "[DUD: 03:11-39:22]", contents)
        contents = re.sub(r"\[DUD:\s03:37:39:22\]",
                          "[DUD: 03:37-39:22]", contents)
        contents = re.sub(r"\[DUD:\s34:33:\s34:35\]",
                          "[DUD: 34:33-34:35]", contents)
        contents = re.sub(r"XXX:\s01:03",
                          "XXX: [DUD: 1:03]", contents)
        contents = re.sub(r"3\s0\s4",
                          "3 o 4", contents)
        contents = re.sub(r"aquí\s1\s0\s2\smuertos",
                          "aquí 1 o 2 muertos", contents)
        contents = re.sub(r"200\,300",
                          "200, 300", contents)
        contents = re.sub(r"20380/0271",
                          "20 3 80 slash 0 2 7 1", contents)

        # Custom replacements for non-generalizable expressions
        contents = re.sub(r"\n\**(\d{1,2}:?)+\**\s*\n",
                          "", contents)
        contents = re.sub(r"Quick tips:\n\n"
                          r"\\-\s_Ctrl\+I_\sadds\s_italic_\sformatting\sand\s"
                          r"\*\*Ctrl\+B\*\*\sadds\s\*\*bold\*\* formatting\.\n\n"
                          r"\\-\sPress\sESC\sto\splay/pause,\sand\s"
                          r"Ctrl\+J\sto\sinsert\sthe\scurrent\stimestamp\.\n\n$",
                          "", contents)
        contents = re.sub(r"Tiempo\stranscrito:\s23:37",
                          "", contents)
        contents = re.sub(r"En:\s1:35m:12s\.",
                          "", contents)
        contents = re.sub(r"\[INTERRUP:\sAgua\]",
                          "", contents)
        contents = re.sub(r"25:41\s25:41",
                          "", contents)
        contents = re.sub(r"\[\]",
                          "", contents)
        contents = re.sub(r"\[INFORMACIÓN\sCONFIDENCIAL:\sXXXXX\s19:14\s\]",
                          "", contents)
        contents = re.sub(r"\("
                          r"(Consentimiento\sInformado\s[y-]\s)?"
                          r"Tratamiento\sde\sDatos"
                          r"(\spersonales)?"
                          r"(\spersonales\sy\ssensibles)?"
                          r":?\s\d{2}:\d{2}\s-\s\d{2}:\d{2}\)",
                          "", contents, flags=re.IGNORECASE)
        contents = re.sub(r"\(Datos\ssensibles(:\s\d{2}:\d{2})?\)", "", contents)
        contents = re.sub(r"\d{1,2}:\d{2}:\s?\d{2}\s?-?\s?", "", contents)
        contents = re.sub(r"1[3-9]:\d{2}\s?-?\s?", "", contents)
        contents = re.sub(r"[2-9]\d:\s?\d{2}\s?\\?-?\s?", "", contents)
        contents = re.sub(r"PAUSA(\d{2}:\d{2})?", "", contents)

        standard_actor_tags = [
            r'ENT([2-9]|1[0-2])?',
            r'TEST([2-9]|1[0-2])?',
            r'X([2-9]|1[0-2])?',
            r'ACOMP',
            r'ASIST',
            r'TRD'
        ]

        # Includes predictable variations of standard transcript tags
        standard_trans_tags = [
            r'[\[\(\{]\[?\s?i?I?INTERRUPP?C?T?(IÓN)?:?(\s?(\d{1,2}:?)+\s?-?\s?)*´?¨?\]?[\}\)\]]',
            r'[\[\{\{]\[?\s?I?CONTE?I?N?:?(\s?(\d{1,2}:?)+-?)*[\}\)\]]',
            r'[\[\(\{]'
            r'\[?\s?INAU?DD?O?U?\s?:?;?_?\.?\n{0,2}(\s?(:?\d{1,2}\s?:?\s?;?\.?_?;?)+\s?\\?-?–?a?A?y?\.?\s?)*'
            r'[\}\)\]]',
            r'[\[\(\{]'
            r'\[?\s?(DUD|DUDA|DUDD|DUDE|DUDU|IDUD)\s?_?:?;?_?\.?\n{0,2}\s*((\d{1,2}\s?:?;?,?_?)+\s?\\?-?–?a?A?\.?/?\s?)*'
            r'[\}\)\]]',
            r'\[CORTE:?(\s?(\d{1,2}:?)+-?)*\]',
            r'[\[\(]'
            r'\s?PAUSA(\sDE\sCAFÉ)?(\spor\sllamada)?(\sCORTA)?\s?:?\.?(\s?(:?\d{1,2}\.?:?\s?)+\s?\\?_?-?–?—?_?/?\s?)*'
            r'[\)\]]',
            r'[\[\{\{](INC|INCLUD|INCLUID):?(\s\w,?)+[\}\)\]]',
            r'\[Datos sensibles:?(\s?(\d{1,2}:?)+-?)*\]',
            r'\[Datos personales:?(\s?(\d{1,2}:?)+-?)*\]',
            r'\[Consentimiento Informado:?(\s?(\d{1,2}:?)+\s?\\?-?\s?)*\]',
            r'\[(\d{1,2}:?)+\s(INAD|DUD)\]',
            r'\[(INAD|DUD|INTERRUP|CONT|PAUSA|XXX):?(\s?(\d{1,2}:?)+\s?-?)*',
            r'(INAD|DUD|INTERRUP|CONT|PAUSA|XXX):?(\s?(\d{1,2}:?)+\s?-?)*\]',
            r'(INAD|DUD):?\s?(\d{1,2}:?)+'
        ]

        contents_cleared = contents

        # Replace standard transcript tags
        for trans_tag in standard_trans_tags:
            contents_cleared = re.sub(trans_tag, "", contents_cleared)

        # Find non-standard transcript tags
        content_trans_tags = re.findall(r"\[[^\]]+\]", contents_cleared)
        content_trans_tags = list(set(content_trans_tags))

        # Replace non-standard transcript tags (needs to be done before finding actor tags)
        contents_cleared = re.sub(r"\[[^\]]+\]",
                                  "", contents_cleared)

        # Replace standard actor tags
        for actor_tag in standard_actor_tags:
            contents_cleared = re.sub(r"{0}:".format(actor_tag), "", contents_cleared)

        # Find non-standard actor tags
        content_actor_tags = re.findall(r"\n\n(\**-?\[?\w+\s?\(?\w*\)?\]?\s?#?[12]?\**\s?):", "\n\n" + contents_cleared)
        content_actor_tags = list(set(content_actor_tags) - set(actor_tags_black_list))

        # print("non-standard actor tags")
        # print(content_actor_tags)

        # print("non-standard transcription tags")
        # print(content_trans_tags)

        # Update full set of actor tags
        y = {tag: [basename] for tag in content_actor_tags}
        actor_tags = {key: actor_tags.get(key, []) + y.get(key, []) for key in
                      set(list(actor_tags.keys()) + list(y.keys()))}

        # Update full set of transcription tags
        y = {tag: [basename] for tag in content_trans_tags}
        trans_tags = {key: trans_tags.get(key, []) + y.get(key, []) for key in
                      set(list(trans_tags.keys()) + list(y.keys()))}

        # THIS BLOCK PRODUCES AN ALIGNMENT READY TRANSCRIPTION
        contents_replaced = contents

        # Replace standard and found transcription tags
        content_trans_tags = [re.escape(tag) for tag in content_trans_tags]
        for trans_tag in standard_trans_tags + content_trans_tags:
            contents_replaced = re.sub(trans_tag, "", contents_replaced)

        # Replace newlines with spaces
        contents_replaced = re.sub(r"\n", " ", contents_replaced)

        # Replace standard and found actor tags
        content_actor_tags = [re.escape(tag) for tag in content_actor_tags]
        for actor_tag in standard_actor_tags + content_actor_tags:
            contents_replaced = re.sub(r"{0}:\s*".format(actor_tag), "\n\n", contents_replaced)

        # Trim trailing and duplicated whitespaces
        contents_replaced = re.sub(r"^\s+", "", contents_replaced)
        contents_replaced = re.sub(r"[ ]+", " ", contents_replaced)
        contents_replaced = re.sub(r"\s+$", "", contents_replaced)

        # Split transcription at sentence level
        contents_replaced = re.sub(r"\.{3}", "[ELLIPSIS]", contents_replaced)
        contents_replaced = re.sub(r"\.\s+", ".\n\n", contents_replaced)
        contents_replaced = re.sub(r"\[ELLIPSIS\]", "...", contents_replaced)
        contents_replaced = re.sub(r"\?\s+", "?\n\n", contents_replaced)
        contents_replaced = re.sub(r"!\s+", "!\n\n", contents_replaced)

        # Replace non-spanish alphabet characters
        contents_replaced = re.sub(r"…", "...", contents_replaced)
        contents_replaced = re.sub(r"ahý", "ahí", contents_replaced)
        contents_replaced = re.sub(r"ý", "y", contents_replaced)
        contents_replaced = re.sub(r"[üû]", "u", contents_replaced)
        contents_replaced = re.sub(r"Ü", "U", contents_replaced)
        contents_replaced = re.sub(r"[öò]", "O", contents_replaced)
        contents_replaced = re.sub(r"ï", "i", contents_replaced)
        contents_replaced = re.sub(r"Î", "I", contents_replaced)
        contents_replaced = re.sub(r"ì", "í", contents_replaced)
        contents_replaced = re.sub(r"Ë", "É", contents_replaced)
        contents_replaced = re.sub(r"ë", "e", contents_replaced)
        contents_replaced = re.sub(r"È", "É", contents_replaced)
        contents_replaced = re.sub(r"è", "é", contents_replaced)
        contents_replaced = re.sub(r"ça", "á", contents_replaced)
        contents_replaced = re.sub(r"ça", "á", contents_replaced)
        contents_replaced = re.sub(r"ço", "ó", contents_replaced)
        contents_replaced = re.sub(r"çi", "í", contents_replaced)
        contents_replaced = re.sub(r"çu", "í", contents_replaced)
        contents_replaced = re.sub(r"ç", "", contents_replaced)
        contents_replaced = re.sub(r"Ä", "A", contents_replaced)
        contents_replaced = re.sub(r"[àâäå]", "a", contents_replaced)
        contents_replaced = re.sub("\u0605", "", contents_replaced)
        contents_replaced = re.sub("\u001B", "", contents_replaced)
        contents_replaced = re.sub("\u00AD", "", contents_replaced)

        # TODO Normalize non-spanish alphabet characters
        # contents_replaced = unicodedata.normalize("NFKD", contents_replaced)
        # contents_replaced = contents_replaced.encode("ascii", "ignore").decode("ascii", "ignore")

        # Verbalize hours
        hours = list(set(re.findall(r"(\d{1,2}):(\d{2})(\s?([ap])\.?m\.?)?", contents_replaced)))
        for time in hours:
            word_formatted_hours = num2words(int(time[0]), lang="es_CO")
            word_formatted_minutes = "" if int(time[1]) == 0 else ("cuarto" if int(time[1]) == 15 else (
                "media" if int(time[1]) == 30 else num2words(int(time[1]), lang="es_CO")))
            word_formatted_time = word_formatted_hours if not word_formatted_minutes else "{hours} y {minutes}".format(
                hours=word_formatted_hours, minutes=word_formatted_minutes)
            word_formatted_noon_ind = " de la mañana" if time[3] == "a" else (
                " de la tarde" if time[3] == "p" else "")
            time_key = "{hours}:{minutes}{noon_ind}".format(hours=time[0],
                                                            minutes=time[1],
                                                            noon_ind=time[2])
            time_value = "{time}{noon_ind}{final_dot}".format(time=word_formatted_time,
                                                              noon_ind=word_formatted_noon_ind,
                                                              final_dot="." if time[2].endswith(".") else "")
            contents_replaced = contents_replaced.replace(time_key, time_value)
            time_tags[time_key] = time_value

        # TODO Verbalize numbers
        # content_numbers = re.findall(r"\d+", contents_replaced)
        # content_numbers = list(set(content_numbers))
        # content_numbers.sort(key=lambda s: len(s), reverse=True)
        # print(content_numbers)
        # [num2words(number, lang="es_CO") for number in sorted(content_numbers)]

        # Write out formatted transcription
        with open("{0}/{1}.txt".format(args.out_dir, basename), "wt") as file:
            file.write(contents_replaced)

        print("Done")

    # Print full set of actor tags
    # print("Non-standard actor tags:")
    # pprint.pprint(actor_tags)
    print("Non-standard actor tags count:")
    pprint.pprint(sorted({tag: len(actor_tags[tag]) for tag in actor_tags}.items(),
                         key=operator.itemgetter(1)))

    # Print full set of transcription tags
    # print("Non-standard transcription tags:")
    # pprint.pprint(trans_tags)
    print("Non-standard transcription tags count:")
    pprint.pprint(sorted({tag: len(trans_tags[tag]) for tag in trans_tags}.items(),
                         key=operator.itemgetter(1)))

    pprint.pprint(time_tags)


if __name__ == '__main__':
    main()
