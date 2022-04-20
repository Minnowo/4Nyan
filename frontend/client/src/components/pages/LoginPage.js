import React, { Component } from 'react'

import Navbar from '../elements/Navbar'

import "../../css/bootstrap.min.css"
import "../../css/global.css"

import API_ENDPOINTS from '../../constant'

export default class LoginPage extends Component 
{
    state = {
        username : "",
        password : ""
    };

    handleInputChange = (e) => 
    {
        // is this really how you're supposed to do this??? 
        switch(e.target.id)
        {
          case "login-username":
            this.setState({username : e.target.value});
            break;
    
          case "login-password":
            this.setState({password : e.target.value});
            break;
        }
      }

    loginUser = async (e) => 
    {
        // prevents the form from submitting 
        e.preventDefault();

        // make form data
        let data = new FormData();
        data.append("username", this.state.username);
        data.append("password", this.state.password);
        
        // create a new http POST request 
        let request = new XMLHttpRequest();
        request.open('POST', API_ENDPOINTS.backend_ref + API_ENDPOINTS.login, true);
        
        // send the data
        request.send(data);

        // on request goes through, handle the resposne
        request.onload = function () 
        {
            let response = JSON.parse(request.response);

            console.log(response);
        };
    }

    render() 
    {
        let nprops = {
                brand : "~4Nyan~"
            }

        return (
            <div className="apply-font" style={{color: "#fff"}}>
                <Navbar {...nprops}></Navbar>

                <form id="login-form">
                    <input type="text" id="login-username" onChange={this.handleInputChange}></input>
                    <input type="password" id="login-password" onChange={this.handleInputChange}></input>
                    <button onClick={this.loginUser}>Login</button>
                </form>
            </div>
        )
    }
}
