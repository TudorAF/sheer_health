import pytest
import json
from .eligibility import EligibilityRecord
def read_file_helper(file):
    with(open(file, 'r')) as f:
        return f.read()


# A few simple test cases 
# TODO add test for build_key , plan date parsing 
def test_error_json():
    # read error_response.json
    # assert that the error_response.json raises an exception
    response = read_file_helper('data/error_response.json')
    # assert error is raised
    with pytest.raises(KeyError) as exc_info:
        EligibilityRecord(json.loads(response))

    print(str(exc_info.value))
    assert exc_info.type == KeyError
    assert 'Error in eligibility record:' in str(exc_info.value)


def test_happy_path():
    response = read_file_helper('data/happy_path.json')
    eligibility_record = EligibilityRecord(json.loads(response))

    assert len(eligibility_record.benefits) == 1
    print(eligibility_record.benefits)
    assert eligibility_record.benefits == {'30': {'Individual': {'Active Coverage': {'coverage_level': 'Individual', 'actual_benefit': True, 'benefit_reimbursement_type': 'coverage', 'time_qualifier': None, 'in_network': False}}}}
    assert eligibility_record.is_eligible() == True

def test_unhappy_path():
    response = read_file_helper('data/unhappy_path.json')
    eligibility_record = EligibilityRecord(json.loads(response))
    # test to ensure that malformed benefits info doesn't break the entire record 
    assert len(eligibility_record.benefits) == 0
    assert eligibility_record.is_eligible() == True
