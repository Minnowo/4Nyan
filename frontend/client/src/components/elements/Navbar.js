import React from 'react'

import "../../css/bootstrap.min.css"
import "../../css/Navbar.css"


export default function Navbar(props)
{

    function renderRightSide(props)
    {
        if(props.displayUser)
            return (
                <ul className="navbar-nav float-right">
                    <li className='nav-item'><a className='nav-link' href='profile'>{props.displayUser}</a></li>
                </ul>
            )

        return (
            <ul className="navbar-nav float-right">
                    <li className='nav-item'><a className='nav-link' href='login'>Login</a></li>
                    <li className='nav-item'><a className='nav-link' href='register'>Register</a></li>
            </ul>
        )
    }


    return (
        <nav className="navbar navbar-expand navbar-dark bg-dark">
            <div className="container-fluid">
                <a className="navbar-brand" href="Home">{props.brand}</a>

                <div className="collapse navbar-collapse" id="navbarResponsive">
                    <ul className="navbar-nav ml-auto">
                        <li className='nav-item'><a className='nav-link' href='Home'>Home</a></li>
                        <li className='nav-item'><a className='nav-link' href='Image'>Image</a></li>
                        <li className='nav-item'><a className='nav-link' href='watch'>Video</a></li>
                        <li className='nav-item'><a className='nav-link' href='upload'>Upload</a></li>
                    </ul>
                </div>

                {renderRightSide(props)}
            </div>
        </nav>
    )
}
