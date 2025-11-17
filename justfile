# e.g. just comephores 202509
comephores month:
    curl -fL https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/REANALYSES/COMEPHORE/H_COMEPHORE_{{month}}.tar --output-dir services/weather-data -O
    tar -xvf services/weather-data/*.tar -C services/weather-data/comephores/ --wildcards "*_ERR.gtif" --strip-components=1 
    rm -f services/weather-data/*.tar
    
