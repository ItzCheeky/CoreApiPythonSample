import json
class EmployeeModel:
    firstName = None
    lastName = None
    dateHired = None
    status = None
    
    def __init__(self, jsonData = '{}') :
        self.__dict__ = json.loads(jsonData)