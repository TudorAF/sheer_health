import logging
import ipdb
from eligibility import EligibilityRecord, read_input

logging.basicConfig(filename='errors.log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR)


def main(file_path):
    # lines = [EligibilityRecord.OUTPUT_HEADERS]
    try: 
        with open('output.txt', 'w') as output:
            output.write(EligibilityRecord.OUTPUT_HEADERS)
            for record in read_input(file_path):
                eligibility_record = EligibilityRecord(record)
                logging.info(f"Processing benefit eligibility record for {eligibility_record.subscriber_key}")
                # lines += eligibility_record.output_lines
                output.writelines(eligibility_record.output_lines)

    except KeyError as e:
        logging.error(str(e))
        next # skip this record and continue




if __name__ == "__main__":
    main('data/input.ndjson.b64')
