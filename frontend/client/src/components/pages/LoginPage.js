import React from 'react'

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


export default function LoginPage(props)
{
    let { cookies } = props;

    if(cookies.get("access_token"))
    {
        window.location.href = "/";
        return null;
    }

    const username = React.useRef("");
    const password = React.useRef("");
    
    const nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    }


    async function loginUser(e)
    {
        // prevents the form from submitting 
        e.preventDefault();

        // make form data
        let data = new FormData();
        data.append("username", username.current.value);
        data.append("password", password.current.value);
        
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

            if (request.status != 200)
                return; 

            if (!response.access_token)
                return;
            
            cookies.set("user", {
                username : response.username,
                user_id  : response.user_id
            });
            cookies.set("access_token", response.access_token);
            cookies.set("token_type", response.token_type);
            window.location.href = "/login";
        };
    }

        
    return (
        <div className="apply-font">
            <Navbar {...nprops}></Navbar>

            <div className="content">

                <form>

                    <div className='row'>
                        <input type="text"     
                            id="login-username" 
                            placeholder="username"
                            required=""
                            maxLength={MAX_USERNAME_LENGTH}
                            minLength={MIN_USERNAME_LENGTH}
                            ref={username}></input>
                    </div>

                    <div className='row'>
                        <input type="password" 
                            id="login-password" 
                            placeholder="password"
                            required=""
                            maxLength={MAX_PASSWORD_LENGTH}
                            minLength={MIN_PASSWORD_LENGTH}
                            ref={password}></input>
                    </div>

                    <div className='row'>
                        <button id="pink-button"
                                onClick={loginUser}>Login</button>
                    </div>

                    <div>
                        <span className="under-text" >Don't have an account?</span>
                        <a href="register" className='link-bold-lite'> Register</a>
                    </div>
                </form>

            </div>
        </div>
    )
}
