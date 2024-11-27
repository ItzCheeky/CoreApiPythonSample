from models.AuthResponseModel import AuthResponseModel
from models.HttpHeaderModel import HttpHeaderModel
from models.HttpResponseModel import HttpResponseModel
from models.EmployeeModel import EmployeeModel
from shared.APIHelper import APIHelper
from shared.GeneralMethods import GeneralMethods
from business.AuthManager import AuthManager
import json
import pickle

class EmployeeManager(object):

    authResponse: None
    httpResponse: None
    httpHeader: None
    authManager: None

    def __init__(self):
        try:

            EmployeeManager.authResponse = AuthResponseModel()
            EmployeeManager.httpResponse = HttpResponseModel()
            EmployeeManager.httpHeader = HttpHeaderModel()
            EmployeeManager.authManager = AuthManager()

            if AuthManager.GetAuthResponse() != None :
                EmployeeManager.authResponse = AuthManager.GetAuthResponse()
                EmployeeManager.httpHeader.authorization = 'Bearer ' + EmployeeManager.authResponse.access_token
        except Exception:
            raise        

    @classmethod
    def GetList(self):
        allEmployees = []
        page = 0

        try:
            if EmployeeManager.httpResponse.header_code == 401 : # UnAuthorised
                EmployeeManager.authResponse = EmployeeManager.authManager.ReAuthorize()
                if EmployeeManager.authResponse != None :
                    EmployeeManager.httpHeader.authorization = "Bearer "+ EmployeeManager.authResponse.access_token
                return EmployeeManager.GetList()
            

            elif EmployeeManager.httpResponse.header_code == 200 : # Success
               
                while True:
            
                    EmployeeManager.httpResponse = APIHelper.Get(f"{EmployeeManager.authResponse.endpoint}/employee?page={page}&limit=1000&orderby=lastName&fields=firstName,lastName,dateHired,status",EmployeeManager.httpHeader)
                    employeeListDict = json.loads(EmployeeManager.httpResponse.response.content)

                    allEmployees.extend(employeeListDict)

                    if len(employeeListDict) < 1000:
                        break

                    page += 1
                    
                    activeEmployees = [employee for employee in allEmployees if employee.get("status") == 1]
                    # print(json.dumps(employeeListDict, indent=4))
                return activeEmployees
                
            else :
                raise Exception(EmployeeManager.httpResponse.response.content)
        except Exception:
            raise

    @classmethod
    def Get(self, id):
        try:
            EmployeeManager.httpResponse = APIHelper.Get(EmployeeManager.authResponse.endpoint + '/employee/' + id +'/budget/', EmployeeManager.httpHeader)

            if EmployeeManager.httpResponse.header_code == 401 : # UnAuthorised
                EmployeeManager.authResponse = EmployeeManager.authManager.ReAuthorize()
                if EmployeeManager.authResponse != None :
                    EmployeeManager.httpHeader.authorization = "Bearer "+ EmployeeManager.authResponse.access_token
                    return EmployeeManager.Get(id)
            elif EmployeeManager.httpResponse.header_code == 200 : # Success
                employee = EmployeeModel(EmployeeManager.httpResponse.body)
                return employee    
            else :
                raise Exception(EmployeeManager.httpResponse.response.content)      
        except Exception:
            raise

   