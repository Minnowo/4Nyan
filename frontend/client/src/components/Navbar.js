import React, { Component } from 'react'

import "../css/bootstrap.min.css"
import "../css/Navbar.css"

export default class Navbar extends Component 
{
    state = {
        brand : this.props.brand
    }
  render() 
  {
    return (
        <nav class="navbar navbar-expand navbar-dark bg-dark">
            <div class="container-fluid">
                <a class="navbar-brand" href="">{this.state.brand}</a>

                <div class="collapse navbar-collapse" id="navbarResponsive">
                    <ul class="navbar-nav ml-auto">
                        <li class='nav-item'><a class='nav-link' href=''>Home</a></li>
                        <li class='nav-item'><a class='nav-link' href=''>Image</a></li>
                        <li class='nav-item'><a class='nav-link' href=''>Video</a></li>
                    </ul>
                </div>
                
                <ul class="navbar-nav float-right">
                    <li class='nav-item'><a class='nav-link' href=''>Login</a></li>
                    <li class='nav-item'><a class='nav-link' href=''>Register</a></li>
                </ul>
            </div>
        </nav>
    )
  }
}
