import React, { Component } from 'react';
import Default from './components/Default';
import {BrowserRouter as Router,Routes,Route} from "react-router-dom";
 
class App extends Component 
{
  state = {};

  render() 
  {
    return (
      <Router>
        <Routes>
        <Route path="/" element={<Default />}></Route>
        </Routes>
      </Router>
    );
  }
}
export default App;