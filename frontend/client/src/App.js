import React, { Component } from 'react';
import {BrowserRouter as Router,Routes,Route} from "react-router-dom";

import Default from './components/pages/Default';

import WatchPage from './components/pages/WatchPage';
import LoginPage from './components/pages/LoginPage';

class App extends Component 
{
  state = {};

  render() 
  {
    return (
      <Router>
        <Routes>
        <Route path="/" element={<Default />}></Route>
        <Route path="/home" element={<Default />}></Route>
        <Route path="/watch" element={<WatchPage />}></Route>
        <Route path="/login" element={<LoginPage />}></Route>
        </Routes>
      </Router>
    );
  }
}
export default App;