import React, { Component } from 'react'

import "../../css/bootstrap.min.css"
import "../../css/Navbar.css"

export default class Navbar extends Component 
{
    state = {
        brand : this.props.brand
    }

    render() 
    {
        return (
            <nav className="navbar navbar-expand navbar-dark bg-dark">
                <div className="container-fluid">
                    <a className="navbar-brand" href="Home">{this.state.brand}</a>

                    <div className="collapse navbar-collapse" id="navbarResponsive">
                        <ul className="navbar-nav ml-auto">
                            <li className='nav-item'><a className='nav-link' href='Home'>Home</a></li>
                            <li className='nav-item'><a className='nav-link' href='Image'>Image</a></li>
                            <li className='nav-item'><a className='nav-link' href='watch'>Video</a></li>
                        </ul>
                    </div>
                    
                    <ul className="navbar-nav float-right">
                        <li className='nav-item'><a className='nav-link' href='login'>Login</a></li>
                        <li className='nav-item'><a className='nav-link' href='RegisterPage'>Register</a></li>
                    </ul>
                </div>
            </nav>
        )
    }
}
