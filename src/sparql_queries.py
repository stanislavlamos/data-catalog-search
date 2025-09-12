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
