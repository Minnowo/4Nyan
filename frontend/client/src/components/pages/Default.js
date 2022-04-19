import React, { Component } from 'react'
import Video  from '../elements/Video'
import Navbar from '../elements/Navbar';

import "../../css/video.css"

export default class Default extends Component 
{
  render() 
  {

    let props = {
      //  http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8
      //  http://192.168.1.149:721/static/m3u8/fallen_kingdom.m3u8
      m3u8 : "http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8",
      autoPlay : false
    };

    let nprops = {
      brand : "~4Nyan~"
    };

    return (
      <div>
        <div>
          <Navbar {...nprops}></Navbar>
          <Video {...props}></Video>
        </div>
      </div>
    )
  }
}
