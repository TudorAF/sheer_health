# Eligibility Policy Processor

## Setup

To get started, follow these steps:
**Note: output.txt file is already included in this file you don't have to do this to view the output**

1. Clone the repository to your local machine.
2. Create a virtual environment using Python's venv module: `python -m venv venv`.
3. Install the required dependencies using the provided `requirements.txt` file: `pip install -r requirements.txt`.
4. Ensure everything is working correctly by running the test suite with `pytest main_test.py`.
5. Finally, execute the main program `python main.py` to generate the output file.

- You can view the output in the `output.txt` file
- Some records are malformed or the response is an error response. You can see them in the `errors.log` file

## Data Processing

### Determining Eligibility

The first step is to determine the eligibility of each policy. This is accomplished by analyzing the policy dates and checking if the current date falls within the policy's active coverage period. If the policy is still in effect and eligible for claims, it is marked as eligible for further processing.

### Parsing Benefits Information

The program parses the complex `benefitsInformation` from the response using a Python data class. This data class helps standardize the schema, making it easier to map the various benefit types and details. The parsed data is then sorted into a nested dictionary structure based on `service_type_code`, allowing quick and efficient lookup of benefits associated with each code.

For example, to access individual deductible information for service type code "30," the program can retrieve it using `benefits["30"]["Individual"]["Deductible"]`. The result will be a summary including coverage level, actual benefit amount, benefit reimbursement type, time qualifier, and in-network status.

## Potential Improvements

While the current program functions effectively, there are several areas that could be enhanced with additional development time:

1. **Test Coverage**: Adding more tests, particularly for parsing plan start dates, to ensure the program's reliability and accuracy.
2. **Refined Abstractions**: Creating a base class for the `Benefits` data class and specialized subclasses for different benefit types (e.g., deductible, co-pay). This would lead to a more elegant and maintainable design.
3. **Insurance Company Data**: Incorporating support for distinguishing between various insurance companies and their policies, providing a more comprehensive view of policyholders' coverage.
4. **Custom Exception Handling**: Implementing custom exceptions to handle errors gracefully, making the program more robust and user-friendly.
5. **Dependents Support**: If applicable, adding support for processing benefits information for policyholders' dependents, enabling a comprehensive analysis of family coverage.

By incorporating these improvements, the program's overall functionality, code quality, and usability can be significantly enhanced, making it a more valuable tool for insurance data processing.
