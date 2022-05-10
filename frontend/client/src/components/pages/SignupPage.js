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


export default function RegisterPage(props)
{
    const { cookies } = props;

    const username = React.useRef("");
    const password = React.useRef("");
    
    const nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    }

    async function registerUser(e)
    {
        // prevents the form from submitting 
        e.preventDefault();

        // make form data
        let data = new FormData();
        data.append("username", username.current.value);
        data.append("password", password.current.value);
        
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

            window.location.href = "/";
        };
    }


    return (
        <div className="apply-font">
            <Navbar {...nprops}></Navbar>

                <div className="content">

                    <form className='align-center'>

                        <div className='row'>
                            <input type="text"     
                                id="signup-username" 
                                placeholder="username"
                                required=""
                                maxLength={MAX_USERNAME_LENGTH}
                                minLength={MIN_USERNAME_LENGTH}
                                ref={username}></input>
                        </div>

                        <div className='row'>
                            <input type="password" 
                                id="signup-password" 
                                placeholder="password"
                                required=""
                                maxLength={MAX_PASSWORD_LENGTH}
                                minLength={MIN_PASSWORD_LENGTH}
                                ref={password}></input>
                        </div>

                        <div className='row'>
                            <button id="pink-button"
                                onClick={registerUser}>Register</button>
                        </div>

                        <div>
                            <span className="under-text" >Already have an account?</span>
                            <a href="login" className='link-bold-lite'> Login</a>
                        </div>
                    </form>

            </div>
        </div>
    )
}
