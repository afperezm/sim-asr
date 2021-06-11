import argparse
import csv
import geocoder
import os
import pandas as pd
import progressbar
import psycopg2

PERSON_INTERVIEWED_QUERY = "SELECT id_persona_entrevistada, id_entrevista, id_persona, codigo_entrevista, " \
                           "es_victima, es_testigo, nombre, apellido, otros_nombres, fec_nac_anio, fec_nac_mes, " \
                           "fec_nac_dia, lugar_nac_codigo, lugar_nac_n1_codigo, lugar_nac_n1_txt, " \
                           "lugar_nac_n2_codigo, lugar_nac_n2_txt, sexo_id, sexo_txt, edad, grupo_etario, " \
                           "orientacion_sexual_id, orientacion_sexual_txt, identidad_genero_id, " \
                           "identidad_genero_txt, pertenencia_etnica_id, pertenencia_etnica_txt, " \
                           "pertenencia_indigena_id, pertenencia_indigena_txt, documento_identidad_tipo_id, " \
                           "documento_identidad_tipo_txt, documento_identidad_numero, nacionalidad_id, " \
                           "nacionalidad_txt, estado_civil_id, estado_civil_txt, lugar_residencia_codigo, " \
                           "lugar_residencia_n1_codigo, lugar_residencia_n1_txt, lugar_residencia_n2_codigo, " \
                           "lugar_residencia_n2_txt, lugar_residencia_n3_codigo, lugar_residencia_n3_txt, " \
                           "lugar_residencia_n3_lat, lugar_residencia_n3_lon, lugar_residencia_zona_id, " \
                           "lugar_residencia_zona_txt, lugar_residencia_descripcion, educacion_formal_id, " \
                           "educacion_formal_txt, profesion, ocupacion_actual, d_sensorial, d_intelectual, " \
                           "d_psicosocial, d_fisica, cargo_publico, cargo_publico_cual, fuerza_publica_miembro, " \
                           "fuerza_publica_estado, fuerza_publica_especificar, actor_armado_ilegal, " \
                           "actor_armado_ilegal_especificar, organizacion_colectivo_participa, relato, " \
                           "insert_id_entrevistador, insert_fecha_hora, insert_fecha, insert_fecha_mes, " \
                           "update_id_entrevistador, update_fecha_hora " \
                           "FROM analitica.persona_entrevistada " \
                           "WHERE lugar_nac_codigo IS NOT NULL AND lugar_residencia_codigo IS NOT NULL"


def main():
    user = PARAMS.user
    password = PARAMS.password
    host = PARAMS.host
    port = PARAMS.port
    database = PARAMS.database
    key = PARAMS.key
    # data_dir = "./"

    connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=database)

    # Convert query results
    persons_interviewed_df = pd.read_sql_query(PERSON_INTERVIEWED_QUERY, connection)

    # Add born location geographic coordinate fields
    persons_interviewed_df['lugar_nac_n2_lat'] = None
    persons_interviewed_df['lugar_nac_n2_lon'] = None

    row_count = len(persons_interviewed_df.index)

    bar = progressbar.ProgressBar(max_value=row_count)
    for row_idx, row in enumerate(persons_interviewed_df.itertuples(), start=1):
        # Geocode born location if not present
        if row.lugar_nac_n2_lat is None:
            # TODO Beware that level 2 (n2) location might be None
            # Concatenate born location names
            born_location = ', '.join(filter(None, [row.lugar_nac_n2_txt, row.lugar_nac_n1_txt]))
            # TODO control queries per second since Google Geocoding API has a quota of 50 QPS
            # Geocode born location
            g = geocoder.google(born_location, key=key)
            print(born_location)
            print(g)
            persons_interviewed_df.at[row.Index, 'lugar_nac_n2_lat'] = g.latlng[0]
            persons_interviewed_df.at[row.Index, 'lugar_nac_n2_lon'] = g.latlng[1]
        # Geocode residence location if not present
        if row.lugar_residencia_n3_lat is None:
            # TODO Beware that either level 2 (n2) or level 3 (n3) locations might be None
            # Concatenate residence location names
            residence_location = ', '.join(filter(lambda l: '' if l is None or l == '[Internacional]' else l,
                                                  [row.lugar_residencia_n3_txt, row.lugar_residencia_n2_txt,
                                                   row.lugar_residencia_n1_txt]))
            # TODO control queries per second since Google Geocoding API has a quota of 50 QPS
            # Geocode residence location
            g = geocoder.google(residence_location, key=key)
            print(residence_location)
            print(g)
            persons_interviewed_df.at[row.Index, 'lugar_residencia_n3_lat'] = g.latlng[0]
            persons_interviewed_df.at[row.Index, 'lugar_residencia_n3_lon'] = g.latlng[1]
        # print(row)
        bar.update(row_idx)
    bar.update(row_count)

    compression_opts = dict(method='zip', archive_name='persons_interviewed.csv')

    persons_interviewed_df.to_csv('persons_interviewed.zip', index=False, sep='\t', compression=compression_opts)

    connection.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Retrieval of interviewed people data."
    )
    parser.add_argument(
        "--user",
        type=str,
        help="User",
        required=True)
    parser.add_argument(
        "--password",
        type=str,
        help="Password",
        required=True)
    parser.add_argument(
        "--host",
        type=str,
        help="Host",
        required=True)
    parser.add_argument(
        "--port",
        type=str,
        help="Port",
        required=True)
    parser.add_argument(
        "--database",
        type=str,
        help="Database",
        required=True)
    parser.add_argument(
        "--key",
        type=str,
        help="Google API key",
        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    PARAMS = parse_args()
    main()
