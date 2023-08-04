import json
import base64 
from datetime import datetime
from decimal import Decimal
import logging
from dataclasses import dataclass

@dataclass
class Benefit:
    ''' holds 1 record for benefitsInformation  '''   
    
    def __init__(self, benefit):
        self.benefit = benefit
        self.code = benefit.get('code')
        # name one of:  Deductible Active Coverage Co-Payment , co-insurance, Out of Pocket (Stop Loss), Active Coverage
        self.name = benefit.get('name', 'unknown')
        self.coverage_level_code = benefit.get('coverageLevelCode') 
        self.coverage_level = benefit.get('coverageLevel') # individual or family
        self.in_network = True if benefit.get('inPlanNetworkIndicatorCode') == 'Y' else False

        self.service_type_codes = benefit.get('serviceTypeCodes')
        self.service_types = benefit.get('serviceTypes')
        self.service_map = dict(zip(self.service_type_codes, self.service_types))

        # types of reimbursment either percentage or absolute number 
        # and defined by a time quilifier
        if benefit.get('benefitAmount'):
            self.benefit_reimbursement_type = 'Amount'
            self.actual_benefit = Decimal(benefit.get('benefitAmount'))
        elif benefit.get('benefitPercent'):
            self.benefit_reimbursement_type = 'Percent'
            self.actual_benefit = Decimal(benefit.get('benefitPercent'))
        elif benefit['name'] == 'Active Coverage':
            self.benefit_reimbursement_type = 'coverage'
            self.actual_benefit = True # can't find "inactive coverage"
        else:
            self.benefit_reimbursement_type = None
            self.actual_benefit = None        

        self.time_qualifier = benefit.get('timeQualifier')

    
    def summary(self):
        return {   'coverage_level': self.coverage_level,
            'actual_benefit': self.actual_benefit,
            'benefit_reimbursement_type': self.benefit_reimbursement_type,
            'time_qualifier': self.time_qualifier,
            'in_network': self.in_network
                }

class EligibilityRecord:
    ''' this class parses dates and determines if a plan is eligible. 
    It also parses the benefitsInformation and returns a dictionary of benefits
    { service_type_code: { coverage_level: { benefit_name: { benefit_summary } } }
    '''
    OUTPUT_HEADERS = "Subscriber Key|is_eligible|Service Type Code|Service Type|Benefit Name|Time Qualifier|Coverage Level|In Network|Benefit Reimbursement Type|Actual Benefit\n"
    def __init__(self, eligibility_record):
        if eligibility_record.get('errors'):
            # TODO raise a custom exception here
            raise KeyError(f"Error in eligibility record: {eligibility_record.get('errors')}")

        self.eligibility_record = eligibility_record
        self.subscriber_key = EligibilityRecord.build_key(eligibility_record['subscriber'])

        # TODO: add dependant support but no example JSON has any
        # self.dependant_keys = None
        self.benefits = {}
        self.service_type_code_map = {}
        self.benefits = {}
        self.output_lines = []

        logging.info(f"Processing benefit eligibility record for {self.subscriber_key}")
        try:
            for benefit in self.eligibility_record['benefitsInformation']:
                logging.info(f"Adding benefit {benefit} to parsed benefits")
                benefit = Benefit(benefit)
                self.service_type_code_map.update(benefit.service_map)

                for code in benefit.service_type_codes:
                    # Retrieve the existing parsed benefit for the code, or create an empty dictionary
                    existing_benefit = self.benefits.get(code, {})

                    # Retrieve the existing parsed benefit for the coverage level, or create an empty dictionary
                    coverage_level_benefit = existing_benefit.get(benefit.coverage_level, {})

                    # If the benefit name already exists, update its summary, otherwise add the new benefit
                    coverage_level_benefit[benefit.name] = coverage_level_benefit.get(benefit.name, {})
                    coverage_level_benefit[benefit.name].update(benefit.summary())


                    # Update the coverage level benefits for the code
                    existing_benefit[benefit.coverage_level] = coverage_level_benefit

                    self.output_lines.append(f"{self.subscriber_key}|{self.is_eligible()}|{code}|{benefit.service_map[code]}|{benefit.name}|{benefit.time_qualifier}|{benefit.coverage_level}|{benefit.in_network}|{benefit.benefit_reimbursement_type}|{benefit.actual_benefit}\n")

                    # Update the parsed benefits for the code
                    self.benefits[code] = existing_benefit
        except TypeError as e:
            logging.error(f"Type Error, an expected key might be missing when parsing benefits with values'{benefit}', {type(benefit)}")
            next

    def plan_start_date(self):
        '''
         some example json: 
             "planDateInformation": { "planBegin": "20230101-20231231" },
         OR 
          "planDateInformation": { "planBegin": "20221101" },
         OR nothing 
        '''
        try:
            return datetime.strptime(self.eligibility_record['planDateInformation']['planBegin'].split('-')[0],'%Y%m%d')
        except (IndexError, ValueError) as e:
            logging.info(f"No plan start date found with {self.eligibility_record.get('planDateInformation')}")
            return None
    
    def plan_end_date(self):
        try:
            return datetime.strptime(self.eligibility_record['planDateInformation']['planBegin'].split('-')[1],'%Y%m%d')
        except (IndexError, ValueError) as e:
            logging.info(f"No plan end date found with {self.eligibility_record.get('planDateInformation')}")
            return None

    def build_key(subscriber):
        return f"{subscriber['firstName']}{subscriber['lastName']}{subscriber['dateOfBirth']}"
    
    def is_eligible(self):
        ''' determines if eligibility record is eligible based on if a today is between plan start and end dates '''
        if self.plan_start_date() > datetime.now():
            logging.info(f'Plan start date is in the future {self.plan_start_date()}')
            return False
        elif self.plan_start_date() < datetime.now() and self.plan_end_date() == None:
            logging.info(f'Plan started: {self.plan_start_date()}. Plan is in effect with no end date')
            return True
        elif self.plan_start_date() < datetime.now() < self.plan_end_date():
            logging.info(f'Plan started: {self.plan_start_date()} and is effective until Plan end on {self.plan_end_date()}')
            return True
        elif self.plan_end_date() < datetime.now():
            logging.info(f'plan ended on {self.plan_end_date()}')
            return False
        else: 
            logging.error('default case reached, plan is ineligible')
            return False



def read_input(file):
    """ File takes an ndjson.b64 file and returns a list of dictionaries """

    logging.info(f"Reading file {file}")
    with open(file, 'r') as f:
        # this first decodes file into bytes then decodes into a string 
        # we split the string according to the new line character and parse and 
        # return a dictionary for each line
        decoded_data = base64.b64decode(f.read()).decode('utf-8').split("\n")
        
        for record in decoded_data:
            try: 
                yield json.loads(record)
            except json.decoder.JSONDecodeError as e:
                if record == '':
                    continue
                else:
                    logging.error(f"could not parse record from base64 encoded file'{record}', {type(record)}")
                    continue

