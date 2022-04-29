import React, { Component } from 'react';
import {BrowserRouter as Router,Routes,Route} from "react-router-dom";
import Cookies from 'universal-cookie';

import Default from './components/pages/Default';

import WatchPage from './components/pages/WatchPage';
import LoginPage from './components/pages/LoginPage';
import RegisterPage from './components/pages/SignupPage';
import UploadPage from './components/pages/UploadPage';


export default function App()
{
    const [state, setState] = React.useState({ 
      cookies : new Cookies()
    });
    
    return (
      <Router>
        <Routes>
        <Route path="/" element={<Default {...state} />}></Route>
        <Route path="/home" element={<Default {...state}/>}></Route>
        <Route path="/watch" element={<WatchPage {...state}/>}></Route>
        <Route path="/login" element={<LoginPage {...state}/>}></Route>
        <Route path="/register" element={<RegisterPage {...state}/>}></Route>
        <Route path="/upload" element={<UploadPage {...state}/>}></Route>
        </Routes>
      </Router>
    );
}
