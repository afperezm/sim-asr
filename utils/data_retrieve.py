import argparse
import pandas as pd
import progressbar
import psycopg2
from geopy.exc import GeocoderServiceError
from geopy.geocoders import GoogleV3


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

    connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=database)

    geo_locator = GoogleV3(api_key=key, timeout=5)

    print("- Querying interviewed persons")

    # Convert query results
    persons_interviewed_df = pd.read_sql_query(PERSON_INTERVIEWED_QUERY, connection)

    connection.close()

    # Add born location geographic coordinate fields
    persons_interviewed_df['lugar_nac_n2_lat'] = None
    persons_interviewed_df['lugar_nac_n2_lon'] = None

    row_count = len(persons_interviewed_df.index)

    print(f"  Done, obtained {row_count} rows")

    print("- Geocoding born and residence addresses")

    bar = progressbar.ProgressBar(max_value=row_count)
    for row_idx, row in enumerate(persons_interviewed_df.itertuples(), start=1):
        # Geocode born location if not present
        if row.lugar_nac_n2_lat is None:
            # Concatenate born location names, beware that level 2 (n2) location might be none and thus geocoded
            # location becomes less accurate
            born_location_address = ', '.join(filter(lambda l: '' if l is None or l == '[Internacional]' else l,
                                                     [row.lugar_nac_n2_txt, row.lugar_nac_n1_txt]))
            # Geocode born location, beware it can throw an error if Google Geocoding quota of 50 QPS is exceeded
            try:
                born_location = geo_locator.geocode(born_location_address)
                # print(row_idx, 'born', born_location_address, born_location)
                persons_interviewed_df.at[row.Index, 'lugar_nac_n2_lat'] = born_location.latitude
                persons_interviewed_df.at[row.Index, 'lugar_nac_n2_lon'] = born_location.longitude
            except GeocoderServiceError as e:
                print(f"Error: geocode failed on input {born_location_address} with error {e}")
                persons_interviewed_df.at[row.Index, 'lugar_nac_n2_lat'] = '-'
                persons_interviewed_df.at[row.Index, 'lugar_nac_n2_lon'] = '-'
        # Geocode residence location if not present
        if row.lugar_residencia_n3_lat is None:
            # Concatenate residence location names, beware that either level 2 (n2) or level 3 (n3) locations might
            # be none and thus the geocoded location becomes less accurate
            residence_location_address = ', '.join(filter(lambda l: '' if l is None or l == '[Internacional]' else l,
                                                          [row.lugar_residencia_n3_txt, row.lugar_residencia_n2_txt,
                                                           row.lugar_residencia_n1_txt]))
            # Geocode residence location, beware it can throw an error if Google Geocoding quota of 50 QPS is exceeded
            try:
                residence_location = geo_locator.geocode(residence_location_address)
                # print(row_idx, 'residence', residence_location_address, residence_location)
                persons_interviewed_df.at[row.Index, 'lugar_residencia_n3_lat'] = residence_location.latitude
                persons_interviewed_df.at[row.Index, 'lugar_residencia_n3_lon'] = residence_location.longitude
            except GeocoderServiceError as e:
                print(f"Error: geocode failed on input {residence_location_address} with error {e}")
                persons_interviewed_df.at[row.Index, 'lugar_residencia_n3_lat'] = '-'
                persons_interviewed_df.at[row.Index, 'lugar_residencia_n3_lon'] = '-'
        bar.update(row_idx)
    bar.update(row_count)

    print("  Done")

    print("- Exporting data TSV formatted file")

    compression_opts = dict(method='zip', archive_name='persons_interviewed.tsv')
    persons_interviewed_df.to_csv('persons_interviewed.zip', index=False, sep='\t', compression=compression_opts)

    print("  Done")


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
