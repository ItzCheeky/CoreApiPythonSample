from flask import Flask, render_template, json, request, redirect
from shared.GeneralMethods import GeneralMethods
from shared.APIHelper import APIHelper
from models.HttpHeaderModel import HttpHeaderModel
from models.HttpResponseModel import HttpResponseModel
from models.AuthResponseModel import AuthResponseModel
from models.EmployeeModel import EmployeeModel
from models.JWTModel import JWTModel
from business.AuthManager import AuthManager
from business.UserInfoManager import UserInfoManager
from business.EmployeeManager import EmployeeManager
from business.JWTManager import JWTManager
import sys

app = Flask(__name__,template_folder='views')
app.secret_key = GeneralMethods.GenerateRandomString()
app.config['SESSION_TYPE'] = 'filesystem'
@app.route("/")
def main():
    config = GeneralMethods.GetConfig()

    authManager = AuthManager()
    authResponse = AuthResponseModel()
    jwt = JWTModel()

    # Authenticate (Code Exchange)
    if request.args.get('code') != None :
        # verfiy that the state parameter returned by the server is the same that was sent earlier.
        if authManager.IsValidState(request.args.get('state')) :
            authResponse = authManager.Authorize(request.args.get('code'))
            jwtManager = JWTManager(config, authResponse.id_token)
            # Decode id_token (JWT) 
            jwt = jwtManager.DecodeJWT()
            if jwtManager.ValidateJWT(jwt) :    
                authManager.SaveAuthResponse(authResponse)
            else :
                raise Exception("Invalid JWT.")
        else :
            raise Exception('State Parameter returned doesn\'t match to the one sent to Core API Server.')

    # Load Activity List
    if authManager.GetAuthResponse() != None :
        # Get the user Info
        userInfoManager = UserInfoManager()
        userInfo = userInfoManager.GetUserInfo()

        # Get Employeee List
        employeeManager = EmployeeManager()
        activeEmployeeList = employeeManager.GetList()

        return render_template('ActivityListView.html', userInfo = userInfo, employeeList = activeEmployeeList)
    else :
        return render_template('index.html')
    
    

@app.route('/connectToCore', methods=['POST'])
def connectToCore():
    try:
        authManager = AuthManager()
        coreUrl = authManager.ConnectToCore()
        return redirect(coreUrl)
    except:
        return '<div style=\'color:red\'>' + str(sys.exc_info()[1]) + '</div>'

@app.route('/disconnectFromCore', methods=['POST'])
def disconnectFromCore():
    try:
        authManager = AuthManager()
        homeUrl = authManager.DisconnectFromCore()
        return redirect(homeUrl)
    except:
        return '<div style=\'color:red\'>' + str(sys.exc_info()[1]) + '</div>'



if __name__ == "__main__":
    app.run()