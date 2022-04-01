import React, { Component } from 'react'
import Video from './Video'

import "../css/video.css"

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

    return (
      <div>
        <div>
          <Video {...props}>hello world</Video>
        </div>
      </div>
    )
  }
}
