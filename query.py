from urlparse import urlparse

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://138.4.249.224:8890/sparql")

attr_uri_dict = {
    "color": "color",
    "covered": "proteccion",
    "height": "altura",
    "lamp": "tieneTipoDeLampara",
    "light": "luz",
    "status": "estado",
    "wattage": "potencia",
    "heading": "heading",
    "pitch": "pitch"
}


def query(furi, attr):
    if attr not in attr_uri_dict:
        return None
    q = """
        PREFIX ap: <http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/alumbrado-publico#>
        SELECT ?v FROM <http://farolas.linkeddata.es/resource/all>
        WHERE { <%s> ap:%s ?v }
    """ % (furi, attr_uri_dict.get(attr))

    sparql.setQuery(q)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        v = result["v"]["value"]
        try:
            if v.startswith('http'):
                return urlparse(v).path.split('/')[-1]
            return v.lstrip('"').rstrip('"')
        except Exception as e:
            pass
    return None
