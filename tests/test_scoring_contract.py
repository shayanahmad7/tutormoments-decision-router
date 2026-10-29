import unittest
from tm_router.scoring_contract import parse_strict_facets,FACETS_RESPONSE_FORMAT
from tm_router import publisher_protocol as p
class ScoringContractTests(unittest.TestCase):
 def test_real_loss_case_is_prevented(self):
  legacy='{"The tutor asks the student to explain their thinking.":["The tutor breaks the task into parts."]}'
  self.assertNotIn('The tutor asks the student to explain their thinking.',p.parse_facets(legacy))
  with self.assertRaises(ValueError):parse_strict_facets(legacy)
  canonical='{"facets":["The tutor asks the student to explain their thinking.","The tutor breaks the task into parts."]}'
  self.assertEqual(parse_strict_facets(canonical),p.parse_facets(canonical))
  self.assertEqual(len(parse_strict_facets(canonical)),2)
 def test_empty_is_distinct_from_parse_failure(self):
  self.assertEqual(parse_strict_facets('{"facets":[]}'),[])
  for bad in ['{}','{"facets":[""]}','{"facets":null}','{"other":[]}']:
   with self.assertRaises(ValueError):parse_strict_facets(bad)
 def test_producer_has_one_required_array(self):
  s=FACETS_RESPONSE_FORMAT['json_schema']['schema']
  self.assertEqual(s['required'],['facets']);self.assertFalse(s['additionalProperties']);self.assertTrue(FACETS_RESPONSE_FORMAT['json_schema']['strict'])
