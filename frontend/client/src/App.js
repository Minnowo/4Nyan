import React, { Component } from 'react';
import './App.css';
import Default from './components/Default';
import VideoPage from './components/VideoPage'
import {BrowserRouter as Router,Routes,Route} from "react-router-dom";
 
class App extends Component {
state = {
    apiURL : 'http://localhost:8000',
    teamName: null
  };

  //TODO: Add post method
    // fetching the GET route from the Express server which matches the GET route from server.js
  callBackendAPI = async () => {
    const response = await fetch(this.state.apiURL+'/home');
    const body = await response.json();
    console.log(body)

    if (response.status !== 200) {
      throw Error(body.message) 
    }
    return body;
  };

  postMethod = async () => {
    console.log('Initalized post')

    //Post Parameters
    const reqParam = {
      method : 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({'number' : 1})
    };

    const resp = await fetch(this.state.apiURL+'/post', reqParam);
    const body = resp.json();
    console.log(body);

  };

  render() {
    return (
      <Router>
        <Routes>
      <Route path="/" element={<Default />}></Route>
      <Route path="/Video" element={<VideoPage />}></Route>
      </Routes>
      </Router>
    );
}

}
export default App;