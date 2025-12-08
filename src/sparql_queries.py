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


get_dataset_distributions_nkod_remote = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct:  <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?distribution ?title ?format ?downloadURL ?accessURL ?conformsTo
    WHERE {{
      {dataset_uri} dcat:distribution ?distribution .
    
      OPTIONAL {{ ?distribution dct:title ?title . }}
      OPTIONAL {{ ?distribution dct:format ?format . }}
      OPTIONAL {{ ?distribution dcat:downloadURL ?downloadURL . }}
      OPTIONAL {{ ?distribution dcat:accessURL ?accessURL . }}
      OPTIONAL {{ ?distribution dct:conformsTo ?conformsTo . }}
    }}
"""


get_dataset_timeframe_and_publisher_nkod_remote = """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dct:  <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?agent ?agentNameCS ?agentNameEN ?startDate ?endDate
    WHERE {{
      BIND(<{dataset_uri}> AS ?dataset)
    
      ?dataset dct:publisher ?agent .
      ?agent a foaf:Agent .
    
      OPTIONAL {{ ?agent foaf:name ?agentNameCS FILTER (lang(?agentNameCS) = "cs") }}
      OPTIONAL {{ ?agent foaf:name ?agentNameEN FILTER (lang(?agentNameEN) = "en") }}
    
      OPTIONAL {{
        ?dataset dct:temporal ?temporal .
        OPTIONAL {{ ?temporal dcat:startDate ?startDate . }}
        OPTIONAL {{ ?temporal dcat:endDate ?endDate . }}
      }}
    }}
"""


get_dataset_publisher_nkod_remote = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?dataset ?prop ?value ?lang
WHERE {
  ?dataset a dcat:Dataset .
  ?dataset dct:publisher ?publisher .

  OPTIONAL {
    ?publisher foaf:name ?name .
    BIND("publisher_name" AS ?prop)
    BIND(?name AS ?value)
    BIND(LANG(?name) AS ?lang)
    FILTER(?lang = "cs" || ?lang = "en" || ?lang = "")
  }

  BIND("publisher_uri" AS ?prop)
  BIND(?publisher AS ?value)
  BIND("" AS ?lang)
}
"""


get_publisher_by_dataset_nkod_remote = """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?publisher (STR(?name_cs_raw) AS ?name_cs) (STR(?name_en_raw) AS ?name_en)
WHERE {{
  <{dataset_uri}> dct:publisher ?publisher .

  OPTIONAL {{
    ?publisher foaf:name ?name_cs_raw .
    FILTER(LANG(?name_cs_raw) = "cs" || LANG(?name_cs_raw) = "")
  }}

  OPTIONAL {{
    ?publisher foaf:name ?name_en_raw .
    FILTER(LANG(?name_en_raw) = "en")
  }}
}}
"""


nkod_remote_get_publisher_all = """
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>

SELECT DISTINCT ?dataset_uri ?publisher (STR(?name_cs_raw) AS ?name_cs) (STR(?name_en_raw) AS ?name_en)
WHERE {
    ?dataset_uri a dcat:Dataset .

    ?dataset_uri dct:publisher ?publisher .

    OPTIONAL {
        ?publisher foaf:name ?name_cs_raw .
        FILTER(LANG(?name_cs_raw) = "cs" || LANG(?name_cs_raw) = "")
    }

    OPTIONAL {
        ?publisher foaf:name ?name_en_raw .
        FILTER(LANG(?name_en_raw) = "en")
    }
}
"""


nkod_local_graphdb_get_publisher_all = """
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?dataset ?publisher ?name ?lang
WHERE {
  ?dataset a dcat:Dataset ;
           dct:publisher ?publisher .

  OPTIONAL {
    ?publisher foaf:name ?name .
    BIND(LANG(?name) AS ?lang)
    FILTER(?lang IN ("cs","en",""))
  }
}
"""


get_classes_nkod_local = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?cls ?com
WHERE {
    ?instance a ?cls .
    OPTIONAL { ?cls rdfs:comment ?com }
}
"""


get_relationships_nkod_local = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?rel ?com
WHERE {
    ?subj ?rel ?obj . 
    OPTIONAL { ?rel rdfs:comment ?com }
}
"""


get_all_distributions_and_formats_nkod_remote = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT ?dataset ?distribution ?format
WHERE {
  ?dataset a dcat:Dataset .
  OPTIONAL {
    ?dataset dcat:distribution ?distribution .
    ?distribution dct:format ?format .
  }
}
"""


get_class_properties_nkod_remote = """
SELECT DISTINCT ?p WHERE {
  ?instance a ?cls .
  ?cls ?p ?com .
}
"""


get_all_distributions_nkod_remote = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?dataset ?distribution ?title ?format ?downloadURL ?accessURL ?conformsTo
WHERE {
  ?dataset a dcat:Dataset ;
           dcat:distribution ?distribution .

  OPTIONAL { ?distribution dct:title ?title . }
  OPTIONAL { ?distribution dct:format ?format . }
  OPTIONAL { ?distribution dcat:downloadURL ?downloadURL . }
  OPTIONAL { ?distribution dcat:accessURL ?accessURL . }
  OPTIONAL { ?distribution dct:conformsTo ?conformsTo . }
}
"""


drop_named_graphs_graphdb = """
DROP NAMED
"""


get_distinct_named_graphs_graphdb = """
SELECT DISTINCT ?g
WHERE {
  GRAPH ?g {
    ?s ?p ?o
  }
}
"""

get_all_timeframes_graphdb = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct:  <http://purl.org/dc/terms/>

SELECT ?dataset ?startDate ?endDate
FROM <http://example.org/nkod-trig-graph>
WHERE {
  ?dataset a dcat:Dataset .

  OPTIONAL {
    # The temporal node is always: datasetURI + "/časové-pokrytí"
    BIND( IRI(CONCAT(STR(?dataset), "/časové-pokrytí")) AS ?temporal )

    ?temporal a dct:PeriodOfTime .

    OPTIONAL { ?temporal dcat:startDate ?startDate . }
    OPTIONAL { ?temporal dcat:endDate   ?endDate . }
  }
}
"""
