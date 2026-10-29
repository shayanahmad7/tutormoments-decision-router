"""Canonical OpenAI wrapper for the publisher's facet-array output.

The original Claude scorer can return a bare JSON array. JSON-object mode on
OpenAI can put a real action in a dictionary key; the publisher compatibility
parser then keeps only list values and loses that action. A strict one-key
wrapper preserves every facet while retaining the publisher prompt text.
"""
import json
FACETS_RESPONSE_FORMAT={"type":"json_schema","json_schema":{"name":"pedagogical_facets","strict":True,"schema":{"type":"object","properties":{"facets":{"type":"array","items":{"type":"string"}}},"required":["facets"],"additionalProperties":False}}}

def parse_strict_facets(text):
    value=json.loads(text)
    if not isinstance(value,dict) or set(value)!={"facets"}:
        raise ValueError("Expected the canonical facets wrapper")
    facets=value["facets"]
    if not isinstance(facets,list) or any(not isinstance(x,str) or not x.strip() for x in facets):
        raise ValueError("Facets must be nonempty strings or an empty list")
    return facets
