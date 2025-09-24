get_catalogs_metadata_nkod_remote = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct: <http://purl.org/dc/terms/>

    SELECT ?dataset ?prop ?value ?lang WHERE {
      ?dataset a dcat:Dataset .
      {
        ?dataset dcat:keyword ?value .
        BIND("keyword" AS ?prop)
      }
      UNION
      {
        ?dataset dct:title ?value .
        BIND("title" AS ?prop)
      }
      UNION
      {
        ?dataset dct:description ?value .
        BIND("description" AS ?prop)
      }
      BIND(LANG(?value) AS ?lang)
      FILTER(?lang = "cs" || ?lang = "en")
    }
"""


get_catalogs_metadata_and_themes_nkod_remote = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct: <http://purl.org/dc/terms/>

    SELECT ?dataset ?prop ?value ?lang WHERE {
      ?dataset a dcat:Dataset .
      {
        ?dataset dcat:keyword ?value .
        BIND("keyword" AS ?prop)
        BIND(LANG(?value) AS ?lang)
        FILTER(?lang = "cs" || ?lang = "en")
      }
      UNION
      {
        ?dataset dct:title ?value .
        BIND("title" AS ?prop)
        BIND(LANG(?value) AS ?lang)
        FILTER(?lang = "cs" || ?lang = "en")
      }
      UNION
      {
        ?dataset dct:description ?value .
        BIND("description" AS ?prop)
        BIND(LANG(?value) AS ?lang)
        FILTER(?lang = "cs" || ?lang = "en")
      }
      UNION
      {
        ?dataset dcat:theme ?theme .
        BIND("themes" AS ?prop)
        BIND(STRAFTER(STR(?theme), "data-theme/") AS ?value)
        BIND("" AS ?lang)
        FILTER(STRLEN(?value) > 0)
      }
    }
"""


get_all_dcat_themes_nkod_remote = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT DISTINCT 
           ?themeName
           (STR(?themeLabelCz) AS ?themeLabelCzStr)
           (STR(?themeLabelEn) AS ?themeLabelEnStr)
           (STR(?themeDefinitionCz) AS ?themeDefinitionCzStr)
           (STR(?themeDefinitionEn) AS ?themeDefinitionEnStr)
    WHERE {
      ?dataset dcat:theme ?theme .
      
      FILTER(isIRI(?theme) && CONTAINS(STR(?theme), "data-theme/"))
      
      BIND(STRAFTER(STR(?theme), "data-theme/") AS ?themeName)
      FILTER(STR(?themeName) != "undefined")
      
      OPTIONAL {
        ?theme skos:prefLabel ?themeLabelCz .
        FILTER(LANG(?themeLabelCz) = "cs")
      }
      OPTIONAL {
        ?theme skos:prefLabel ?themeLabelEn .
        FILTER(LANG(?themeLabelEn) = "en")
      }
      
      OPTIONAL {
        ?theme skos:definition ?themeDefinitionCz .
        FILTER(LANG(?themeDefinitionCz) = "cs")
      }
      OPTIONAL {
        ?theme skos:definition ?themeDefinitionEn .
        FILTER(LANG(?themeDefinitionEn) = "en")
      }
    }
"""

