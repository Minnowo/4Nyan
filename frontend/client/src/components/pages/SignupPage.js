import React, { Component } from 'react'

import Navbar from '../elements/Navbar'

import "../../css/LoginRegister.css"

import "../../css/bootstrap.min.css"
import "../../css/global.css"

import API_ENDPOINTS from '../../constant'
import { 
    MAX_USERNAME_LENGTH, 
    MIN_USERNAME_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH
        } from '../../constant'

export default class SIgnupPage extends Component 
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
          case "signup-username":
            this.setState({username : e.target.value});
            break;
    
          case "signup-password":
            this.setState({password : e.target.value});
            break;
        }
      }

    registerUser = async (e) => 
    {
        // prevents the form from submitting 
        e.preventDefault();

        // make form data
        let data = new FormData();
        data.append("username", this.state.username);
        data.append("password", this.state.password);
        
        // create a new http POST request 
        let request = new XMLHttpRequest();
        request.open('POST', API_ENDPOINTS.backend_ref + API_ENDPOINTS.register, true);
        
        // send the data
        request.send(data);

        // on request goes through, handle the resposne
        request.onload = function () 
        {
            let response = JSON.parse(request.response);

            console.log(response);

            if(request.status != 200)
                return;

            if (!response.user_id)
                return;
                
            console.log("user created");
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

                    <div className="content">

                        <form>

                            <div className='row'>
                                <input type="text"     
                                    id="signup-username" 
                                    placeholder="username"
                                    required=""
                                    maxLength={MAX_USERNAME_LENGTH}
                                    minLength={MIN_USERNAME_LENGTH}
                                    onChange={this.handleInputChange}></input>
                            </div>

                            <div className='row'>
                                <input type="password" 
                                    id="signup-password" 
                                    placeholder="password"
                                    required=""
                                    maxLength={MAX_PASSWORD_LENGTH}
                                    minLength={MIN_PASSWORD_LENGTH}
                                    onChange={this.handleInputChange}></input>
                            </div>

                            <div className='row'>
                                <button id="register-button"
                                    onClick={this.registerUser}><strong>Register</strong></button>
                            </div>

                            <div>
                                Already have an account?
                                <a href="login" className='link-bold'> Login</a>
                            </div>
                        </form>

                </div>
            </div>
        )
    }
}
